from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

class UserCreate(BaseModel):
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}

class UserResponse(BaseModel):
    id: int
    user_id: str
    name: Optional[str]
    email: Optional[str]
    preferences: Dict[str, Any]
    personality_profile: Dict[str, Any]
    created_at: datetime
    is_active: bool

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tone_used: Optional[str] = None
    emotion_detected: Optional[Dict[str, float]] = {}
    memory_recalled: Optional[List[str]] = []
    tokens_used: int
    response_time: float

class MemoryItem(BaseModel):
    content: str
    memory_type: str = Field(..., description="Type: preference, fact, emotion, context")
    importance_score: int = Field(default=5, ge=1, le=10)

class ToneAnalysis(BaseModel):
    primary_tone: str
    confidence: float
    emotions: Dict[str, float]
    formality_level: str  # formal, neutral, casual

class PersonalityProfile(BaseModel):
    communication_style: str = "friendly"
    formality_preference: str = "neutral"
    topics_of_interest: List[str] = []
    emotional_sensitivity: float = 0.5
    humor_preference: str = "light"
