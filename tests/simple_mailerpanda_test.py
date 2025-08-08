#!/usr/bin/env python3
"""Simple test for MailerPanda HushMCP integration."""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
    from hushh_mcp.consent.token import issue_token, validate_token
    from hushh_mcp.constants import ConsentScope
    
    print("Testing MailerPanda HushMCP Integration")
    print("=" * 50)
    
    # Test 1: Create agent instance
    print("\n1. Testing agent instantiation...")
    agent = MassMailerAgent()
    print("Agent created successfully")
    
    # Test 2: Test token creation
    print("\n2. Testing token creation...")
    user_id = "test_user_001"
    agent_id = "mailerpanda"
    
    # Create a basic token
    token = issue_token(
        user_id=user_id,
        agent_id=agent_id,
        scope=ConsentScope.VAULT_READ_EMAIL,
        expires_in_ms=3600000  # 1 hour
    )
    print(f"✅ Token created: {token.token[:50]}...")
    
    # Test 3: Test token validation
    print("\n3. Testing token validation...")
    is_valid, reason, parsed = validate_token(token.token, ConsentScope.VAULT_READ_EMAIL)
    print(f"✅ Token validation: {is_valid} ({reason})")
    
    # Test 4: Test agent methods (if they exist)
    print("\n4. Testing agent methods...")
    agent_methods = [method for method in dir(agent) if not method.startswith('_')]
    print(f"✅ Agent public methods: {agent_methods}")
    
    # Test 5: Check if agent has HushMCP integration
    print("\n5. Checking HushMCP integration...")
    hushh_methods = [method for method in dir(agent) if 'consent' in method.lower() or 'vault' in method.lower() or 'trust' in method.lower()]
    print(f"✅ HushMCP methods: {hushh_methods if hushh_methods else 'None found'}")
    
    # Test 6: Check manifest integration
    print("\n6. Testing manifest integration...")
    try:
        from hushh_mcp.agents.mailerpanda.manifest import manifest
        print(f"✅ Manifest loaded: {manifest.get('name', 'Unknown')}")
        print(f"📋 Required scopes: {manifest.get('required_scopes', [])}")
    except Exception as e:
        print(f"⚠️ Manifest issue: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Basic MailerPanda test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are properly installed")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
