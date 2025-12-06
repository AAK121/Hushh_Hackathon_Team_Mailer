# hushh_mcp/config.py

import os
import sys
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')

# Load .env file into environment
load_dotenv(dotenv_path)

print("Environment variables loaded from .env file", file=sys.stderr)

# ==================== Security Keys ====================

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    error_msg = (
        "❌ SECRET_KEY must be set in .env and at least 32 characters long\n"
        "For Docker deployments, ensure:\n"
        "  1. .env file exists in the project root with SECRET_KEY=<your-key>\n"
        "  2. docker-compose.yml includes 'env_file: - .env' under the backend service\n"
        f"Current SECRET_KEY value: {SECRET_KEY!r} (length: {len(SECRET_KEY) if SECRET_KEY else 0})"
    )
    raise ValueError(error_msg)

VAULT_ENCRYPTION_KEY = os.getenv("VAULT_ENCRYPTION_KEY")
if not VAULT_ENCRYPTION_KEY or len(VAULT_ENCRYPTION_KEY) != 64:
    error_msg = (
        "❌ VAULT_ENCRYPTION_KEY must be a 64-character hex string (256-bit AES key)\n"
        "For Docker deployments, ensure:\n"
        "  1. .env file exists in the project root with VAULT_ENCRYPTION_KEY=<64-hex-chars>\n"
        "  2. docker-compose.yml includes 'env_file: - .env' under the backend service\n"
        f"Current VAULT_ENCRYPTION_KEY value: {VAULT_ENCRYPTION_KEY!r} (length: {len(VAULT_ENCRYPTION_KEY) if VAULT_ENCRYPTION_KEY else 0})"
    )
    raise ValueError(error_msg)

# ==================== Expiration Settings ====================

# Default expiry durations (in milliseconds)
# 7 days
DEFAULT_CONSENT_TOKEN_EXPIRY_MS = int(os.getenv("DEFAULT_CONSENT_TOKEN_EXPIRY_MS", 1000 * 60 * 60 * 24 * 7))  # 30 days
DEFAULT_TRUST_LINK_EXPIRY_MS = int(os.getenv("DEFAULT_TRUST_LINK_EXPIRY_MS", 1000 * 60 * 60 * 24 * 30))      

# ==================== Environment Info ====================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
AGENT_ID = os.getenv("AGENT_ID", "agent_hushh_default")
HUSHH_HACKATHON = os.getenv("HUSHH_HACKATHON", "disabled").lower() == "enabled"

# ==================== Defaults Export ====================

__all__ = [
    "SECRET_KEY",
    "VAULT_ENCRYPTION_KEY",
    "DEFAULT_CONSENT_TOKEN_EXPIRY_MS",
    "DEFAULT_TRUST_LINK_EXPIRY_MS",
    "ENVIRONMENT",
    "AGENT_ID",
    "HUSHH_HACKATHON"
]
