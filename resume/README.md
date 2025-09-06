# STAN Internship Challenge - Human-like Conversational Chatbot

🤖 **LIVE DEMO**: [Chat with the AI](https://your-chatbot-url.netlify.app) | 📚 **API Docs**: [Backend API](https://your-backend-url.railway.app/docs)

A sophisticated full-stack chatbot application with human-like conversation capabilities, memory persistence, and context awareness. This project demonstrates advanced NLP techniques and efficient memory management for creating more natural AI interactions.

## 🎯 Challenge Requirements ✅

All STAN Internship Challenge requirements have been successfully implemented:

- ✅ **Human-like Conversations**: Natural, emotional, and engaging interactions
- ✅ **Memory & Personalization**: Persistent user profiles across sessions  
- ✅ **Non-Google AI Models**: OpenAI GPT and Anthropic Claude integration
- ✅ **Efficient Storage**: ChromaDB vector store with PostgreSQL/SQLite
- ✅ **Modular Backend**: Pluggable FastAPI architecture
- ✅ **Clean Documentation**: Comprehensive guides and API docs
- ✅ **All 7 Test Cases**: Memory recall, tone adaptation, personalization validated

## 🚀 **LIVE DEPLOYMENT**

The chatbot is production-ready and can be deployed to live web hosting with one command:

### Quick Deploy (Windows)
```bash
cd chatbot-project
deploy.bat
```

### Quick Deploy (Linux/Mac)
```bash
cd chatbot-project
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment Options
- **Railway** (Backend) + **Netlify** (Frontend) - Recommended
- **Heroku** (Backend) + **Vercel** (Frontend) - Alternative
- **Docker** deployment to any cloud provider

## Features

- **Human-like Interaction**: Natural, emotional, and engaging conversations with personality consistency
- **Memory & Personalization**: Per-user profiles and preferences stored efficiently
- **Context Awareness**: Maintains conversation flow and recalls previous topics
- **Adaptive Tone**: Shifts between formal/informal based on context
- **Emotional Intelligence**: Callbacks to previous emotional moments in conversations
- **Multi-model Support**: Integration with OpenAI GPT, Claude, and Mistral models
- **Efficient Storage**: Optimized memory persistence with multi-tiered approach
- **Cost Optimization**: Token compression and efficient context management

## Project Structure

```
├── backend/               # Python FastAPI backend
│   ├── app/              # Application code
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── db/           # Database models and connections
│   │   ├── memory/       # Memory system implementation
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic services
│   │   └── utils/        # Utility functions
│   ├── tests/            # Backend tests
│   ├── .env.example      # Environment variables example
│   ├── requirements.txt  # Python dependencies
│   └── main.py           # Application entry point
├── frontend/             # React frontend
│   ├── public/           # Public assets
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── contexts/     # React contexts
│   │   ├── hooks/        # Custom hooks
│   │   ├── pages/        # Application pages
│   │   ├── services/     # API services
│   │   ├── styles/       # CSS styles
│   │   ├── utils/        # Utility functions
│   │   ├── App.jsx       # Main application component
│   │   └── index.jsx     # Entry point
│   ├── package.json      # NPM dependencies
│   └── vite.config.js    # Vite configuration
├── docs/                 # Documentation
│   └── architecture.pdf  # Architecture document
├── docker-compose.yml    # Docker Compose configuration
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## Technology Stack

### Backend
- Python 3.9+
- FastAPI (web framework)
- SQLAlchemy (ORM)
- PostgreSQL (relational database)
- Redis (caching and session management)
- Pinecone/Qdrant (vector database for embeddings)
- OpenAI API / Anthropic Claude API / Mistral API

### Frontend
- React 18+
- Vite (build tool)
- TailwindCSS (styling)
- Axios (HTTP client)

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- Redis
- Docker & Docker Compose (optional)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and configure your environment variables.

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file based on `.env.example` and configure your environment variables.

4. Run the development server:
   ```bash
   npm run dev
   ```

### Docker Setup (Optional)

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

## API Documentation

Once the backend is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Memory System Architecture

The chatbot's memory system consists of three components:

1. **Short-term Memory**: Recent conversation turns stored in Redis for fast access
   - Caches user preferences and active conversation state
   - Provides immediate context for the current conversation

2. **Long-term Memory**: Complete conversation history in PostgreSQL
   - Stores all messages with metadata (sentiment, tokens, timestamps)
   - Enables recalling specific conversations across sessions

3. **Semantic Memory**: Vector embeddings for semantic search in Qdrant/Pinecone
   - Converts messages to embeddings for similarity search
   - Allows retrieving contextually relevant information based on semantic meaning
   - Supports "remembering" topics discussed in previous conversations

This multi-tiered approach enables the chatbot to:
- Maintain conversation flow within a session
- Recall previous interactions across sessions
- Retrieve relevant information based on semantic similarity
- Adapt responses based on user preferences and conversation history

## Testing

### Backend Tests

```bash
cd backend
python -m pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## License

MIT