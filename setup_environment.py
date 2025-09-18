#!/usr/bin/env python3
"""
HushhMCP Environment Setup Script

This script generates the required cryptographic keys for the HushhMCP system
and provides instructions for setting them as environment variables.

SECURITY WARNING: These keys are critical for system security.
- Store them securely
- Never commit them to version control
- Use different keys for production and development
"""

import secrets
import os
from pathlib import Path

def generate_key_pair():
    """Generate a 64-character hex key (256-bit)"""
    return secrets.token_hex(32)

def main():
    print("🔐 HushhMCP Environment Setup")
    print("=" * 50)
    
    # Generate required keys
    vault_encryption_key = generate_key_pair()
    vault_master_key = generate_key_pair()
    hushh_secret_key = generate_key_pair()
    
    print("\n✅ Generated cryptographic keys:")
    print(f"VAULT_ENCRYPTION_KEY={vault_encryption_key}")
    print(f"VAULT_MASTER_KEY={vault_master_key}")
    print(f"HUSHH_SECRET_KEY={hushh_secret_key}")
    
    # Create .env file
    env_content = f"""# HushhMCP Environment Configuration
# Generated on: {datetime.now().isoformat()}
# 
# WARNING: Keep these keys secure and private
# - Do not commit this file to version control
# - Use different keys for production and development
# - Rotate keys regularly for enhanced security

# Vault encryption keys (256-bit AES keys in hex format)
VAULT_ENCRYPTION_KEY={vault_encryption_key}
VAULT_MASTER_KEY={vault_master_key}

# HushhMCP consent token signing key
HUSHH_SECRET_KEY={hushh_secret_key}

# User-specific encryption (enable/disable)
ENABLE_USER_SPECIFIC_KEYS=true

# Vault storage directory
VAULT_ROOT=vault
"""
    
    # Write to .env file
    env_file = Path(".env")
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"\n📝 Environment file created: {env_file.absolute()}")
    
    print("\n🚀 Vercel Deployment Setup:")
    print("Run these commands to set up Vercel environment variables:")
    print(f"vercel env add VAULT_ENCRYPTION_KEY production")
    print(f"  → Enter: {vault_encryption_key}")
    print(f"vercel env add VAULT_MASTER_KEY production")  
    print(f"  → Enter: {vault_master_key}")
    print(f"vercel env add HUSHH_SECRET_KEY production")
    print(f"  → Enter: {hushh_secret_key}")
    
    print("\n✅ Setup Complete!")
    print("Your HushhMCP system is now configured with proper cryptographic keys.")
    print("\nIMPORTANT SECURITY NOTES:")
    print("1. Keep the .env file private and secure")
    print("2. Never commit keys to version control")
    print("3. Use different keys for different environments")
    print("4. Rotate keys regularly for enhanced security")

if __name__ == "__main__":
    from datetime import datetime
    main()
