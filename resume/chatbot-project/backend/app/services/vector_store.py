import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import asyncio
import os
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.model_name = settings.EMBEDDING_MODEL
    
    async def initialize(self):
        """Initialize ChromaDB and embedding model"""
        try:
            # Initialize ChromaDB
            os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
            self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="user_memories",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(self.model_name)
            
            print(f"✅ Vector store initialized with {self.collection.count()} memories")
            
        except Exception as e:
            print(f"❌ Vector store initialization failed: {e}")
            raise
    
    async def add_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str,
        importance_score: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a memory to the vector store"""
        try:
            # Generate embedding
            embedding = await asyncio.to_thread(
                self.embedding_model.encode, content
            )
            
            # Create unique ID
            memory_id = f"{user_id}_{memory_type}_{hash(content) % 1000000}"
            
            # Prepare metadata
            memory_metadata = {
                "user_id": user_id,
                "memory_type": memory_type,
                "importance_score": importance_score,
                "content_length": len(content),
                **(metadata or {})
            }
            
            # Add to collection
            self.collection.add(
                embeddings=[embedding.tolist()],
                documents=[content],
                metadatas=[memory_metadata],
                ids=[memory_id]
            )
            
            return memory_id
            
        except Exception as e:
            print(f"Error adding memory: {e}")
            raise
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        n_results: int = 5,
        memory_types: Optional[List[str]] = None,
        min_importance: int = 1
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories"""
        try:
            # Generate query embedding
            query_embedding = await asyncio.to_thread(
                self.embedding_model.encode, query
            )
            
            # Build where clause
            where_clause = {"user_id": user_id}
            if memory_types:
                where_clause["memory_type"] = {"$in": memory_types}
            if min_importance > 1:
                where_clause["importance_score"] = {"$gte": min_importance}
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            memories = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    memories.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i],
                        "similarity": 1 - results["distances"][0][i],  # Convert distance to similarity
                        "id": results["ids"][0][i] if "ids" in results else None
                    })
            
            return memories
            
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    async def get_user_memories(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all memories for a user"""
        try:
            where_clause = {"user_id": user_id}
            if memory_type:
                where_clause["memory_type"] = memory_type
            
            results = self.collection.get(
                where=where_clause,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            memories = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    memories.append({
                        "content": doc,
                        "metadata": results["metadatas"][i],
                        "id": results["ids"][i]
                    })
            
            return memories
            
        except Exception as e:
            print(f"Error getting user memories: {e}")
            return []
    
    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update an existing memory"""
        try:
            if content:
                # Generate new embedding
                embedding = await asyncio.to_thread(
                    self.embedding_model.encode, content
                )
                
                self.collection.update(
                    ids=[memory_id],
                    embeddings=[embedding.tolist()],
                    documents=[content],
                    metadatas=[metadata] if metadata else None
                )
            elif metadata:
                self.collection.update(
                    ids=[memory_id],
                    metadatas=[metadata]
                )
                
        except Exception as e:
            print(f"Error updating memory: {e}")
            raise
    
    async def delete_memory(self, memory_id: str):
        """Delete a memory"""
        try:
            self.collection.delete(ids=[memory_id])
        except Exception as e:
            print(f"Error deleting memory: {e}")
            raise
    
    async def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for a user"""
        try:
            memories = await self.get_user_memories(user_id)
            
            stats = {
                "total_memories": len(memories),
                "memory_types": {},
                "importance_distribution": {},
                "avg_importance": 0
            }
            
            if memories:
                importance_scores = []
                for memory in memories:
                    memory_type = memory["metadata"].get("memory_type", "unknown")
                    importance = memory["metadata"].get("importance_score", 1)
                    
                    stats["memory_types"][memory_type] = stats["memory_types"].get(memory_type, 0) + 1
                    stats["importance_distribution"][str(importance)] = stats["importance_distribution"].get(str(importance), 0) + 1
                    importance_scores.append(importance)
                
                stats["avg_importance"] = sum(importance_scores) / len(importance_scores)
            
            return stats
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {"total_memories": 0, "memory_types": {}, "importance_distribution": {}, "avg_importance": 0}
    
    async def close(self):
        """Clean up resources"""
        try:
            if self.client:
                # ChromaDB doesn't need explicit closing
                pass
        except Exception as e:
            print(f"Error closing vector store: {e}")
