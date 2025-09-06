from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
import asyncio
from app.core.config import settings

# SQLAlchemy setup
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = None

async def init_db():
    """Initialize database and Redis connections"""
    global redis_client
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await asyncio.to_thread(redis_client.ping)
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
        redis_client = None

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Get Redis client"""
    return redis_client
