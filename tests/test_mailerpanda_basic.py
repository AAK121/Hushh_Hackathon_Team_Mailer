#!/usr/bin/env python3
"""
Fixed and simplified test for MailerPanda integration.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_mailerpanda_basic():
    """Test basic MailerPanda functionality."""
    
    print("Testing MailerPanda Basic Integration")
    print("=" * 50)
    
    try:
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        from hushh_mcp.consent.token import issue_token, validate_token
        from hushh_mcp.constants import ConsentScope
        
        print("1. Testing agent instantiation...")
        agent = MassMailerAgent()
        print("   Agent created successfully")
        
        print("2. Testing token creation...")
        user_id = "test_user_001"
        agent_id = "mailerpanda"
        
        # Create a basic token
        token = issue_token(
            user_id=user_id,
            agent_id=agent_id,
            scope=ConsentScope.VAULT_READ_EMAIL,
            expires_in_ms=3600000  # 1 hour
        )
        print(f"   Token created: {token.token[:50]}...")
        
        print("3. Testing token validation...")
        is_valid, reason, parsed = validate_token(token.token, ConsentScope.VAULT_READ_EMAIL)
        print(f"   Token validation: {is_valid} ({reason})")
        
        print("4. Testing agent methods...")
        agent_methods = [method for method in dir(agent) if not method.startswith('_')]
        print(f"   Agent public methods: {agent_methods}")
        
        print("5. Checking HushMCP integration...")
        hushh_methods = [method for method in dir(agent) if 'consent' in method.lower() or 'vault' in method.lower() or 'trust' in method.lower()]
        print(f"   HushMCP methods: {hushh_methods if hushh_methods else 'None found'}")
        
        print("6. Testing manifest integration...")
        try:
            from hushh_mcp.agents.mailerpanda.manifest import manifest
            print(f"   Manifest loaded: {manifest.get('name', 'Unknown')}")
            print(f"   Required scopes: {list(manifest.get('required_scopes', {}).keys())}")
        except Exception as e:
            print(f"   Manifest issue: {e}")
        
        print("\nTest completed successfully!")
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_mailerpanda_basic()
    sys.exit(0 if success else 1)
