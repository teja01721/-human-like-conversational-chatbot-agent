from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str = ""
    CLAUDE_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Vector Store
    VECTOR_DB_PATH: str = "./vector_store"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # AI Models
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    # Memory Settings
    MAX_MEMORY_ITEMS: int = 100
    MEMORY_DECAY_DAYS: int = 30
    CONTEXT_WINDOW_SIZE: int = 4000
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()
