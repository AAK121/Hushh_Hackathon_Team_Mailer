#!/usr/bin/env python3
"""
Direct test script to bypass LLM parsing and test contact retrieval directly
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgent
from hushh_mcp.agents.relationship_memory.utils.vault_manager import VaultManager

def test_direct_action_bypass():
    """Test agent by directly calling action methods, bypassing LLM parsing"""
    
    print("🧪 Testing direct action bypass...")
    
    load_dotenv()
    
    # Initialize agent
    agent = RelationshipMemoryAgent()
    user_id = "direct_test_user"
    vault_key = "e2d989c4d382c80beebbe58c6f07f94b42e554f691ab11738115a489350584b8"
    
    # Issue tokens
    tokens = {}
    for scope in agent.required_scopes:
        token_obj = issue_token(
            user_id=user_id,
            agent_id=agent.agent_id,
            scope=scope,
            expires_in_ms=24 * 60 * 60 * 1000
        )
        tokens[scope.value] = token_obj.token
    
    # Initialize vault manager directly
    vault_manager = VaultManager(user_id=user_id, vault_key=vault_key)
    
    print("1. Adding test contacts directly...")
    
    # Add test contacts using vault manager directly
    test_contacts = [
        {"name": "Direct Test Alice", "email": "alice@direct.com", "phone": "555-0001"},
        {"name": "Direct Test Bob", "email": "bob@direct.com", "phone": "555-0002"},
        {"name": "Direct Test Carol", "email": "carol@direct.com", "phone": "555-0003"}
    ]
    
    for contact in test_contacts:
        result = vault_manager.store_contact(contact)
        print(f"  ✅ Stored: {contact['name']}")
    
    print("\n2. Retrieving contacts directly from vault manager...")
    stored_contacts = vault_manager.get_all_contacts()
    print(f"  📋 Found {len(stored_contacts)} contacts:")
    for contact in stored_contacts:
        print(f"    - {contact.get('name')} ({contact.get('email')})")
    
    print("\n3. Testing agent _show_contacts method directly...")
    result = agent._show_contacts(vault_manager)
    print(f"  Agent result: {result}")
    
    print("\n4. Testing agent handle with direct action override...")
    
    # Monkey patch the _process_input method to return specific actions
    def mock_process_input(user_input, vault_manager, llm):
        if "show contacts" in user_input.lower():
            return agent._show_contacts(vault_manager)
        elif "add contact" in user_input.lower():
            # Extract name from input
            if "Test David" in user_input:
                contact_data = {
                    "name": "Test David",
                    "email": "david@test.com",
                    "phone": "555-0004"
                }
                return agent._add_contact(contact_data, vault_manager)
        return {"status": "error", "message": "Unknown action"}
    
    # Temporarily replace the method
    original_method = agent._process_input
    agent._process_input = mock_process_input
    
    # Test adding contact
    print("  Testing add contact...")
    result = agent.handle(
        user_id=user_id,
        tokens=tokens,
        user_input="Add contact: Test David",
        vault_key=vault_key
    )
    print(f"    Add result: {result.get('status')} - {result.get('message')}")
    
    # Test showing contacts
    print("  Testing show contacts...")
    result = agent.handle(
        user_id=user_id,
        tokens=tokens,
        user_input="Show contacts",
        vault_key=vault_key
    )
    print(f"    Show result: {result.get('status')} - {result.get('message')}")
    if result.get('contacts'):
        print(f"    Found {len(result['contacts'])} contacts in agent response")
    
    # Restore original method
    agent._process_input = original_method
    
    print("\n5. Final vault verification...")
    final_contacts = vault_manager.get_all_contacts()
    print(f"  📋 Final count: {len(final_contacts)} contacts in vault")
    
    return len(final_contacts)

def test_comprehensive_user_flow():
    """Test with a user that already has data to see if retrieval works"""
    
    print("\n🔍 Testing with existing user data...")
    
    # Use a user ID that we know has data from previous tests
    user_id = "user_comprehensive_test"
    vault_key = "e2d989c4d382c80beebbe58c6f07f94b42e554f691ab11738115a489350584b8"
    
    vault_manager = VaultManager(user_id=user_id, vault_key=vault_key)
    
    print("Checking existing data...")
    existing_contacts = vault_manager.get_all_contacts()
    existing_memories = vault_manager.get_all_memories()
    existing_reminders = vault_manager.get_all_reminders()
    
    print(f"  Contacts: {len(existing_contacts)}")
    print(f"  Memories: {len(existing_memories)}")
    print(f"  Reminders: {len(existing_reminders)}")
    
    if existing_contacts:
        print("  Contact details:")
        for contact in existing_contacts:
            print(f"    - {contact.get('name', 'No name')} | {contact.get('email', 'No email')}")
    
    return len(existing_contacts), len(existing_memories), len(existing_reminders)

if __name__ == "__main__":
    print("🚀 Direct action bypass test...\n")
    
    # Test direct vault operations
    contact_count = test_direct_action_bypass()
    
    # Test with existing user data
    existing_counts = test_comprehensive_user_flow()
    
    print(f"\n📊 Summary:")
    print(f"  New test user contacts: {contact_count}")
    print(f"  Existing user data: {existing_counts[0]} contacts, {existing_counts[1]} memories, {existing_counts[2]} reminders")
    
    if contact_count > 0 and existing_counts[0] > 0:
        print("✅ Data persistence is working correctly!")
        print("❌ The issue is likely in LLM parsing when API quota is exceeded")
    else:
        print("❌ There may be an issue with data persistence")
    
    print("\n✅ Direct test completed!")
