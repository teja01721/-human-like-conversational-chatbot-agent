# Human-Like Chatbot Architecture

## Overview

This document describes the architecture of the Human-Like Conversational Chatbot built for the STAN Internship Challenge. The system is designed to provide natural, empathetic, and context-aware conversations with long-term memory capabilities.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
├─────────────────────────────────────────────────────────────────┤
│  • Chat Interface     • User Profile    • Memory Management     │
│  • Tone Visualization • Analytics       • Real-time Updates     │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP/WebSocket
┌─────────────────▼───────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                       │
├─────────────────────────────────────────────────────────────────┤
│  • Authentication    • Rate Limiting    • Request Validation    │
│  • Error Handling    • CORS            • Health Checks         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                   Core Services Layer                          │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│ │ Conversation    │ │ Memory          │ │ Personality     │     │
│ │ Engine          │ │ Manager         │ │ Engine          │     │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘     │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│ │ Tone            │ │ AI Client       │ │ Vector Store    │     │
│ │ Analyzer        │ │ (OpenAI/Claude) │ │ (ChromaDB)      │     │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘     │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    Data Storage Layer                          │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐     │
│ │ PostgreSQL      │ │ Redis Cache     │ │ Vector Database │     │
│ │ (User Data,     │ │ (Sessions,      │ │ (Embeddings,    │     │
│ │ Chat History)   │ │ Temp Data)      │ │ Semantic Search)│     │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Conversation Engine
**Purpose**: Orchestrates the entire conversation flow
**Key Features**:
- Message processing and response generation
- Context management and conversation history
- Integration with memory and personality systems
- Tone adaptation based on user emotional state

**Flow**:
1. Receives user message
2. Analyzes tone and emotion
3. Recalls relevant memories
4. Generates personality-aware system prompt
5. Calls AI model with context
6. Post-processes response for human-likeness
7. Stores conversation and extracts new memories

### 2. Memory Manager
**Purpose**: Handles long-term memory storage and retrieval
**Key Features**:
- Automatic memory extraction from conversations
- Semantic search for relevant memories
- Memory importance scoring and decay
- User profile generation from memories

**Memory Types**:
- **Preferences**: User likes/dislikes, communication style
- **Facts**: Personal information, relationships, work
- **Emotions**: Emotional patterns and triggers
- **Goals**: User aspirations and objectives
- **Context**: Conversation context and topics

### 3. Vector Store (ChromaDB)
**Purpose**: Efficient semantic search and memory storage
**Key Features**:
- Sentence transformer embeddings (all-MiniLM-L6-v2)
- Cosine similarity search
- Metadata filtering (user, type, importance)
- Persistent storage with compression

### 4. Personality Engine
**Purpose**: Generates human-like, personalized responses
**Key Features**:
- Dynamic system prompt generation
- Personality trait analysis
- Communication style adaptation
- Response variety and natural flow

### 5. Tone Analyzer
**Purpose**: Analyzes user emotional state and communication style
**Key Features**:
- Sentiment analysis (positive/negative/neutral)
- Emotion detection (joy, sadness, anger, fear, surprise, disgust)
- Formality level assessment (formal/casual/neutral)
- Urgency detection

### 6. AI Client
**Purpose**: Interfaces with external AI models
**Supported Models**:
- OpenAI GPT (3.5-turbo, 4)
- Anthropic Claude (3-haiku, 3-sonnet)
- Fallback mechanisms for reliability

**Features**:
- Token counting and compression
- Context window management
- Model selection based on availability
- Cost optimization strategies

## Data Models

### User Model
```python
class User:
    id: int
    user_id: str (unique)
    name: Optional[str]
    email: Optional[str]
    preferences: Dict[str, Any]
    personality_profile: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
```

### Chat Session
```python
class ChatSession:
    id: int
    session_id: str (unique)
    user_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### Chat Message
```python
class ChatMessage:
    id: int
    session_id: str
    user_id: str
    message: str
    response: str
    tone_detected: Optional[str]
    emotion_score: Dict[str, float]
    timestamp: datetime
    tokens_used: int
```

### User Memory
```python
class UserMemory:
    id: int
    user_id: str
    memory_type: str
    content: str
    importance_score: int (1-10)
    created_at: datetime
    last_accessed: datetime
    access_count: int
