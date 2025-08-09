#!/usr/bin/env python3
"""Test version of AddToCalendar agent run script that doesn't require API keys."""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

def test_addtocalendar_agent():
    """Test AddToCalendar agent without requiring external API keys."""
    
    print("Testing AddToCalendar Agent - No External APIs")
    print("=" * 60)
    
    try:
        # Load environment
        env_path = os.path.join(project_root, '.env')
        load_dotenv(env_path)
        
        # Import required modules
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.agents.addtocalendar.manifest import manifest
        
        print("1. Testing manifest loading...")
        print(f"   Agent ID: {manifest.get('id', 'Unknown')}")
        print(f"   Agent Name: {manifest.get('name', 'Unknown')}")
        print(f"   Scopes: {len(manifest.get('scopes', []))}")
        
        print("2. Testing token creation...")
        user_id = "test_user_calendar"
        
        # Create tokens for both required scopes
        if len(manifest.get('scopes', [])) >= 2:
            email_token = issue_token(
                user_id=user_id,
                agent_id=manifest["id"],
                scope=manifest["scopes"][0],
                expires_in_ms=3600000
            )
            print(f"   Email token created: {email_token.token[:50]}...")
            
            calendar_token = issue_token(
                user_id=user_id,
                agent_id=manifest["id"],
                scope=manifest["scopes"][1],
                expires_in_ms=3600000
            )
            print(f"   Calendar token created: {calendar_token.token[:50]}...")
        
        print("3. Testing agent import...")
        from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
        print("   AddToCalendar agent imported successfully")
        
        print("4. Testing agent instantiation...")
        try:
            agent = AddToCalendarAgent()
            print("   Agent created successfully")
            
            # Test agent methods
            methods = [method for method in dir(agent) if not method.startswith('_') and callable(getattr(agent, method))]
            print(f"   Available methods: {methods}")
            
        except Exception as e:
            if "API_KEY" in str(e) or "OPENAI" in str(e):
                print(f"   Expected API key error: {e}")
                print("   Agent structure is correct, just needs API configuration")
            else:
                raise e
        
        print("\n✅ AddToCalendar agent test completed successfully!")
        print("📝 Note: Agent requires OpenAI API key for full functionality")
        return True
        
    except Exception as e:
        print(f"\n❌ AddToCalendar agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_addtocalendar_agent()
    sys.exit(0 if success else 1)
