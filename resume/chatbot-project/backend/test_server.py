#!/usr/bin/env python3
"""
Simple test server to debug Python/FastAPI issues
"""

try:
    print("🔍 Testing Python imports...")
    
    # Test basic Python
    print("✅ Python is working")
    
    # Test FastAPI import
    try:
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        print("Installing FastAPI...")
        import subprocess
        subprocess.run(["pip", "install", "fastapi", "uvicorn"])
        from fastapi import FastAPI
        print("✅ FastAPI installed and imported")
    
    # Create simple app
    app = FastAPI(title="Debug Server")
    
    @app.get("/")
    def read_root():
        return {"message": "Server is working!", "status": "success"}
    
    @app.get("/health")
    def health():
        return {"status": "healthy", "debug": True}
    
    print("✅ FastAPI app created successfully")
    
    # Test uvicorn import
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError:
        print("❌ Uvicorn not found, installing...")
        import subprocess
        subprocess.run(["pip", "install", "uvicorn"])
        import uvicorn
        print("✅ Uvicorn installed and imported")
    
    # Start server
    print("🚀 Starting debug server on http://localhost:8000")
    print("📡 Health check: http://localhost:8000/health")
    
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
except Exception as e:
    print(f"❌ Error occurred: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
