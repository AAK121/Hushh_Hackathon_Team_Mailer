# Railway Deployment Configuration for Memory Service

# Start Command (Railway will use this)
# python api.py

# Environment Variables to set in Railway:
PORT=8005
GOOGLE_API_KEY=your_google_api_key_here
SERVICE_NAME=memory
SERVICE_VERSION=1.0.0
HUSHH_MCP_VAULT_PATH=./vault
HUSHH_MCP_SECRET_KEY=your_hushh_secret_key
MEMORY_RETENTION_DAYS=365
MAX_MEMORIES_PER_CONTACT=100
PROACTIVE_CHECK_INTERVAL_HOURS=24
RELATIONSHIP_ANALYSIS_MODEL=gemini-pro
MIN_INTERACTIONS_FOR_ANALYSIS=5
VAULT_ENCRYPTION_KEY=your_vault_encryption_key_here
VAULT_BACKUP_ENABLED=true
LOG_LEVEL=INFO
CONSENT_TOKEN_SECRET=your_consent_token_secret
ENABLE_PROACTIVE_REMINDERS=true