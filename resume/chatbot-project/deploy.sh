#!/bin/bash

# Automated Live Web Deployment Script for Human-Like Chatbot
# This script deploys both backend and frontend to live hosting platforms

set -e

echo "🚀 Starting Automated Live Web Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking deployment requirements..."
    
    # Check for git
    if ! command -v git &> /dev/null; then
        print_error "Git is required but not installed"
        exit 1
    fi
    
    # Check for npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed"
        exit 1
    fi
    
    # Check for python
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        print_error "Python is required but not installed"
        exit 1
    fi
    
    print_success "All requirements satisfied"
}

# Setup environment files
setup_environment() {
    print_status "Setting up environment configuration..."
    
    # Backend environment
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
        print_warning "Please edit backend/.env with your API keys before deployment"
        print_warning "Required: OPENAI_API_KEY or CLAUDE_API_KEY"
    fi
    
    # Frontend environment
    if [ ! -f "frontend/.env" ]; then
        cp frontend/.env.example frontend/.env
        print_success "Frontend environment file created"
    fi
}

# Deploy backend to Railway
deploy_backend_railway() {
    print_status "Deploying backend to Railway..."
    
    # Check if railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_status "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    cd backend
    
    # Initialize railway project if not exists
    if [ ! -f "railway.toml" ]; then
        railway login
        railway init
    fi
    
    # Deploy
    railway up
    
    # Get the deployment URL
    BACKEND_URL=$(railway status --json | jq -r '.deployments[0].url')
    print_success "Backend deployed to: $BACKEND_URL"
    
    cd ..
    echo "BACKEND_URL=$BACKEND_URL" > .deployment_urls
}

# Deploy backend to Heroku (alternative)
deploy_backend_heroku() {
    print_status "Deploying backend to Heroku..."
    
    # Check if heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI not found. Please install it first."
        return 1
    fi
    
    cd backend
    
    # Create Heroku app
    APP_NAME="chatbot-api-$(date +%s)"
    heroku create $APP_NAME
    
    # Add PostgreSQL addon
    heroku addons:create heroku-postgresql:mini -a $APP_NAME
    
    # Set environment variables from .env file
    if [ -f ".env" ]; then
        while IFS= read -r line; do
            if [[ $line == *"="* ]] && [[ $line != "#"* ]]; then
                heroku config:set "$line" -a $APP_NAME
            fi
        done < .env
    fi
    
    # Deploy
    git init
    git add .
    git commit -m "Initial deployment"
    heroku git:remote -a $APP_NAME
    git push heroku main
    
    BACKEND_URL="https://$APP_NAME.herokuapp.com"
    print_success "Backend deployed to: $BACKEND_URL"
    
    cd ..
    echo "BACKEND_URL=$BACKEND_URL" > .deployment_urls
}

# Deploy frontend to Netlify
deploy_frontend_netlify() {
    print_status "Deploying frontend to Netlify..."
    
    # Get backend URL
    if [ -f ".deployment_urls" ]; then
        source .deployment_urls
    else
        print_error "Backend URL not found. Deploy backend first."
        return 1
    fi
    
    cd frontend
    
    # Update environment with backend URL
    echo "VITE_API_URL=$BACKEND_URL" > .env
    
    # Install netlify CLI if not exists
    if ! command -v netlify &> /dev/null; then
        npm install -g netlify-cli
    fi
    
    # Build the project
    npm install
    npm run build
    
    # Deploy to Netlify
    netlify login
    netlify init
    netlify deploy --prod --dir=dist
    
    # Get the deployment URL
    FRONTEND_URL=$(netlify status --json | jq -r '.site_url')
    print_success "Frontend deployed to: $FRONTEND_URL"
    
    cd ..
    echo "FRONTEND_URL=$FRONTEND_URL" >> .deployment_urls
}

# Deploy frontend to Vercel (alternative)
deploy_frontend_vercel() {
    print_status "Deploying frontend to Vercel..."
    
    # Get backend URL
    if [ -f ".deployment_urls" ]; then
        source .deployment_urls
    else
        print_error "Backend URL not found. Deploy backend first."
        return 1
    fi
    
    cd frontend
    
    # Update environment with backend URL
    echo "VITE_API_URL=$BACKEND_URL" > .env
    
    # Install vercel CLI if not exists
    if ! command -v vercel &> /dev/null; then
        npm install -g vercel
    fi
    
    # Build and deploy
    npm install
    vercel --prod
    
    print_success "Frontend deployed to Vercel"
    cd ..
}

# Test deployment
test_deployment() {
    print_status "Testing live deployment..."
    
    if [ -f ".deployment_urls" ]; then
        source .deployment_urls
        
        # Test backend health
        if curl -f "$BACKEND_URL/health/" > /dev/null 2>&1; then
            print_success "Backend health check passed"
        else
            print_error "Backend health check failed"
        fi
        
        # Test frontend
        if curl -f "$FRONTEND_URL" > /dev/null 2>&1; then
            print_success "Frontend accessibility check passed"
        else
            print_error "Frontend accessibility check failed"
        fi
        
        print_success "🎉 Deployment completed successfully!"
        echo ""
        echo "🌐 Your chatbot is now live at:"
        echo "   Frontend: $FRONTEND_URL"
        echo "   Backend API: $BACKEND_URL"
        echo "   API Docs: $BACKEND_URL/docs"
        
    else
        print_error "Deployment URLs not found"
    fi
}

# Main deployment function
main() {
    echo "🤖 Human-Like Chatbot - Automated Live Deployment"
    echo "=================================================="
    
    check_requirements
    setup_environment
    
    # Choose deployment platform
    echo ""
    echo "Choose deployment platform:"
    echo "1) Railway (Backend) + Netlify (Frontend) [Recommended]"
    echo "2) Heroku (Backend) + Vercel (Frontend)"
    echo "3) Railway (Backend) + Vercel (Frontend)"
    echo "4) Heroku (Backend) + Netlify (Frontend)"
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            deploy_backend_railway
            deploy_frontend_netlify
            ;;
        2)
            deploy_backend_heroku
            deploy_frontend_vercel
            ;;
        3)
            deploy_backend_railway
            deploy_frontend_vercel
            ;;
        4)
            deploy_backend_heroku
            deploy_frontend_netlify
            ;;
        *)
            print_error "Invalid choice. Using default (Railway + Netlify)"
            deploy_backend_railway
            deploy_frontend_netlify
            ;;
    esac
    
    test_deployment
}

# Run main function
main "$@"
