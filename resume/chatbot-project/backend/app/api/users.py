from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.schemas import UserCreate, UserResponse, MemoryItem
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.user_id == user_data.user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        user = User(
            user_id=user_data.user_id,
            name=user_data.name,
            email=user_data.email,
            preferences=user_data.preferences or {}
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: dict,
    db: Session = Depends(get_db)
):
    """Update user information"""
    
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields
        if "name" in user_data:
            user.name = user_data["name"]
        if "email" in user_data:
            user.email = user_data["email"]
        if "preferences" in user_data:
            user.preferences = user_data["preferences"]
        if "personality_profile" in user_data:
            user.personality_profile = user_data["personality_profile"]
        
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.get("/{user_id}/memories")
async def get_user_memories(
    user_id: str,
    memory_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    app_request: Request = None
):
    """Get user memories"""
    
    try:
        # Get vector store from app state
        vector_store = app_request.app.state.vector_store
        
        memories = await vector_store.get_user_memories(
            user_id=user_id,
            memory_type=memory_type,
            limit=limit
        )
        
        return {
            "memories": memories,
            "total_count": len(memories)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching memories: {str(e)}")

@router.post("/{user_id}/memories")
async def add_user_memory(
    user_id: str,
    memory: MemoryItem,
    db: Session = Depends(get_db),
    app_request: Request = None
):
    """Add a memory for the user"""
    
    try:
        # Get memory manager from app state
        memory_manager = app_request.app.state.memory_manager
        
        memory_id = await memory_manager.store_memory(
            user_id=user_id,
            content=memory.content,
            memory_type=memory.memory_type,
            importance_score=memory.importance_score,
            session=db
        )
        
        return {
            "message": "Memory added successfully",
            "memory_id": memory_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding memory: {str(e)}")

@router.delete("/{user_id}/memories/{memory_id}")
async def delete_user_memory(
    user_id: str,
    memory_id: str,
    db: Session = Depends(get_db),
    app_request: Request = None
):
    """Delete a user memory"""
    
    try:
        # Get vector store from app state
        vector_store = app_request.app.state.vector_store
        
        await vector_store.delete_memory(memory_id)
        
        return {"message": "Memory deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting memory: {str(e)}")

@router.get("/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db),
    app_request: Request = None
):
    """Get comprehensive user profile"""
    
    try:
        # Get memory manager from app state
        memory_manager = app_request.app.state.memory_manager
        
        profile = await memory_manager.get_user_profile(user_id, db)
        
        return profile
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {str(e)}")

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    app_request: Request = None
):
    """Delete user and all associated data"""
    
    try:
        from app.models.user import ChatSession, ChatMessage, UserMemory
        
        # Delete all user data
        db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
        db.query(ChatSession).filter(ChatSession.user_id == user_id).delete()
        db.query(UserMemory).filter(UserMemory.user_id == user_id).delete()
        
        # Delete user
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            db.delete(user)
        
        db.commit()
        
        # Delete from vector store
        vector_store = app_request.app.state.vector_store
        user_memories = await vector_store.get_user_memories(user_id)
        for memory in user_memories:
            await vector_store.delete_memory(memory["id"])
        
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
