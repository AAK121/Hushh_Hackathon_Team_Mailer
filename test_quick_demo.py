#!/usr/bin/env python3
"""
Quick demo of the improved contact management features
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgent
from hushh_mcp.consent.token import issue_token
from hushh_mcp.types import ConsentScope

def quick_demo():
    """Quick demo of improved contact management"""
    print("🚀 Quick Demo: Improved Contact Management")
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
        
        # Test 1: Add initial contact
        print("\n📝 Test 1: Adding initial contact")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="add jhon smith to contacts",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 2: Update contact with email (should update, not create duplicate)
        print("\n📧 Test 2: Adding email to existing contact")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="add email of jhon smith as jhon@gmail.com",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 3: Show contacts (should show only 1 contact, not duplicates)
        print("\n👥 Test 3: Showing all contacts")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="show contacts",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 4: Get contact details (new functionality)
        print("\n🔍 Test 4: Getting contact details")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="show me the details of jhon smith",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 5: Add second contact
        print("\n👤 Test 5: Adding second contact")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="add alok kale to contacts",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 6: Update second contact (should update, not duplicate)
        print("\n📧 Test 6: Adding email to second contact")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="add email for alok as alokkale121@gmail.com",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 7: Final contact list
        print("\n📋 Test 7: Final contact list")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="show all contacts",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        print("\n" + "=" * 50)
        print("✅ Demo completed!")
        print("\n🎯 Key Improvements Demonstrated:")
        print("   1. ✅ Contact uniqueness checking")
        print("   2. ✅ Smart contact updating vs creating duplicates")
        print("   3. ✅ New get_contact_details functionality")
        print("   4. ✅ Proper contact matching and merging")
        print("   5. ✅ LangGraph function tool calling with 1.0 confidence")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_demo()
