#!/usr/bin/env python3
"""
Setup script for Human-Like Chatbot
Automates the initial setup process
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    requirements = {
        "python": "python --version",
        "node": "node --version",
        "npm": "npm --version",
        "git": "git --version"
    }
    
    missing = []
    for tool, command in requirements.items():
        result = run_command(command, check=False)
        if result and result.returncode == 0:
            print(f"✅ {tool}: {result.stdout.strip()}")
        else:
            print(f"❌ {tool}: Not found")
            missing.append(tool)
    
    if missing:
        print(f"\n⚠️  Missing requirements: {', '.join(missing)}")
        print("Please install the missing tools and run setup again.")
        return False
    
    return True

def setup_backend():
    """Setup backend environment"""
    print("\n🐍 Setting up backend...")
    
    backend_dir = Path("backend")
    
    # Create virtual environment
    if not (backend_dir / "venv").exists():
        print("Creating virtual environment...")
        run_command("python -m venv venv", cwd=backend_dir)
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = backend_dir / "venv" / "Scripts" / "activate"
        pip_path = backend_dir / "venv" / "Scripts" / "pip"
    else:  # Unix/Linux/Mac
        activate_script = backend_dir / "venv" / "bin" / "activate"
        pip_path = backend_dir / "venv" / "bin" / "pip"
    
    # Install dependencies
    print("Installing Python dependencies...")
    run_command(f"{pip_path} install -r requirements.txt", cwd=backend_dir)
    
    # Copy environment file
    env_example = backend_dir / ".env.example"
    env_file = backend_dir / ".env"
    
    if env_example.exists() and not env_file.exists():
        print("Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print("⚠️  Please edit backend/.env with your API keys!")
    
    print("✅ Backend setup complete!")

def setup_frontend():
    """Setup frontend environment"""
    print("\n⚛️  Setting up frontend...")
    
    frontend_dir = Path("frontend")
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    run_command("npm install", cwd=frontend_dir)
    
    # Copy environment file
    env_example = frontend_dir / ".env.example"
    env_file = frontend_dir / ".env"
    
    if env_example.exists() and not env_file.exists():
        print("Creating .env file from template...")
        shutil.copy(env_example, env_file)
    
    print("✅ Frontend setup complete!")

def setup_database():
    """Setup database"""
    print("\n🗄️  Setting up database...")
    
    backend_dir = Path("backend")
    
    # Create necessary directories
    directories = ["vector_store", "logs"]
    for directory in directories:
        dir_path = backend_dir / directory
        dir_path.mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    print("✅ Database setup complete!")

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n📝 Creating startup scripts...")
    
    # Windows batch file
    with open("start_backend.bat", "w") as f:
        f.write("""@echo off
cd backend
call venv\\Scripts\\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
""")
    
    with open("start_frontend.bat", "w") as f:
        f.write("""@echo off
cd frontend
npm run dev
pause
""")
    
    # Unix shell scripts
    with open("start_backend.sh", "w") as f:
        f.write("""#!/bin/bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
""")
    
    with open("start_frontend.sh", "w") as f:
        f.write("""#!/bin/bash
cd frontend
npm run dev
""")
    
    # Make shell scripts executable on Unix systems
    if os.name != 'nt':
        os.chmod("start_backend.sh", 0o755)
        os.chmod("start_frontend.sh", 0o755)
    
    print("✅ Startup scripts created!")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("\n1. Configure API Keys:")
    print("   - Edit backend/.env")
    print("   - Add your OpenAI API key: OPENAI_API_KEY=your_key_here")
    print("   - Add your Claude API key: CLAUDE_API_KEY=your_key_here")
    
    print("\n2. Start the services:")
    if os.name == 'nt':  # Windows
        print("   - Backend: double-click start_backend.bat")
        print("   - Frontend: double-click start_frontend.bat")
    else:  # Unix/Linux/Mac
        print("   - Backend: ./start_backend.sh")
        print("   - Frontend: ./start_frontend.sh")
    
    print("\n3. Alternative manual start:")
    print("   Backend:")
    print("   cd backend")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("   uvicorn app.main:app --reload")
    
    print("\n   Frontend:")
    print("   cd frontend")
    print("   npm run dev")
    
    print("\n4. Access the application:")
    print("   - Frontend: http://localhost:3000")
    print("   - Backend API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    
    print("\n5. Run tests:")
    print("   cd backend")
    print("   python -m pytest tests/ -v")
    print("   python ../scripts/test_examples.py")
    
    print("\n6. Docker deployment (optional):")
    print("   docker-compose up -d")
    
    print("\n📚 Documentation:")
    print("   - README.md: Project overview")
    print("   - backend/app/: Backend source code")
    print("   - frontend/src/: Frontend source code")
    
    print("\n⚠️  IMPORTANT:")
    print("   - Make sure to add your API keys to backend/.env")
    print("   - The chatbot needs either OpenAI or Claude API access")
    print("   - Check the health endpoint: http://localhost:8000/health/")

def main():
    """Main setup function"""
    print("🚀 Human-Like Chatbot Setup")
    print("="*40)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   The directory should contain 'backend' and 'frontend' folders")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    try:
        # Setup components
        setup_backend()
        setup_frontend()
        setup_database()
        create_startup_scripts()
        
        # Print next steps
        print_next_steps()
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
