# Human-Like Conversational Chatbot - STAN Internship Challenge

A sophisticated chatbot with memory, empathy, and context-awareness that feels genuinely human-like.

## 🎯 Features

- **Human-like Conversations**: Natural, emotional, and engaging interactions
- **Long-term Memory**: Remembers user preferences, chat history, and personal details
- **Tone Adaptation**: Adjusts communication style based on user mood and context
- **Multi-AI Support**: OpenAI GPT, Claude, and local models (Ollama)
- **Vector Memory**: Efficient semantic search and context retrieval
- **Cost Optimization**: Token compression and smart context management

## 🏗️ Architecture

```
chatbot-project/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── tests/              # Test cases
│   └── requirements.txt
├── frontend/               # React chat UI
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   └── utils/          # Frontend utilities
│   └── package.json
├── docs/                   # Documentation
└── docker-compose.yml      # Container orchestration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker (optional)
- OpenAI API Key or Claude API Key

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
Create `.env` files in both backend and frontend directories:

**Backend `.env`:**
```
OPENAI_API_KEY=your_openai_key
CLAUDE_API_KEY=your_claude_key
DATABASE_URL=postgresql://user:pass@localhost/chatbot
REDIS_URL=redis://localhost:6379
VECTOR_DB_PATH=./vector_store
```

**Frontend `.env`:**
```
VITE_API_URL=http://localhost:8000
```

## 🧪 Test Cases

Run the comprehensive test suite:
```bash
cd backend
python -m pytest tests/ -v
```

Test cases cover:
- Memory recall across sessions
- Tone adaptation based on user mood
- Personalization and preference memory
- Natural conversation variety
- Identity consistency
- Hallucination resistance
- Stable memory handling

## 📊 Performance

- **Response Time**: < 2 seconds average
- **Memory Efficiency**: Vector embeddings with compression
- **Cost Optimization**: Smart token management and caching
- **Scalability**: Modular architecture for easy integration

## 🔧 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment
1. Set up PostgreSQL and Redis
2. Configure environment variables
3. Run database migrations
4. Start backend and frontend services

## 🎨 Customization

The chatbot personality and behavior can be customized through:
- `backend/app/core/personality.py` - Core personality traits
- `backend/app/services/tone_analyzer.py` - Tone detection logic
- `backend/app/services/memory_manager.py` - Memory handling

## 📈 Monitoring

- Health checks at `/health`
- Metrics at `/metrics`
- Logs in structured JSON format

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.
