#!/usr/bin/env python3
"""
Generate Valid HushhMCP Token for Testing
=========================================
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope

def generate_test_token():
    """Generate a valid HushhMCP token for testing"""
    
    # Required scopes for ChanduFinance agent - use single scope as base
    scope = ConsentScope.VAULT_WRITE_FILE
    
    token = issue_token(
        user_id="test_user_123",
        agent_id="chandufinance",
        scope=scope,
        expires_in_ms=24 * 60 * 60 * 1000  # 24 hours
    )
    
    print("Generated Valid HushhMCP Token:")
    print("=" * 50)
    print(f"Token: {token.token}")
    print(f"User ID: {token.user_id}")
    print(f"Agent ID: {token.agent_id}")
    print(f"Scope: {token.scope}")
    print(f"Issued At: {token.issued_at}")
    print(f"Expires At: {token.expires_at}")
    
    return token.token

if __name__ == "__main__":
    token = generate_test_token()
