# Railway Deployment Configuration for Finance Service

# Start Command (Railway will use this)
# python api.py

# Environment Variables to set in Railway:
PORT=8004
GOOGLE_API_KEY=your_google_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
YAHOO_FINANCE_API_KEY=your_yahoo_finance_key_here
SERVICE_NAME=finance
SERVICE_VERSION=1.0.0
HUSHH_MCP_VAULT_PATH=./vault
HUSHH_MCP_SECRET_KEY=your_hushh_secret_key
DEFAULT_ANALYSIS_PERIOD=1y
MAX_PORTFOLIO_SIZE=50
CACHE_DURATION_MINUTES=15
MAX_POSITION_SIZE=0.1
RISK_FREE_RATE=0.02
LOG_LEVEL=INFO
CONSENT_TOKEN_SECRET=your_consent_token_secret