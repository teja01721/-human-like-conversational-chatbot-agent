import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.services.ai_client import AIClient
from app.services.memory_manager import MemoryManager
from app.services.tone_analyzer import ToneAnalyzer
from app.models.user import User, ChatSession, ChatMessage
from app.models.schemas import ChatRequest, ChatResponse
from app.core.personality import PersonalityEngine

class ConversationEngine:
    def __init__(self, memory_manager: MemoryManager):
        self.ai_client = AIClient()
        self.memory_manager = memory_manager
        self.tone_analyzer = ToneAnalyzer()
        self.personality_engine = PersonalityEngine()
    
    async def process_message(
        self,
        request: ChatRequest,
        session: Session
    ) -> ChatResponse:
        """Process a user message and generate a human-like response"""
        
        start_time = time.time()
        
        try:
            # Get or create user
            user = await self._get_or_create_user(request.user_id, session)
            
            # Get or create chat session
            chat_session = await self._get_or_create_session(
                request.session_id, request.user_id, session
            )
            
            # Analyze user's tone and emotion
            tone_analysis = await self.tone_analyzer.analyze_tone(request.message)
            
            # Recall relevant memories
            memories = await self.memory_manager.recall_memories(
                user_id=request.user_id,
                query=request.message,
                context=request.context.get("recent_context", "")
            )
            
            # Get user profile for personalization
            user_profile = await self.memory_manager.get_user_profile(request.user_id, session)
            
            # Build conversation context
            conversation_context = await self._build_conversation_context(
                chat_session.session_id, session, limit=10
            )
            
            # Generate personality-aware system prompt
            system_prompt = self.personality_engine.generate_system_prompt(
                user_profile=user_profile,
                tone_analysis=tone_analysis,
                memories=memories
            )
            
            # Prepare messages for AI
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            messages.extend(conversation_context)
            
            # Add memory context if relevant
            if memories:
                memory_context = self._format_memory_context(memories)
                messages.append({
                    "role": "system", 
                    "content": f"Relevant memories about the user: {memory_context}"
                })
            
            # Add current message
            messages.append({"role": "user", "content": request.message})
            
            # Generate AI response
            ai_response = await self.ai_client.generate_response(
                messages=messages,
                temperature=self._calculate_temperature(tone_analysis, user_profile)
            )
            
            # Post-process response for human-likeness
            processed_response = await self._post_process_response(
                ai_response["content"],
                tone_analysis,
                user_profile,
                memories
            )
            
            # Store conversation in database
            chat_message = ChatMessage(
                session_id=chat_session.session_id,
                user_id=request.user_id,
                message=request.message,
                response=processed_response,
                tone_detected=tone_analysis.get("primary_tone"),
                emotion_score=tone_analysis.get("emotions", {}),
                tokens_used=ai_response.get("tokens_used", 0)
            )
            session.add(chat_message)
            session.commit()
            
            # Extract and store new memories
            memories_created = await self.memory_manager.extract_and_store_memories(
                user_id=request.user_id,
                message=request.message,
                response=processed_response,
                session=session
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            return ChatResponse(
                response=processed_response,
                session_id=chat_session.session_id,
                tone_used=self._determine_response_tone(tone_analysis, user_profile),
                emotion_detected=tone_analysis.get("emotions", {}),
                memory_recalled=[m["content"][:50] + "..." for m in memories[:3]],
                tokens_used=ai_response.get("tokens_used", 0),
                response_time=response_time
            )
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return ChatResponse(
                response="I apologize, but I'm having trouble processing your message right now. Could you please try again?",
                session_id=request.session_id or str(uuid.uuid4()),
                tone_used="apologetic",
                emotion_detected={},
                memory_recalled=[],
                tokens_used=0,
                response_time=time.time() - start_time
            )
    
    async def _get_or_create_user(self, user_id: str, session: Session) -> User:
        """Get existing user or create new one"""
        user = session.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            user = User(
                user_id=user_id,
                preferences={},
                personality_profile={}
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        
        return user
    
    async def _get_or_create_session(
        self, 
        session_id: Optional[str], 
        user_id: str, 
        session: Session
    ) -> ChatSession:
        """Get existing chat session or create new one"""
        
        if session_id:
            chat_session = session.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            if chat_session:
                return chat_session
        
        # Create new session
        new_session_id = session_id or str(uuid.uuid4())
        chat_session = ChatSession(
            session_id=new_session_id,
            user_id=user_id,
            title="New Conversation"
        )
        session.add(chat_session)
        session.commit()
        session.refresh(chat_session)
        
        return chat_session
    
    async def _build_conversation_context(
        self, 
        session_id: str, 
        session: Session, 
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Build conversation context from recent messages"""
        
        messages = session.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
        
        context = []
        for msg in reversed(messages):  # Reverse to get chronological order
            context.append({"role": "user", "content": msg.message})
            if msg.response:
                context.append({"role": "assistant", "content": msg.response})
        
        return context
    
    def _format_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """Format memories into context string"""
        if not memories:
            return ""
        
        context_parts = []
        for memory in memories[:5]:  # Limit to top 5 memories
            importance = memory.get("importance", 1)
            memory_type = memory.get("type", "fact")
            content = memory["content"]
            
            context_parts.append(f"[{memory_type.upper()}] {content}")
        
        return " | ".join(context_parts)
    
    def _calculate_temperature(
        self, 
        tone_analysis: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> float:
        """Calculate AI temperature based on context"""
        base_temp = 0.7
        
        # Adjust based on user's emotional state
        emotions = tone_analysis.get("emotions", {})
        if emotions.get("sadness", 0) > 0.6:
            base_temp = 0.5  # More consistent for sad users
        elif emotions.get("joy", 0) > 0.6:
            base_temp = 0.8  # More creative for happy users
        
        # Adjust based on user personality
        personality = user_profile.get("personality_profile", {})
        if personality.get("communication_style") == "formal":
            base_temp -= 0.1
        elif personality.get("communication_style") == "casual":
            base_temp += 0.1
        
        return max(0.1, min(1.0, base_temp))
    
    async def _post_process_response(
        self,
        response: str,
        tone_analysis: Dict[str, Any],
        user_profile: Dict[str, Any],
        memories: List[Dict[str, Any]]
    ) -> str:
        """Post-process AI response for human-likeness"""
        
        # Add personality touches
        processed = self.personality_engine.add_personality_touches(
            response, user_profile, tone_analysis
        )
        
        # Add memory callbacks if appropriate
        if memories and len(processed) < 200:  # Only for shorter responses
            processed = self._add_memory_callbacks(processed, memories)
        
        # Ensure response variety
        processed = self._ensure_response_variety(processed, tone_analysis)
        
        return processed
    
    def _add_memory_callbacks(
        self, 
        response: str, 
        memories: List[Dict[str, Any]]
    ) -> str:
        """Add subtle memory callbacks to response"""
        
        # Find highly relevant memories
        relevant_memories = [m for m in memories if m.get("similarity", 0) > 0.7]
        
        if not relevant_memories:
            return response
        
        # Add a subtle callback
        memory = relevant_memories[0]
        memory_type = memory.get("type", "")
        
        callbacks = {
            "preference": [
                "I remember you mentioned liking",
                "Since you prefer",
                "Given your interest in"
            ],
            "fact": [
                "I recall you telling me about",
                "You mentioned earlier that",
                "I remember you said"
            ],
            "emotion": [
                "I know this is important to you",
                "Given how you feel about this",
                "I understand this matters to you"
            ]
        }
        
        if memory_type in callbacks and len(response) < 150:
            # Only add callback to shorter responses
            import random
            callback_phrase = random.choice(callbacks[memory_type])
            # This would need more sophisticated integration
            # For now, just return the original response
        
        return response
    
    def _ensure_response_variety(
        self, 
        response: str, 
        tone_analysis: Dict[str, Any]
    ) -> str:
        """Ensure response has variety and doesn't sound robotic"""
        
        # Add natural conversation starters based on tone
        primary_tone = tone_analysis.get("primary_tone", "neutral")
        
        variety_starters = {
            "happy": ["That's wonderful!", "I'm so glad to hear that!", "How exciting!"],
            "sad": ["I'm sorry to hear that.", "That sounds difficult.", "I understand how you feel."],
            "excited": ["That's amazing!", "Wow, that's fantastic!", "I can feel your excitement!"],
            "confused": ["Let me help clarify that.", "I can see why that might be confusing.", "Let's work through this together."],
            "neutral": ["I see.", "That's interesting.", "Tell me more about that."]
        }
        
        # Only add starters to responses that don't already have emotional language
        if (len(response) > 20 and 
            not any(starter.lower() in response.lower() for starters in variety_starters.values() for starter in starters)):
            
            if primary_tone in variety_starters:
                import random
                starter = random.choice(variety_starters[primary_tone])
                response = f"{starter} {response}"
        
        return response
    
    def _determine_response_tone(
        self, 
        tone_analysis: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> str:
        """Determine appropriate response tone"""
        
        user_tone = tone_analysis.get("primary_tone", "neutral")
        user_emotions = tone_analysis.get("emotions", {})
        
        # Mirror user's emotional state appropriately
        if user_emotions.get("sadness", 0) > 0.6:
            return "empathetic"
        elif user_emotions.get("joy", 0) > 0.6:
            return "enthusiastic"
        elif user_emotions.get("anger", 0) > 0.5:
            return "calming"
        elif user_tone == "formal":
            return "professional"
        elif user_tone == "casual":
            return "friendly"
        else:
            return "warm"
