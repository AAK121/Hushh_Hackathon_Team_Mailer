# hushh_mcp/config.py

import os
import secrets
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')

# Load .env file into environment
load_dotenv()

# ==================== Security Keys ====================

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    # Generate a temporary key for serverless environments
    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        print("🔧 Generating temporary SECRET_KEY for Vercel deployment")
        SECRET_KEY = secrets.token_hex(32)  # 64-character hex string
    else:
        raise ValueError("❌ SECRET_KEY must be set in .env and at least 32 characters long")

# Global vault encryption key (for legacy support)
VAULT_ENCRYPTION_KEY = os.getenv("VAULT_ENCRYPTION_KEY")
if not VAULT_ENCRYPTION_KEY or len(VAULT_ENCRYPTION_KEY) != 64:
    # Generate a temporary key for serverless environments
    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        print("🔧 Generating temporary VAULT_ENCRYPTION_KEY for Vercel deployment")
        VAULT_ENCRYPTION_KEY = secrets.token_hex(32)  # 64-character hex string
    else:
        raise ValueError("❌ VAULT_ENCRYPTION_KEY must be a 64-character hex string (256-bit AES key)")

# Master key for encrypting user-specific keys
VAULT_MASTER_KEY = os.getenv("VAULT_MASTER_KEY")
if not VAULT_MASTER_KEY or len(VAULT_MASTER_KEY) != 64:
    # Generate a temporary key for serverless environments
    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        print("🔧 Generating temporary VAULT_MASTER_KEY for Vercel deployment")
        VAULT_MASTER_KEY = secrets.token_hex(32)  # 64-character hex string
    else:
        raise ValueError("❌ VAULT_MASTER_KEY must be set as a 64-character hex string (256-bit AES key) in environment variables")

# ==================== User Management ====================

# Enable user-specific encryption keys
ENABLE_USER_SPECIFIC_KEYS = os.getenv("ENABLE_USER_SPECIFIC_KEYS", "true").lower() == "true"

# Vault root directory
VAULT_ROOT = os.getenv("VAULT_ROOT", "vault")

# ==================== Expiration Settings ====================

# Default expiry durations (in milliseconds)
# 7 days
DEFAULT_CONSENT_TOKEN_EXPIRY_MS = int(os.getenv("DEFAULT_CONSENT_TOKEN_EXPIRY_MS", 1000 * 60 * 60 * 24 * 7))  # 30 days
DEFAULT_TRUST_LINK_EXPIRY_MS = int(os.getenv("DEFAULT_TRUST_LINK_EXPIRY_MS", 1000 * 60 * 60 * 24 * 30))      

# ==================== Environment Info ====================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
AGENT_ID = os.getenv("AGENT_ID", "agent_hushh_default")
HUSHH_HACKATHON = os.getenv("HUSHH_HACKATHON", "disabled").lower() == "enabled"

# ==================== External API URLs ====================

# ArXiv API URLs
ARXIV_API_BASE_URL = os.getenv("ARXIV_API_BASE_URL", "http://export.arxiv.org/api/query")
ARXIV_PDF_BASE_URL = os.getenv("ARXIV_PDF_BASE_URL", "https://arxiv.org/pdf")
ARXIV_ABS_BASE_URL = os.getenv("ARXIV_ABS_BASE_URL", "https://arxiv.org/abs")

# Google OAuth URLs
GOOGLE_OAUTH_TOKEN_URI = os.getenv("GOOGLE_OAUTH_TOKEN_URI", "https://oauth2.googleapis.com/token")
GOOGLE_CALENDAR_SCOPE = os.getenv("GOOGLE_CALENDAR_SCOPE", "https://www.googleapis.com/auth/calendar.events")

# Other API URLs can be added here as needed
# PUBMED_API_BASE_URL = os.getenv("PUBMED_API_BASE_URL", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils")
# SEMANTIC_SCHOLAR_API_BASE_URL = os.getenv("SEMANTIC_SCHOLAR_API_BASE_URL", "https://api.semanticscholar.org/graph/v1")

# API Timeouts and limits
API_REQUEST_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", "15"))  # seconds
ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", "10"))

# ==================== Defaults Export ====================

__all__ = [
    "SECRET_KEY",
    "VAULT_ENCRYPTION_KEY",
    "VAULT_MASTER_KEY",
    "ENABLE_USER_SPECIFIC_KEYS",
    "VAULT_ROOT",
    "DEFAULT_CONSENT_TOKEN_EXPIRY_MS",
    "DEFAULT_TRUST_LINK_EXPIRY_MS",
    "ENVIRONMENT",
    "AGENT_ID",
    "HUSHH_HACKATHON",
    "ARXIV_API_BASE_URL",
    "ARXIV_PDF_BASE_URL",
    "ARXIV_ABS_BASE_URL",
    "GOOGLE_OAUTH_TOKEN_URI",
    "GOOGLE_CALENDAR_SCOPE",
    "API_REQUEST_TIMEOUT",
    "ARXIV_MAX_RESULTS"
]
