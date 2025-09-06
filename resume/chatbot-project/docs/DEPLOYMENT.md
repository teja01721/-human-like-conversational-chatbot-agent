# Deployment Guide

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git
- OpenAI or Claude API key

### Automated Setup
```bash
git clone <repository-url>
cd chatbot-project
python scripts/setup.py
```

## Manual Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env if needed
```

### 3. Database Setup

The application uses SQLite by default for development. For production, configure PostgreSQL in the `.env` file.

### 4. Start Services

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Docker Deployment

### Development with Docker Compose

```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env with your API keys
# OPENAI_API_KEY=your_key_here
# CLAUDE_API_KEY=your_key_here

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Docker Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Scale services if needed
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Build and push images to ECR:**
```bash
# Create ECR repositories
aws ecr create-repository --repository-name chatbot-backend
aws ecr create-repository --repository-name chatbot-frontend

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag images
docker build -t chatbot-backend ./backend
docker tag chatbot-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest

docker build -t chatbot-frontend ./frontend
docker tag chatbot-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/chatbot-frontend:latest

# Push images
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/chatbot-frontend:latest
```

2. **Create ECS Task Definition:**
```json
{
  "family": "chatbot-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/chatbot"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:openai-key"
        }
      ]
    }
  ]
}
```

#### Using AWS Lambda (Serverless)

1. **Install Serverless Framework:**
```bash
npm install -g serverless
```

2. **Create serverless.yml:**
```yaml
service: chatbot-api

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
```

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT_ID/chatbot-backend ./backend
gcloud run deploy chatbot-backend --image gcr.io/PROJECT_ID/chatbot-backend --platform managed

# Build and deploy frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/chatbot-frontend ./frontend
gcloud run deploy chatbot-frontend --image gcr.io/PROJECT_ID/chatbot-frontend --platform managed
```

### Heroku Deployment

#### Backend (API)

```bash
# Create Heroku app
heroku create chatbot-api

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key_here
heroku config:set CLAUDE_API_KEY=your_key_here

# Deploy
git subtree push --prefix backend heroku main
```

#### Frontend

```bash
# Create frontend app
heroku create chatbot-frontend

# Set build pack
heroku buildpacks:set heroku/nodejs

# Set environment variables
heroku config:set VITE_API_URL=https://chatbot-api.herokuapp.com

# Deploy
git subtree push --prefix frontend heroku main
```

### DigitalOcean App Platform

Create `app.yaml`:
```yaml
name: chatbot-app
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-username/chatbot-project
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: OPENAI_API_KEY
    value: your_key_here
    type: SECRET

- name: frontend
  source_dir: /frontend
  github:
    repo: your-username/chatbot-project
    branch: main
  run_command: npm run build && npm run preview -- --host 0.0.0.0 --port $PORT
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs

databases:
- name: chatbot-db
  engine: PG
  version: "13"
```

## Environment Configuration

### Backend Environment Variables

```bash
# AI API Keys (Required)
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key

# Database (Required)
DATABASE_URL=postgresql://user:password@localhost/chatbot_db
# For SQLite: sqlite:///./chatbot.db

# Redis (Optional)
REDIS_URL=redis://localhost:6379

# Vector Store
VECTOR_DB_PATH=./vector_store
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# AI Configuration
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7

# Memory Settings
MAX_MEMORY_ITEMS=100
MEMORY_DECAY_DAYS=30
CONTEXT_WINDOW_SIZE=4000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Frontend Environment Variables

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
# For production: https://your-api-domain.com
```

## Database Setup

### PostgreSQL Setup

```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Start PostgreSQL service
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE chatbot_db;
CREATE USER chatbot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;
\q
```

### Redis Setup

```bash
# Install Redis
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# Start Redis service
sudo systemctl start redis-server

# Test Redis connection
redis-cli ping
```

## SSL/HTTPS Setup

### Using Let's Encrypt with Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring and Logging

### Health Checks

The application provides health check endpoints:
- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed system status

### Logging Configuration

```python
# backend/app/core/logging.py
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

### Monitoring with Prometheus

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Performance Optimization

### Backend Optimizations

1. **Database Connection Pooling:**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

2. **Redis Caching:**
```python
@lru_cache(maxsize=128)
async def get_user_profile(user_id: str):
    # Cache user profiles
    pass
```

3. **Async Processing:**
```python
# Use async/await for I/O operations
async def process_message(message: str):
    # Non-blocking AI API calls
    pass
```

### Frontend Optimizations

1. **Code Splitting:**
```javascript
const UserProfile = lazy(() => import('./components/UserProfile'));
```

2. **Memoization:**
```javascript
const MemoizedChatMessage = React.memo(ChatMessage);
```

3. **Virtual Scrolling:**
```javascript
// For large chat histories
import { FixedSizeList as List } from 'react-window';
```

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump -h localhost -U chatbot_user chatbot_db > backup.sql

# Restore
psql -h localhost -U chatbot_user chatbot_db < backup.sql
```

### Vector Store Backup

```bash
# Backup ChromaDB data
tar -czf vector_backup.tar.gz vector_store/

# Restore
tar -xzf vector_backup.tar.gz
```

## Troubleshooting

### Common Issues

1. **API Key Issues:**
   - Verify API keys are correctly set in `.env`
   - Check API key permissions and quotas
   - Test API connectivity

2. **Database Connection:**
   - Verify database URL format
   - Check database service status
   - Validate credentials

3. **Memory Issues:**
   - Monitor vector store size
   - Implement memory cleanup
   - Check embedding model requirements

4. **Performance Issues:**
   - Monitor response times
   - Check token usage
   - Optimize database queries

### Debug Mode

```bash
# Backend debug mode
export DEBUG=true
uvicorn app.main:app --reload --log-level debug

# Frontend debug mode
npm run dev -- --debug
```

### Log Analysis

```bash
# View application logs
tail -f logs/app.log

# Search for errors
grep -i error logs/app.log

# Monitor real-time logs
docker-compose logs -f backend
```

## Security Checklist

- [ ] API keys stored securely (not in code)
- [ ] Database credentials encrypted
- [ ] HTTPS enabled in production
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation in place
- [ ] Error messages don't leak sensitive info
- [ ] Regular security updates applied
- [ ] Backup encryption enabled
- [ ] Access logs monitored

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Configuration:**
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

2. **Database Scaling:**
   - Read replicas for query optimization
   - Connection pooling
   - Query optimization

3. **Caching Strategy:**
   - Redis cluster for distributed caching
   - CDN for static assets
   - Application-level caching

### Vertical Scaling

- Increase CPU/RAM for AI processing
- SSD storage for faster database access
- Optimize memory usage for embeddings

This deployment guide provides comprehensive instructions for deploying the Human-Like Chatbot in various environments, from development to production-scale deployments.
