#!/usr/bin/env python3
"""
Test the improved contact management with uniqueness checks and contact details
"""

import sys
import os

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgent
from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope

def setup_agent_and_tokens():
    """Setup agent and issue required tokens"""
    try:
        agent = RelationshipMemoryAgent()
        
        # Issue tokens for all required scopes
        tokens = {}
        for scope in agent.required_scopes:
            token = issue_token(
                user_id="test_user_improved",
                agent_id=agent.agent_id,
                scope=scope,
                expires_in_ms=3600000  # 1 hour in milliseconds
            )
            tokens[scope.value] = token.token
        
        vault_key = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
        
        return agent, tokens, "test_user_improved", vault_key
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return None, None, None, None

def test_contact_improvements():
    """Test the improved contact management features"""
    print("🔧 Testing Improved Contact Management")
    print("=" * 50)
    
    agent, tokens, user_id, vault_key = setup_agent_and_tokens()
    if not agent:
        print("❌ Failed to setup agent")
        return
    
    # Test scenarios
    test_cases = [
        # 1. Add initial contact
        {
            "input": "add jhon smith to contacts",
            "description": "Add initial contact"
        },
        # 2. Add email for existing contact (should update, not create new)
        {
            "input": "add email of jhon smith as jhon@gmail.com",
            "description": "Add email to existing contact (should update)"
        },
        # 3. Show contacts to verify no duplicates
        {
            "input": "show contacts",
            "description": "Show all contacts (check for duplicates)"
        },
        # 4. Get contact details
        {
            "input": "show me the details of jhon smith",
            "description": "Get detailed contact information"
        },
        # 5. Add another contact
        {
            "input": "add alok kale to contacts",
            "description": "Add second contact"
        },
        # 6. Update the second contact
        {
            "input": "add email for alok as alokkale121@gmail.com",
            "description": "Add email to second contact"
        },
        # 7. Show all contacts again
        {
            "input": "show all contacts",
            "description": "Show all contacts after updates"
        },
        # 8. Get details of second contact
        {
            "input": "tell me about alok kale",
            "description": "Get details of second contact"
        },
        # 9. Try to add contact with similar name (should ask for clarification)
        {
            "input": "add Alok to contacts",
            "description": "Try to add contact with similar name"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['description']}")
        print(f"🗣️  Input: {test_case['input']}")
        
        try:
            result = agent.handle(
                user_id=user_id,
                tokens=tokens,
                user_input=test_case['input'],
                vault_key=vault_key
            )
            
            print(f"📊 Status: {result['status']}")
            print(f"💬 Response: {result['message']}")
            
            if result.get('data'):
                print(f"📄 Data ({len(result['data'])} items):")
                for j, item in enumerate(result['data'][:5], 1):  # Show first 5 items
                    if isinstance(item, dict):
                        if 'name' in item:
                            email_part = f" ({item['email']})" if item.get('email') else ""
                            print(f"  {j}. 👤 {item['name']}{email_part}")
                        else:
                            print(f"  {j}. {item}")
                    else:
                        print(f"  {j}. {item}")
                
                if len(result['data']) > 5:
                    print(f"  ... and {len(result['data']) - 5} more items")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("-" * 40)

def test_specific_scenario():
    """Test the specific scenario from user feedback"""
    print("\n🎯 Testing Specific User Scenario")
    print("=" * 50)
    
    agent, tokens, user_id, vault_key = setup_agent_and_tokens()
    if not agent:
        print("❌ Failed to setup agent")
        return
    
    # Replicate the exact user scenario
    commands = [
        "add jhon smith to contacts",
        "add email of jhon smith as jhon@gmail.com",
        "show me the details of jhon smith",
        "show contacts",
        "add alok kale to contacts", 
        "add chandresh to contacts",
        "add email for alok as alokkale121@gmail.com",
        "show contacts"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n▶️  Command {i}: {cmd}")
        
        try:
            result = agent.handle(
                user_id=user_id,
                tokens=tokens,
                user_input=cmd,
                vault_key=vault_key
            )
            
            print(f"📊 Status: {result['status']}")
            print(f"💬 Response: {result['message']}")
            
        except Exception as e:
            print(f"❌ Command failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Improved Contact Management Tests")
    
    try:
        test_contact_improvements()
        test_specific_scenario()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
