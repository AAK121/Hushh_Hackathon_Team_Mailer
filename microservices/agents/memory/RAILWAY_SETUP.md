# Memory Agent - Railway Deployment

## Service Configuration

**Service Name**: `hushh-memory`
**Runtime**: Python 3.11
**Start Command**: `python api.py`
**Port**: 8000

## Repository Setup

1. **Connect Repository**: Link your GitHub repository `Hushh_Hackathon_Team_Mailer`
2. **Set Root Directory**: `microservices/agents/memory`
3. **Auto-Deploy**: Enable for main branch

## Environment Variables

Add these environment variables in Railway dashboard:

```env
# AI/ML APIs
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# Vector Database
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_ENVIRONMENT=your-pinecone-environment
PINECONE_INDEX_NAME=hushh-memory-index

# Alternative Vector DBs (choose one)
WEAVIATE_URL=your-weaviate-cluster-url
WEAVIATE_API_KEY=your-weaviate-api-key
CHROMA_PERSIST_DIRECTORY=/app/chroma_db

# Traditional Database
DATABASE_URL=postgresql://username:password@host:port/database
REDIS_URL=redis://username:password@host:port

# Authentication
API_KEY=memory-service-secure-key-2024

# Service Settings
SERVICE_NAME=memory
ENVIRONMENT=production
PORT=8000
PYTHONPATH=/app

# Python Settings
PYTHON_VERSION=3.11
PIP_NO_CACHE_DIR=1

# Memory Settings (for vector processing)
WEB_MEMORY=2048
WEB_CONCURRENCY=2

# Timeout Settings
REQUEST_TIMEOUT=300
STARTUP_TIMEOUT=120

# Memory Agent Settings
MAX_MEMORY_ENTRIES=10000
SIMILARITY_THRESHOLD=0.8
EMBEDDING_MODEL=text-embedding-ada-002
VECTOR_DIMENSION=1536
BATCH_SIZE=100

# Chat Settings
MAX_CHAT_HISTORY=50
SESSION_TIMEOUT=3600
AUTO_SAVE_INTERVAL=30
```

## Resource Configuration

- **Memory**: 2GB (for vector embeddings and ML models)
- **CPU**: 2 vCPU
- **Storage**: 5GB (for persistent memory)
- **Timeout**: 300 seconds

## Health Check

The service will be available at:
- **Health Check**: `https://hushh-memory.railway.app/health`
- **API Documentation**: `https://hushh-memory.railway.app/docs`

## Deployment Steps

1. **Create New Project** in Railway
2. **Connect GitHub Repository**
3. **Set Service Name**: `hushh-memory`
4. **Configure Environment Variables** (copy from above)
5. **Set Start Command**: `python api.py`
6. **Deploy**

## Expected URL
After deployment: `https://hushh-memory.railway.app`

## API Endpoints

- `POST /execute` - Execute memory operations
- `POST /proactive` - Proactive memory suggestions
- `POST /chat/start` - Start chat session
- `POST /chat/message` - Send chat message
- `GET /chat/{session_id}/history` - Get chat history
- `DELETE /chat/{session_id}` - End chat session
- `GET /chat/sessions` - List active sessions
- `GET /status` - Service status
- `GET /health` - Health check

## Monitoring

- Check deployment logs in Railway dashboard
- Monitor memory usage during vector operations
- Verify embedding generation performance
- Monitor vector database connections
- Track chat session persistence

## Dependencies

The service includes heavy ML and vector database dependencies:
- langchain (large package)
- transformers (ML models)
- torch/pytorch (ML framework)
- pinecone-client (vector database)
- chromadb (local vector database)
- sentence-transformers (embeddings)
- numpy (numerical computing)
- pandas (data processing)
- redis (caching)

Total package size: ~400MB (too large for Vercel)

## Data Persistence

The memory agent requires persistent storage for:
- **Vector Embeddings**: Long-term memory storage
- **Chat Sessions**: Active conversation state
- **User Relationships**: Relationship mapping data
- **Memory Metadata**: Timestamps, relevance scores

## Security & Privacy

- All conversation data encrypted at rest
- Personal data anonymized before storage
- GDPR-compliant data retention policies
- Secure vector database connections
- Memory purging on user request