from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import time

from app.core.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.conversation_engine import ConversationEngine

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    app_request: Request = None
):
    """Send a message to the chatbot and get a human-like response"""
    
    try:
        # Get conversation engine from app state
        memory_manager = app_request.app.state.memory_manager
        conversation_engine = ConversationEngine(memory_manager)
        
        # Process the message
        response = await conversation_engine.process_message(request, db)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.get("/sessions/{user_id}")
async def get_user_sessions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all chat sessions for a user"""
    
    try:
        from app.models.user import ChatSession
        
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatSession.is_active == True
        ).order_by(ChatSession.updated_at.desc()).all()
        
        return [
            {
                "session_id": session.session_id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at
            }
            for session in sessions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    
    try:
        from app.models.user import ChatMessage
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "id": msg.id,
                "message": msg.message,
                "response": msg.response,
                "timestamp": msg.timestamp,
                "tone_detected": msg.tone_detected,
                "emotion_score": msg.emotion_score
            }
            for msg in reversed(messages)  # Return in chronological order
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat history: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    
    try:
        from app.models.user import ChatSession, ChatMessage
        
        # Delete messages first
        db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
        
        # Delete session
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@router.post("/feedback")
async def submit_feedback(
    feedback_data: dict,
    db: Session = Depends(get_db)
):
    """Submit feedback on chatbot responses"""
    
    try:
        # Store feedback for improving the chatbot
        # This could be used for fine-tuning or improving responses
        
        return {"message": "Feedback received successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@router.get("/analytics/{user_id}")
async def get_user_analytics(
    user_id: str,
    db: Session = Depends(get_db),
    app_request: Request = None
):
    """Get analytics and insights for a user"""
    
    try:
        from app.models.user import ChatMessage
        
        # Get memory manager
        memory_manager = app_request.app.state.memory_manager
        
        # Get user profile
        user_profile = await memory_manager.get_user_profile(user_id, db)
        
        # Get conversation statistics
        total_messages = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).count()
        
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
        
        # Calculate average response time and token usage
        avg_tokens = sum(msg.tokens_used for msg in recent_messages) / len(recent_messages) if recent_messages else 0
        
        return {
            "user_profile": user_profile,
            "conversation_stats": {
                "total_messages": total_messages,
                "average_tokens_per_response": avg_tokens,
                "recent_activity": len(recent_messages)
            },
            "personality_insights": user_profile.get("personality_profile", {}),
            "memory_stats": user_profile.get("memory_stats", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")
