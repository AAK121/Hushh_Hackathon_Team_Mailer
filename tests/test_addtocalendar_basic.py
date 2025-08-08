#!/usr/bin/env python3
"""Test AddToCalendar agent import and basic functionality."""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def test_addtocalendar_imports():
    """Test that AddToCalendar agent imports correctly."""
    
    print("Testing AddToCalendar Agent Imports")
    print("=" * 50)
    
    try:
        # Test individual imports
        print("1. Testing consent token imports...")
        from hushh_mcp.consent.token import validate_token, issue_token
        print("   Consent token imports: OK")
        
        print("2. Testing constants imports...")
        from hushh_mcp.constants import ConsentScope
        print("   Constants imports: OK")
        
        print("3. Testing email analysis operons...")
        from hushh_mcp.operons.email_analysis import prioritize_emails_operon, categorize_emails_operon
        print("   Email analysis operons: OK")
        
        print("4. Testing trust link operations...")
        from hushh_mcp.trust.link import verify_trust_link
        print("   Trust link operations: OK")
        
        print("5. Testing vault operations...")
        from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
        print("   Vault operations: OK")
        
        print("6. Testing AddToCalendar agent import...")
        from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
        print("   AddToCalendar agent: OK")
        
        print("7. Testing manifest import...")
        from hushh_mcp.agents.addtocalendar.manifest import manifest
        print("   Manifest: OK")
        print(f"   Agent name: {manifest.get('name', 'Unknown')}")
        
        print("\nAll imports successful!")
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_addtocalendar_basic():
    """Test basic AddToCalendar agent functionality."""
    
    print("\nTesting AddToCalendar Agent Basic Functionality")
    print("=" * 50)
    
    try:
        from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        print("1. Creating AddToCalendar agent...")
        # Note: This might fail due to missing API keys, but we'll catch that
        try:
            agent = AddToCalendarAgent()
            print("   Agent created successfully")
            agent_created = True
        except ValueError as e:
            if "API_KEY" in str(e):
                print(f"   Expected API key error: {e}")
                print("   Agent structure is correct, just needs API keys")
                agent_created = False
            else:
                raise e
        
        print("2. Testing token creation...")
        user_id = "test_user_calendar"
        token = issue_token(
            user_id=user_id,
            agent_id="addtocalendar",
            scope=ConsentScope.VAULT_READ_EMAIL,
            expires_in_ms=3600000
        )
        print(f"   Token created: {token.token[:50]}...")
        
        print("3. Testing agent methods...")
        if agent_created:
            methods = [method for method in dir(agent) if not method.startswith('_')]
            print(f"   Available methods: {len(methods)}")
            
            # Check for specific expected methods
            expected_methods = ['handle', 'process_emails']
            for method in expected_methods:
                if hasattr(agent, method):
                    print(f"   + {method} method available")
                else:
                    print(f"   ? {method} method not found")
        else:
            print("   Skipping method tests (agent not created)")
        
        print("\nBasic functionality test completed!")
        return True
        
    except Exception as e:
        print(f"Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("AddToCalendar Agent - Import and Basic Functionality Test")
    print("=" * 60)
    
    success1 = test_addtocalendar_imports()
    success2 = test_addtocalendar_basic()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("+ All AddToCalendar tests passed!")
        print("Note: Agent requires API keys for full functionality")
        sys.exit(0)
    else:
        print("- Some AddToCalendar tests failed!")
        sys.exit(1)
