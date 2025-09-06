from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db, get_redis
import time

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "Human-Like Chatbot API"
    }

@router.get("/detailed")
async def detailed_health_check(
    db: Session = Depends(get_db),
    app_request: Request = None
):
    """Detailed health check with service dependencies"""
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {}
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        redis_client = get_redis()
        if redis_client:
            redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "not configured"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check vector store
    try:
        if hasattr(app_request.app.state, 'vector_store'):
            vector_store = app_request.app.state.vector_store
            if vector_store.collection:
                health_status["services"]["vector_store"] = "healthy"
            else:
                health_status["services"]["vector_store"] = "not initialized"
        else:
            health_status["services"]["vector_store"] = "not available"
    except Exception as e:
        health_status["services"]["vector_store"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
