#!/usr/bin/env python3
"""API integration test for HushMCP Email Suite."""

import sys
import os
import time
import subprocess
import requests
from datetime import datetime, timedelta

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_api_offline():
    """Test API components without starting the server."""
    
    print("Testing API Components (Offline)")
    print("=" * 50)
    
    try:
        from hushh_mcp.consent.token import issue_token, validate_token
        from hushh_mcp.constants import ConsentScope
        
        # Test 1: Create test tokens
        print("\n1. Creating test tokens...")
        user_id = "test_api_user"
        
        email_token = issue_token(
            user_id=user_id,
            agent_id="mailerpanda",
            scope=ConsentScope.VAULT_READ_EMAIL,
            expires_in_ms=3600000
        )
        
        write_token = issue_token(
            user_id=user_id,
            agent_id="mailerpanda",
            scope=ConsentScope.VAULT_WRITE_EMAIL,
            expires_in_ms=3600000
        )
        
        temp_token = issue_token(
            user_id=user_id,
            agent_id="mailerpanda",
            scope=ConsentScope.CUSTOM_TEMPORARY,
            expires_in_ms=3600000
        )
        
        print(f"Created 3 tokens successfully")
        
        # Test 2: Validate tokens
        print("\n2. Validating tokens...")
        
        is_valid, reason, parsed = validate_token(email_token.token, ConsentScope.VAULT_READ_EMAIL)
        print(f"Email token validation: {is_valid}")
        
        is_valid, reason, parsed = validate_token(write_token.token, ConsentScope.VAULT_WRITE_EMAIL)
        print(f"Write token validation: {is_valid}")
        
        is_valid, reason, parsed = validate_token(temp_token.token, ConsentScope.CUSTOM_TEMPORARY)
        print(f"Temp token validation: {is_valid}")
        
        # Test 3: Test agent instantiation
        print("\n3. Testing agent instantiation...")
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        agent = MassMailerAgent()
        print("MailerPanda agent created successfully")
        
        print("\nOffline API tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Offline API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_request_format():
    """Test API request format without actually sending requests."""
    
    print("\nTesting API Request Format")
    print("=" * 50)
    
    try:
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        # Create sample consent tokens
        user_id = "test_user_001"
        consent_tokens = {}
        
        scopes = [
            ConsentScope.VAULT_READ_EMAIL,
            ConsentScope.VAULT_WRITE_EMAIL,
            ConsentScope.VAULT_READ_FILE,
            ConsentScope.CUSTOM_TEMPORARY
        ]
        
        for i, scope in enumerate(scopes):
            token = issue_token(
                user_id=user_id,
                agent_id="mailerpanda",
                scope=scope,
                expires_in_ms=3600000
            )
            consent_tokens[f"token_{i}"] = token.token
        
        # Create sample API request
        api_request = {
            "user_id": user_id,
            "consent_tokens": consent_tokens,
            "parameters": {
                "user_input": "Send welcome email to test@example.com",
                "mode": "test"
            }
        }
        
        print(f"Sample API request format created")
        print(f"User ID: {api_request['user_id']}")
        print(f"Consent tokens: {len(api_request['consent_tokens'])}")
        print(f"Parameters: {list(api_request['parameters'].keys())}")
        
        print("API request format test completed successfully!")
        return True
        
    except Exception as e:
        print(f"API request format test failed: {e}")
        return False


if __name__ == "__main__":
    print("HushMCP Email Suite - API Integration Test")
    print("=" * 60)
    
    success1 = test_api_offline()
    success2 = test_api_request_format()
    
    if success1 and success2:
        print("\nAll API tests passed!")
        sys.exit(0)
    else:
        print("\nSome API tests failed!")
        sys.exit(1)
