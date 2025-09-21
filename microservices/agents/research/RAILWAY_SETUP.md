# Research Agent - Railway Deployment

## Service Configuration

**Service Name**: `hushh-research`
**Runtime**: Python 3.11
**Start Command**: `python api.py`
**Port**: 8000

## Repository Setup

1. **Connect Repository**: Link your GitHub repository `Hushh_Hackathon_Team_Mailer`
2. **Set Root Directory**: `microservices/agents/research`
3. **Auto-Deploy**: Enable for main branch

## Environment Variables

Add these environment variables in Railway dashboard:

```env
# AI/ML API Keys
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# Research APIs
ARXIV_API_KEY=your-arxiv-key-here
SEMANTIC_SCHOLAR_API_KEY=your-semantic-scholar-key

# Database (if needed)
DATABASE_URL=postgresql://username:password@host:port/database

# Authentication
API_KEY=research-service-secure-key-2024

# Service Settings
SERVICE_NAME=research
ENVIRONMENT=production
PORT=8000
PYTHONPATH=/app

# Python Settings
PYTHON_VERSION=3.11
PIP_NO_CACHE_DIR=1

# Memory Settings (for large ML models)
WEB_MEMORY=2048
WEB_CONCURRENCY=2

# Timeout Settings
REQUEST_TIMEOUT=300
STARTUP_TIMEOUT=120
```

## Resource Configuration

- **Memory**: 2GB (for ML models and large documents)
- **CPU**: 2 vCPU
- **Storage**: 5GB
- **Timeout**: 300 seconds

## Health Check

The service will be available at:
- **Health Check**: `https://hushh-research.railway.app/health`
- **API Documentation**: `https://hushh-research.railway.app/docs`

## Deployment Steps

1. **Create New Project** in Railway
2. **Connect GitHub Repository**
3. **Set Service Name**: `hushh-research`
4. **Configure Environment Variables** (copy from above)
5. **Set Start Command**: `python api.py`
6. **Deploy**

## Expected URL
After deployment: `https://hushh-research.railway.app`

## Monitoring

- Check deployment logs in Railway dashboard
- Monitor memory usage (should stay under 2GB)
- Verify health endpoint responds within 30 seconds

## Dependencies

The service includes heavy ML dependencies:
- langchain (large package)
- transformers (ML models)
- torch/pytorch (ML framework)
- pandas (data processing)
- numpy (numerical computing)
- PyPDF2 (document processing)

Total package size: ~500MB (too large for Vercel)