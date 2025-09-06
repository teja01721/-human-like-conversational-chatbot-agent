import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.user import UserMemory, User, ChatMessage
from app.services.vector_store import VectorStore
from app.services.ai_client import AIClient
from app.core.database import get_db

class MemoryManager:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.ai_client = AIClient()
    
    async def extract_and_store_memories(
        self,
        user_id: str,
        message: str,
        response: str,
        session: Session
    ) -> List[str]:
        """Extract important information from conversation and store as memories"""
        
        memories_created = []
        
        try:
            # Use AI to extract important information
            extraction_prompt = f"""
            Analyze this conversation and extract important information to remember about the user.
            Focus on: preferences, personal facts, interests, emotional state, goals, relationships.
            
            User message: "{message}"
            Assistant response: "{response}"
            
            Return a JSON list of memories in this format:
            [
                {{
                    "content": "specific fact or preference",
                    "type": "preference|fact|emotion|goal|interest",
                    "importance": 1-10,
                    "reasoning": "why this is important to remember"
                }}
            ]
            
            Only extract genuinely important information. Return empty list if nothing significant.
            """
            
            ai_response = await self.ai_client.generate_response([
                {"role": "system", "content": "You are a memory extraction expert. Extract only important, specific information."},
                {"role": "user", "content": extraction_prompt}
            ], temperature=0.1)
            
            try:
                extracted_memories = json.loads(ai_response["content"])
                
                for memory_data in extracted_memories:
                    if isinstance(memory_data, dict) and "content" in memory_data:
                        memory_id = await self.store_memory(
                            user_id=user_id,
                            content=memory_data["content"],
                            memory_type=memory_data.get("type", "fact"),
                            importance_score=memory_data.get("importance", 5),
                            session=session
                        )
                        memories_created.append(memory_data["content"])
                        
            except json.JSONDecodeError:
                # Fallback: store basic conversation context
                await self.store_memory(
                    user_id=user_id,
                    content=f"User said: {message[:200]}...",
                    memory_type="context",
                    importance_score=3,
                    session=session
                )
                memories_created.append("conversation context")
        
        except Exception as e:
            print(f"Error extracting memories: {e}")
        
        return memories_created
    
    async def store_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str,
        importance_score: int = 5,
        session: Session = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a memory in both database and vector store"""
        
        try:
            # Store in vector store
            memory_id = await self.vector_store.add_memory(
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                importance_score=importance_score,
                metadata=metadata or {}
            )
            
            # Store in database if session provided
            if session:
                db_memory = UserMemory(
                    user_id=user_id,
                    memory_type=memory_type,
                    content=content,
                    importance_score=importance_score
                )
                session.add(db_memory)
                session.commit()
            
            return memory_id
            
        except Exception as e:
            print(f"Error storing memory: {e}")
            raise
    
    async def recall_memories(
        self,
        user_id: str,
        query: str,
        context: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Recall relevant memories for a query"""
        
        try:
            # Enhance query with context
            search_query = query
            if context:
                search_query = f"{context} {query}"
            
            # Search vector store
            memories = await self.vector_store.search_memories(
                user_id=user_id,
                query=search_query,
                n_results=n_results,
                min_importance=3  # Only recall moderately important+ memories
            )
            
            # Filter and rank memories
            relevant_memories = []
            for memory in memories:
                if memory["similarity"] > 0.3:  # Similarity threshold
                    relevant_memories.append({
                        "content": memory["content"],
                        "type": memory["metadata"].get("memory_type", "unknown"),
                        "importance": memory["metadata"].get("importance_score", 1),
                        "similarity": memory["similarity"],
                        "age_days": self._calculate_memory_age(memory["metadata"])
                    })
            
            # Sort by relevance score (combination of similarity, importance, and recency)
            relevant_memories.sort(
                key=lambda m: (
                    m["similarity"] * 0.4 + 
                    (m["importance"] / 10) * 0.4 + 
                    (1 / max(m["age_days"], 1)) * 0.2
                ),
                reverse=True
            )
            
            return relevant_memories[:n_results]
            
        except Exception as e:
            print(f"Error recalling memories: {e}")
            return []
    
    async def get_user_profile(self, user_id: str, session: Session) -> Dict[str, Any]:
        """Get comprehensive user profile from memories"""
        
        try:
            # Get user from database
            user = session.query(User).filter(User.user_id == user_id).first()
            
            # Get memory statistics
            memory_stats = await self.vector_store.get_memory_stats(user_id)
            
            # Get recent important memories
            recent_memories = await self.vector_store.get_user_memories(
                user_id=user_id,
                limit=20
            )
            
            # Analyze personality from memories
            personality_traits = await self._analyze_personality(user_id, recent_memories)
            
            profile = {
                "user_id": user_id,
                "name": user.name if user else None,
                "preferences": user.preferences if user else {},
                "personality_profile": personality_traits,
                "memory_stats": memory_stats,
                "communication_style": self._infer_communication_style(recent_memories),
                "topics_of_interest": self._extract_interests(recent_memories),
                "emotional_patterns": self._analyze_emotional_patterns(recent_memories)
            }
            
            return profile
            
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    async def _analyze_personality(self, user_id: str, memories: List[Dict]) -> Dict[str, Any]:
        """Analyze personality traits from memories"""
        
        if not memories:
            return {"communication_style": "neutral", "traits": []}
        
        try:
            # Combine memory contents for analysis
            memory_text = " ".join([m["content"] for m in memories[:10]])
            
            analysis_prompt = f"""
            Based on these user memories, analyze their personality traits:
            
            {memory_text}
            
            Return JSON with:
            {{
                "communication_style": "formal|casual|friendly|professional",
                "traits": ["trait1", "trait2", ...],
                "formality_preference": "formal|neutral|casual",
                "emotional_sensitivity": 0.0-1.0,
                "humor_appreciation": 0.0-1.0
            }}
            """
            
            response = await self.ai_client.generate_response([
                {"role": "system", "content": "You are a personality analysis expert."},
                {"role": "user", "content": analysis_prompt}
            ], temperature=0.1)
            
            return json.loads(response["content"])
            
        except Exception:
            return {
                "communication_style": "friendly",
                "traits": ["curious", "engaged"],
                "formality_preference": "neutral",
                "emotional_sensitivity": 0.5,
                "humor_appreciation": 0.5
            }
    
    def _calculate_memory_age(self, metadata: Dict[str, Any]) -> int:
        """Calculate age of memory in days"""
        try:
            # This would need to be implemented based on your metadata structure
            return 1  # Default to 1 day
        except:
            return 1
    
    def _infer_communication_style(self, memories: List[Dict]) -> str:
        """Infer preferred communication style from memories"""
        # Simple heuristic - could be enhanced with AI analysis
        formal_indicators = ["please", "thank you", "would you", "could you"]
        casual_indicators = ["hey", "yeah", "cool", "awesome", "lol"]
        
        formal_count = 0
        casual_count = 0
        
        for memory in memories:
            content = memory["content"].lower()
            formal_count += sum(1 for indicator in formal_indicators if indicator in content)
            casual_count += sum(1 for indicator in casual_indicators if indicator in content)
        
        if formal_count > casual_count * 1.5:
            return "formal"
        elif casual_count > formal_count * 1.5:
            return "casual"
        else:
            return "neutral"
    
    def _extract_interests(self, memories: List[Dict]) -> List[str]:
        """Extract topics of interest from memories"""
        interests = []
        
        # Simple keyword extraction - could be enhanced with NLP
        interest_keywords = {
            "technology": ["tech", "programming", "AI", "computer", "software"],
            "sports": ["football", "basketball", "soccer", "tennis", "gym"],
            "music": ["music", "song", "band", "concert", "album"],
            "movies": ["movie", "film", "cinema", "actor", "director"],
            "travel": ["travel", "trip", "vacation", "country", "city"],
            "food": ["food", "restaurant", "cooking", "recipe", "cuisine"]
        }
        
        for memory in memories:
            content = memory["content"].lower()
            for interest, keywords in interest_keywords.items():
                if any(keyword in content for keyword in keywords):
                    if interest not in interests:
                        interests.append(interest)
        
        return interests[:5]  # Return top 5 interests
    
    def _analyze_emotional_patterns(self, memories: List[Dict]) -> Dict[str, float]:
        """Analyze emotional patterns from memories"""
        # Simple sentiment analysis - could be enhanced
        positive_words = ["happy", "excited", "love", "great", "awesome", "wonderful"]
        negative_words = ["sad", "angry", "frustrated", "disappointed", "worried"]
        
        positive_count = 0
        negative_count = 0
        total_words = 0
        
        for memory in memories:
            words = memory["content"].lower().split()
            total_words += len(words)
            positive_count += sum(1 for word in words if word in positive_words)
            negative_count += sum(1 for word in words if word in negative_words)
        
        if total_words == 0:
            return {"positivity": 0.5, "emotional_volatility": 0.3}
        
        return {
            "positivity": max(0.1, min(0.9, 0.5 + (positive_count - negative_count) / total_words * 10)),
            "emotional_volatility": min(0.8, (positive_count + negative_count) / total_words * 20)
        }
    
    async def cleanup_old_memories(self, user_id: str, days_old: int = 30):
        """Clean up old, low-importance memories"""
        try:
            # This would implement memory decay logic
            # For now, just a placeholder
            pass
        except Exception as e:
            print(f"Error cleaning up memories: {e}")