```

## API Endpoints

### Chat Endpoints
- `POST /api/chat/message` - Send message to chatbot
- `GET /api/chat/sessions/{user_id}` - Get user's chat sessions
- `GET /api/chat/history/{session_id}` - Get chat history
- `DELETE /api/chat/sessions/{session_id}` - Delete session
- `GET /api/chat/analytics/{user_id}` - Get conversation analytics

### User Endpoints
- `POST /api/users/` - Create user
- `GET /api/users/{user_id}` - Get user info
- `PUT /api/users/{user_id}` - Update user
- `GET /api/users/{user_id}/profile` - Get user profile
- `GET /api/users/{user_id}/memories` - Get user memories
- `POST /api/users/{user_id}/memories` - Add memory
- `DELETE /api/users/{user_id}/memories/{memory_id}` - Delete memory

### Health Endpoints
- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed system status

## Memory System Architecture

### Memory Lifecycle
1. **Extraction**: AI analyzes conversations for important information
2. **Storage**: Memories stored in both SQL database and vector store
3. **Indexing**: Vector embeddings created for semantic search
4. **Retrieval**: Relevant memories recalled based on query similarity
5. **Decay**: Old, low-importance memories gradually fade

### Memory Scoring
- **Importance Score**: 1-10 scale based on content significance
- **Recency**: Recently created memories have higher weight
- **Access Frequency**: Frequently accessed memories stay relevant
- **Similarity**: Semantic similarity to current conversation

### Memory Types and Use Cases
- **Preferences**: "User prefers casual communication" → Adjust tone
- **Facts**: "User works as a teacher" → Reference in career discussions
- **Emotions**: "User feels anxious about presentations" → Provide support
- **Goals**: "User wants to learn Spanish" → Suggest resources
- **Context**: "Discussed vacation plans" → Follow up later

## Personality System

### Personality Traits Analysis
The system analyzes user interactions to build a personality profile:

```python
PersonalityProfile = {
    "communication_style": "formal|casual|friendly|professional",
    "formality_preference": "formal|neutral|casual", 
    "emotional_sensitivity": 0.0-1.0,
    "humor_appreciation": 0.0-1.0,
    "traits": ["curious", "analytical", "empathetic", ...],
    "topics_of_interest": ["technology", "sports", "music", ...]
}
```

### Response Adaptation
Based on personality analysis, the system adapts:
- **Vocabulary**: Formal vs casual language
- **Tone**: Professional vs friendly approach
- **Content**: Technical vs simplified explanations
- **Humor**: Appropriate level and type
- **Empathy**: Emotional support level

## Performance Optimizations

### Token Management
- Context compression for long conversations
- Smart truncation preserving important information
- Token counting and budget management
- Efficient prompt engineering

### Caching Strategy
- Redis for session data and temporary storage
- Vector store for persistent memory search
- Response caching for common queries
- Memory result caching

### Cost Optimization
- Model selection based on query complexity
- Batch processing for memory operations
- Compression of conversation history
- Efficient embedding generation

## Security Considerations

### Data Protection
- User data encryption at rest and in transit
- API key secure storage and rotation
- Input sanitization and validation
- Rate limiting and abuse prevention

### Privacy
- User consent for memory storage
- Data retention policies
- Memory deletion capabilities
- Anonymous usage analytics

## Scalability Design

### Horizontal Scaling
- Stateless API design
- Database connection pooling
- Load balancer ready
- Microservice architecture

### Performance Monitoring
- Response time tracking
- Token usage monitoring
- Memory system performance
- Error rate tracking

## Deployment Architecture

### Development Environment
- Local SQLite database
- File-based vector store
- Environment variables for configuration
- Hot reload for development

### Production Environment
- PostgreSQL for relational data
- Redis for caching and sessions
- Persistent vector store
- Docker containerization
- Health checks and monitoring

### Infrastructure Requirements
- **CPU**: 2+ cores for AI processing
- **Memory**: 4GB+ RAM for embeddings
- **Storage**: SSD for database and vector store
- **Network**: Stable internet for AI API calls

## Testing Strategy

### Unit Tests
- Individual component testing
- Mock external dependencies
- Memory system validation
- API endpoint testing

### Integration Tests
- End-to-end conversation flow
- Memory persistence across sessions
- AI model integration
- Database operations

### Behavioral Tests
- Memory recall accuracy
- Tone adaptation effectiveness
- Personality consistency
- Response variety validation

## Future Enhancements

### Advanced Features
- Multi-language support
- Voice conversation capabilities
- Advanced emotion recognition
- Custom personality training

### Technical Improvements
- GraphQL API option
- Real-time WebSocket communication
- Advanced caching strategies
- Machine learning model fine-tuning

### Integration Capabilities
- Social media platform integration
- CRM system connectivity
- Analytics dashboard
- Third-party AI model support

This architecture provides a robust foundation for a human-like conversational AI that can be easily extended and integrated into various platforms while maintaining high performance and user satisfaction.
