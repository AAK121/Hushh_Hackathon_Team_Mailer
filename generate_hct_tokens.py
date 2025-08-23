#!/usr/bin/env python3
"""
HCT Token Generator for MailerPanda Frontend
Generates real cryptographic consent tokens for API authentication.
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope

def generate_mailerpanda_tokens(user_id="frontend_user_123", agent_id="mailerpanda"):
    """
    Generate HCT tokens for MailerPanda with required scopes.
    
    Args:
        user_id: User identifier (default: test_user)
        agent_id: Agent identifier (default: mailerpanda)
    
    Returns:
        dict: Contains individual tokens and combined token list
    """
    
    # Required scopes for MailerPanda operations
    required_scopes = [
        ConsentScope.VAULT_READ_EMAIL,    # vault.read.email
        ConsentScope.VAULT_WRITE_EMAIL,   # vault.write.email  
        ConsentScope.VAULT_READ_FILE,     # vault.read.file
        ConsentScope.VAULT_WRITE_FILE,    # vault.write.file
        ConsentScope.CUSTOM_TEMPORARY     # custom.temporary
    ]
    
    # Token expiration (24 hours from now in milliseconds)
    expires_in_ms = 24 * 60 * 60 * 1000  # 24 hours in milliseconds
    
    tokens = {}
    token_list = []
    
    print(f"Generating HCT tokens for user: {user_id}, agent: {agent_id}")
    print(f"Tokens will expire in: 24 hours")
    print("-" * 60)
    
    for scope in required_scopes:
        try:
            # Generate individual token for each scope
            token_obj = issue_token(
                user_id=user_id,
                agent_id=agent_id,
                scope=scope,
                expires_in_ms=expires_in_ms
            )
            
            # Extract just the token string
            token = token_obj.token
            
            scope_name = scope.value
            tokens[scope_name] = token
            token_list.append(token)
            
            print(f"✅ Generated token for scope: {scope_name}")
            print(f"   Token: {token}")
            print()
            
        except Exception as e:
            print(f"❌ Error generating token for scope {scope.value}: {e}")
            return None
    
    print("-" * 60)
    print("🎯 SUMMARY - Copy these tokens to your frontend:")
    print("-" * 60)
    
    # Format for JavaScript array (ready to copy-paste)
    js_array = "[\n" + ",\n".join([f'    "{token}"' for token in token_list]) + "\n]"
    
    print("JavaScript Array Format:")
    print(js_array)
    print()
    
    # Format for individual usage
    print("Individual Tokens:")
    for scope_name, token in tokens.items():
        print(f"  {scope_name}: {token}")
    
    return {
        'individual': tokens,
        'array': token_list,
        'js_array': js_array
    }

def main():
    """Main function to generate tokens with optional command line arguments."""
    
    # Parse command line arguments
    user_id = sys.argv[1] if len(sys.argv) > 1 else "frontend_user_123"
    agent_id = sys.argv[2] if len(sys.argv) > 2 else "mailerpanda"
    
    print("=" * 60)
    print("🔐 HCT Token Generator for MailerPanda")
    print("=" * 60)
    
    # Check if SECRET_KEY is available
    from hushh_mcp.config import SECRET_KEY
    if not SECRET_KEY or len(SECRET_KEY) < 32:
        print("❌ ERROR: SECRET_KEY not found or too short in .env file")
        print("   Required: Minimum 32 characters")
        return 1
    
    print(f"✅ SECRET_KEY loaded successfully ({len(SECRET_KEY)} characters)")
    print()
    
    # Generate tokens
    result = generate_mailerpanda_tokens(user_id, agent_id)
    
    if result:
        print("\n🚀 Tokens generated successfully!")
        print("   Copy the JavaScript array above and paste it into your frontend code.")
        print("   Replace the consent_tokens array in MailerPandaUI.tsx")
        return 0
    else:
        print("\n❌ Token generation failed!")
        return 1

if __name__ == "__main__":
    exit(main())
