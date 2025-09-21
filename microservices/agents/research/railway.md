# Railway Deployment Configuration for Research Service
# Use this configuration when deploying to Railway

# Start Command (Railway will use this)
# python api.py

# Environment Variables to set in Railway:
PORT=8003
GOOGLE_API_KEY=your_google_api_key_here
ARXIV_MAX_RESULTS=20
ARXIV_DELAY_SECONDS=3
SERVICE_NAME=research
SERVICE_VERSION=1.0.0
HUSHH_MCP_VAULT_PATH=./vault
HUSHH_MCP_SECRET_KEY=your_hushh_secret_key
PAPERS_STORAGE_PATH=./papers
MAX_PAPER_SIZE=10MB
PDF_TIMEOUT_SECONDS=30
MAX_PAGES_PER_PAPER=50
LOG_LEVEL=INFO
CONSENT_TOKEN_SECRET=your_consent_token_secret

# Railway automatically detects Python and will:
# 1. Install requirements.txt
# 2. Run the start command (python api.py)
# 3. Expose the PORT environment variable