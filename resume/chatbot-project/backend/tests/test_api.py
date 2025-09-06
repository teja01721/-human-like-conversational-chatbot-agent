import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from app.main import app
from app.core.database import get_db
from app.models.user import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_app_state():
    mock_vector_store = Mock()
    mock_vector_store.add_memory = AsyncMock(return_value="memory_123")
    mock_vector_store.search_memories = AsyncMock(return_value=[])
    mock_vector_store.get_user_memories = AsyncMock(return_value=[])
    mock_vector_store.get_memory_stats = AsyncMock(return_value={
        "total_memories": 0,
        "memory_types": {},
        "avg_importance": 0
    })
    
    mock_memory_manager = Mock()
    mock_memory_manager.get_user_profile = AsyncMock(return_value={
        "user_id": "test_user",
        "personality_profile": {},
        "memory_stats": {}
    })
    
    app.state.vector_store = mock_vector_store
    app.state.memory_manager = mock_memory_manager
    
    return app.state

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_basic_health_check(self, client):
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "Human-Like Chatbot API"
    
    def test_detailed_health_check(self, client, mock_app_state):
        response = client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert "database" in data["services"]

class TestUserEndpoints:
    """Test user management endpoints"""
    
    def test_create_user(self, client):
        user_data = {
            "user_id": "test_user_123",
            "name": "Test User",
            "email": "test@example.com",
            "preferences": {"theme": "dark"}
        }
        
        response = client.post("/api/users/", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user_123"
        assert data["name"] == "Test User"
    
    def test_get_user(self, client):
        # First create a user
        user_data = {
            "user_id": "test_user_456",
            "name": "Another User",
            "email": "another@example.com"
        }
        client.post("/api/users/", json=user_data)
        
        # Then get the user
        response = client.get("/api/users/test_user_456")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user_456"
        assert data["name"] == "Another User"
    
    def test_update_user(self, client):
        # Create user first
        user_data = {
            "user_id": "test_user_789",
            "name": "Original Name"
        }
        client.post("/api/users/", json=user_data)
        
        # Update user
        update_data = {
            "name": "Updated Name",
            "preferences": {"language": "en"}
        }
        response = client.put("/api/users/test_user_789", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
    
    def test_get_nonexistent_user(self, client):
        response = client.get("/api/users/nonexistent_user")
        assert response.status_code == 404

class TestChatEndpoints:
    """Test chat functionality endpoints"""
    
    def test_send_message(self, client, mock_app_state):
        with patch('app.services.conversation_engine.ConversationEngine.process_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = Mock(
                response="Hello! How can I help you today?",
                session_id="session_123",
                tone_used="friendly",
                emotion_detected={"joy": 0.8},
                memory_recalled=["User prefers casual conversation"],
                tokens_used=25,
                response_time=1.2
            )
            
            message_data = {
                "user_id": "test_user",
                "message": "Hello, how are you?",
                "context": {}
            }
            
            response = client.post("/api/chat/message", json=message_data)
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "session_id" in data
    
    def test_get_user_sessions(self, client):
        # This would require setting up test data in the database
        response = client.get("/api/chat/sessions/test_user")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_chat_history(self, client):
        response = client.get("/api/chat/history/test_session")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestMemoryEndpoints:
    """Test memory management endpoints"""
    
    def test_get_user_memories(self, client, mock_app_state):
        response = client.get("/api/users/test_user/memories")
        assert response.status_code == 200
        data = response.json()
        assert "memories" in data
        assert "total_count" in data
    
    def test_add_user_memory(self, client, mock_app_state):
        memory_data = {
            "content": "User loves chocolate ice cream",
            "memory_type": "preference",
            "importance_score": 7
        }
        
        response = client.post("/api/users/test_user/memories", json=memory_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "memory_id" in data
    
    def test_get_user_profile(self, client, mock_app_state):
        response = client.get("/api/users/test_user/profile")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_json(self, client):
        response = client.post(
            "/api/users/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        incomplete_data = {
            "name": "Test User"
            # Missing required user_id
        }
        
        response = client.post("/api/users/", json=incomplete_data)
        assert response.status_code == 422
    
    def test_duplicate_user_creation(self, client):
        user_data = {
            "user_id": "duplicate_user",
            "name": "First User"
        }
        
        # Create user first time
        response1 = client.post("/api/users/", json=user_data)
        assert response1.status_code == 200
        
        # Try to create same user again
        response2 = client.post("/api/users/", json=user_data)
        assert response2.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
