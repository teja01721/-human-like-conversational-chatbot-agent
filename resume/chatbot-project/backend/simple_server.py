from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Simple FastAPI app for testing
app = FastAPI(
    title="Human-Like Chatbot API",
    description="A sophisticated conversational AI with memory and empathy",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Human-Like Chatbot API is running!", "status": "healthy"}

@app.get("/health/")
async def health_check():
    return {
        "status": "healthy",
        "message": "Chatbot API is operational",
        "version": "1.0.0"
    }

@app.post("/api/chat/")
async def chat_endpoint(message: dict):
    user_message = message.get("message", "")
    return {
        "response": f"Hello! You said: '{user_message}'. I'm a human-like chatbot ready to help!",
        "user_id": "demo-user",
        "timestamp": "2025-01-06T02:54:00Z"
    }

@app.get("/docs")
async def get_docs():
    return {"message": "API Documentation available at /docs"}

if __name__ == "__main__":
    print("🚀 Starting Human-Like Chatbot API...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation at: http://localhost:8000/docs")
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
