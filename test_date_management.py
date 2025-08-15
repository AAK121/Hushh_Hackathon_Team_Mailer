#!/usr/bin/env python3
"""
Demo of the new date management features for contacts
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgent
from hushh_mcp.consent.token import issue_token
from hushh_mcp.types import ConsentScope

def test_date_management():
    """Test the new date management features"""
    print("🎉 Testing Date Management Features")
    print("=" * 50)
    
    try:
        # Setup
        agent = RelationshipMemoryAgent()
        user_id = "demo_user"
        vault_key = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
        
        # Issue tokens
        tokens = {}
        for scope in agent.required_scopes:
            token = issue_token(
                user_id=user_id,
                agent_id=agent.agent_id,
                scope=scope,
                expires_in_ms=3600000
            )
            tokens[scope.value] = token.token
        
        print("✅ Agent setup complete")
        
        # Test 1: Add a contact
        print("\n👤 Test 1: Adding a contact")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="add Om to contacts",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 2: Add birthday for Om
        print("\n🎂 Test 2: Adding Om's birthday")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="Om's birthday is on 12 nov",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 3: Add another contact
        print("\n👤 Test 3: Adding another contact")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="add John Smith to contacts",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 4: Add anniversary for John
        print("\n💍 Test 4: Adding John's anniversary")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="add anniversary for John on 25 december 2020",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 5: Add another date close to current date
        print("\n🎓 Test 5: Adding a graduation date")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="add graduation for Om on 20 august",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 6: Get contact details (should show dates)
        print("\n🔍 Test 6: Getting Om's contact details")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="show me the details of Om",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 7: Show upcoming dates
        print("\n📅 Test 7: Showing upcoming important dates")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="show upcoming important dates",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 8: Alternative query for upcoming dates
        print("\n🎈 Test 8: Asking about birthdays coming up")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="any birthdays coming up?",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        print("\n" + "=" * 50)
        print("✅ Date Management Demo completed!")
        print("\n🎯 New Features Demonstrated:")
        print("   1. ✅ Adding important dates (birthday, anniversary, etc.)")
        print("   2. ✅ Date format parsing (DD-MM)")
        print("   3. ✅ Contact details showing dates")
        print("   4. ✅ Upcoming dates calculation")
        print("   5. ✅ Smart date queries and responses")
        print("   6. ✅ Multiple date types per contact")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_date_management()
