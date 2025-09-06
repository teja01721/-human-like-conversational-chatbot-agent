from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.api import chat, users, health
from app.core.config import settings
from app.core.database import init_db
from app.services.memory_manager import MemoryManager
from app.services.vector_store import VectorStore

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    
    # Initialize services
    vector_store = VectorStore()
    await vector_store.initialize()
    
    memory_manager = MemoryManager(vector_store)
    
    # Store in app state
    app.state.vector_store = vector_store
    app.state.memory_manager = memory_manager
    
    yield
    
    # Shutdown
    await vector_store.close()

app = FastAPI(
    title="Human-Like Chatbot API",
    description="A sophisticated conversational AI with memory and empathy",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
