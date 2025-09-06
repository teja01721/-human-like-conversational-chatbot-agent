@echo off
REM Automated Live Web Deployment Script for Windows
REM This script deploys both backend and frontend to live hosting platforms

echo 🚀 Starting Automated Live Web Deployment...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is required but not installed
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

echo ✅ Requirements check passed

REM Setup environment files
if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env"
    echo ⚠️  Please edit backend\.env with your API keys
    echo Required: OPENAI_API_KEY or CLAUDE_API_KEY
    notepad "backend\.env"
)

if not exist "frontend\.env" (
    copy "frontend\.env.example" "frontend\.env"
)

echo 📝 Environment files configured

REM Install global deployment tools
echo 🔧 Installing deployment tools...
npm install -g @railway/cli netlify-cli vercel

REM Deploy Backend to Railway
echo 🚂 Deploying backend to Railway...
cd backend

REM Login to Railway (will open browser)
railway login

REM Initialize and deploy
railway init --name chatbot-backend
railway up

REM Get deployment URL
for /f "tokens=*" %%i in ('railway status --json') do set RAILWAY_OUTPUT=%%i
echo Backend deployed successfully!

cd ..

REM Deploy Frontend to Netlify
echo 🌐 Deploying frontend to Netlify...
cd frontend

REM Install dependencies
npm install

REM Build the project
npm run build

REM Login to Netlify (will open browser)
netlify login

REM Deploy
netlify init
netlify deploy --prod --dir=dist

echo ✅ Frontend deployed successfully!

cd ..

echo 🎉 Deployment completed!
echo Your chatbot is now live on the web!
echo Check the deployment URLs in your Railway and Netlify dashboards.

pause
