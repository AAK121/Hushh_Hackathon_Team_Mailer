# Finance Agent - Railway Deployment

## Service Configuration

**Service Name**: `hushh-finance`
**Runtime**: Python 3.11
**Start Command**: `python api.py`
**Port**: 8000

## Repository Setup

1. **Connect Repository**: Link your GitHub repository `Hushh_Hackathon_Team_Mailer`
2. **Set Root Directory**: `microservices/agents/finance`
3. **Auto-Deploy**: Enable for main branch

## Environment Variables

Add these environment variables in Railway dashboard:

```env
# Financial APIs
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key-here
FINNHUB_API_KEY=your-finnhub-key-here
YAHOO_FINANCE_API_KEY=your-yahoo-finance-key
POLYGON_API_KEY=your-polygon-key-here
QUANDL_API_KEY=your-quandl-key-here

# AI/ML APIs
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# Database
DATABASE_URL=postgresql://username:password@host:port/database
REDIS_URL=redis://username:password@host:port

# Authentication
API_KEY=finance-service-secure-key-2024

# Service Settings
SERVICE_NAME=finance
ENVIRONMENT=production
PORT=8000
PYTHONPATH=/app

# Python Settings
PYTHON_VERSION=3.11
PIP_NO_CACHE_DIR=1

# Memory Settings (for data processing)
WEB_MEMORY=1536
WEB_CONCURRENCY=2

# Timeout Settings
REQUEST_TIMEOUT=180
STARTUP_TIMEOUT=90

# Financial Data Settings
MARKET_DATA_CACHE_TTL=300
MAX_HISTORICAL_DAYS=365
DEFAULT_CURRENCY=USD
```

## Resource Configuration

- **Memory**: 1.5GB (for financial data processing)
- **CPU**: 2 vCPU
- **Storage**: 3GB
- **Timeout**: 180 seconds

## Health Check

The service will be available at:
- **Health Check**: `https://hushh-finance.railway.app/health`
- **API Documentation**: `https://hushh-finance.railway.app/docs`

## Deployment Steps

1. **Create New Project** in Railway
2. **Connect GitHub Repository**
3. **Set Service Name**: `hushh-finance`
4. **Configure Environment Variables** (copy from above)
5. **Set Start Command**: `python api.py`
6. **Deploy**

## Expected URL
After deployment: `https://hushh-finance.railway.app`

## API Endpoints

- `POST /search` - Search financial data
- `POST /upload` - Upload financial documents
- `GET /status` - Service status
- `GET /health` - Health check

## Monitoring

- Check deployment logs in Railway dashboard
- Monitor memory usage during data processing
- Verify API response times under 10 seconds
- Monitor external API rate limits

## Dependencies

The service includes heavy financial and ML dependencies:
- pandas (data processing)
- numpy (numerical computing)
- yfinance (financial data)
- langchain (large package)
- transformers (ML models)
- scikit-learn (ML algorithms)
- matplotlib (plotting)
- requests (API calls)

Total package size: ~300MB (too large for Vercel)

## Security Notes

- All API keys stored as environment variables
- Rate limiting implemented for external APIs
- Input validation for financial queries
- HTTPS only communication