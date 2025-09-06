import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import shutil
from app.services.vector_store import VectorStore
from app.services.memory_manager import MemoryManager
from app.services.ai_client import AIClient

@pytest.fixture
async def vector_store():
    # Create temporary directory for test vector store
    temp_dir = tempfile.mkdtemp()
    
    with patch('app.core.config.settings') as mock_settings:
        mock_settings.VECTOR_DB_PATH = temp_dir
        mock_settings.EMBEDDING_MODEL = "all-MiniLM-L6-v2"
        
        store = VectorStore()
        await store.initialize()
        
        yield store
        
        await store.close()
        shutil.rmtree(temp_dir)

@pytest.fixture
def memory_manager(vector_store):
    return MemoryManager(vector_store)

class TestVectorStore:
    """Test vector store functionality"""
    
    @pytest.mark.asyncio
    async def test_add_and_search_memory(self, vector_store):
        # Add a memory
        memory_id = await vector_store.add_memory(
            user_id="test_user",
            content="I love pizza with pepperoni",
            memory_type="preference",
            importance_score=8
        )
        
        assert memory_id is not None
        
        # Search for related memory
        results = await vector_store.search_memories(
            user_id="test_user",
            query="favorite food pizza",
            n_results=5
        )
        
        assert len(results) > 0
        assert "pizza" in results[0]["content"].lower()
        assert results[0]["similarity"] > 0.3
    
    @pytest.mark.asyncio
    async def test_memory_filtering_by_type(self, vector_store):
        # Add different types of memories
        await vector_store.add_memory(
            user_id="test_user",
            content="I work as a software engineer",
            memory_type="fact",
            importance_score=7
        )
        
        await vector_store.add_memory(
            user_id="test_user",
            content="I prefer casual communication",
            memory_type="preference",
            importance_score=6
        )
        
        # Search for preferences only
        results = await vector_store.search_memories(
            user_id="test_user",
            query="communication style",
            memory_types=["preference"]
        )
        
        assert len(results) > 0
        assert all(r["metadata"]["memory_type"] == "preference" for r in results)
    
    @pytest.mark.asyncio
    async def test_memory_importance_filtering(self, vector_store):
        # Add memories with different importance scores
        await vector_store.add_memory(
            user_id="test_user",
            content="Low importance memory",
            memory_type="fact",
            importance_score=2
        )
        
        await vector_store.add_memory(
            user_id="test_user",
            content="High importance memory",
            memory_type="fact",
            importance_score=9
        )
        
        # Search with minimum importance filter
        results = await vector_store.search_memories(
            user_id="test_user",
            query="memory",
            min_importance=5
        )
        
        assert len(results) > 0
        assert all(r["metadata"]["importance_score"] >= 5 for r in results)

class TestMemoryManager:
    """Test memory manager functionality"""
    
    @pytest.mark.asyncio
    async def test_memory_extraction(self, memory_manager):
        with patch.object(memory_manager.ai_client, 'generate_response', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = {
                "content": '''[
                    {
                        "content": "User likes Italian food",
                        "type": "preference",
                        "importance": 7,
                        "reasoning": "User specifically mentioned loving Italian cuisine"
                    }
                ]''',
                "tokens_used": 50
            }
            
            memories = await memory_manager.extract_and_store_memories(
                user_id="test_user",
                message="I absolutely love Italian food, especially pasta",
                response="That's great! Italian cuisine has so many delicious options.",
                session=None
            )
            
            assert len(memories) > 0
            assert "Italian food" in memories[0]
    
    @pytest.mark.asyncio
    async def test_memory_recall(self, memory_manager):
        # Mock vector store search
        with patch.object(memory_manager.vector_store, 'search_memories', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {
                    "content": "User is a vegetarian",
                    "metadata": {"memory_type": "preference", "importance_score": 8},
                    "similarity": 0.9
                }
            ]
            
            memories = await memory_manager.recall_memories(
                user_id="test_user",
                query="food recommendations",
                n_results=5
            )
            
            assert len(memories) > 0
            assert memories[0]["content"] == "User is a vegetarian"
            assert memories[0]["similarity"] > 0.8

class TestMemoryPersistence:
    """Test memory persistence across sessions"""
    
    @pytest.mark.asyncio
    async def test_memory_survives_restart(self, vector_store):
        # Add memory
        memory_id = await vector_store.add_memory(
            user_id="persistent_user",
            content="I have a cat named Whiskers",
            memory_type="fact",
            importance_score=6
        )
        
        # Simulate restart by creating new vector store instance
        temp_dir = vector_store.client._settings.persist_directory
        
        new_store = VectorStore()
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.VECTOR_DB_PATH = temp_dir
            mock_settings.EMBEDDING_MODEL = "all-MiniLM-L6-v2"
            
            await new_store.initialize()
            
            # Search for the memory
            results = await new_store.search_memories(
                user_id="persistent_user",
                query="pet cat",
                n_results=5
            )
            
            assert len(results) > 0
            assert "Whiskers" in results[0]["content"]
            
            await new_store.close()

class TestMemoryStats:
    """Test memory statistics functionality"""
    
    @pytest.mark.asyncio
    async def test_memory_statistics(self, vector_store):
        # Add various memories
        memories_data = [
            ("I like coffee", "preference", 7),
            ("I work in tech", "fact", 8),
            ("I feel excited about AI", "emotion", 6),
            ("I want to learn Spanish", "goal", 9),
            ("I enjoy reading sci-fi", "interest", 5)
        ]
        
        for content, mem_type, importance in memories_data:
            await vector_store.add_memory(
                user_id="stats_user",
                content=content,
                memory_type=mem_type,
                importance_score=importance
            )
        
        # Get statistics
        stats = await vector_store.get_memory_stats("stats_user")
        
        assert stats["total_memories"] == 5
        assert "preference" in stats["memory_types"]
        assert "fact" in stats["memory_types"]
        assert stats["avg_importance"] > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
