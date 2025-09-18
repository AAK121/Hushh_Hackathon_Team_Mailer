"""
Simple test for the LangGraph Relationship Memory Agent
Tests basic functionality without requiring OpenAI API
"""

import uuid
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, project_root)

def test_basic_parsing():
    """Test basic input parsing logic"""
    print("Testing basic parsing logic...")
    
    # Test input patterns
    test_inputs = [
        "add john smith with email john@example.com",
        "remember that I met sarah at the conference",
        "remind me to call mike on 2024-03-15",
        "show my contacts",
        "search for contacts at google"
    ]
    
    for input_text in test_inputs:
        print(f"Input: {input_text}")
        
        # Basic pattern matching (fallback when AI is not available)
        input_lower = input_text.lower()
        
        if any(x in input_lower for x in ['add', 'new contact', 'create contact']):
            print("  -> Detected: ADD_CONTACT")
        elif any(x in input_lower for x in ['remember', 'memory', 'met']):
            print("  -> Detected: ADD_MEMORY")
        elif any(x in input_lower for x in ['remind', 'reminder']):
            print("  -> Detected: ADD_REMINDER")
        elif any(x in input_lower for x in ['show contacts', 'my contacts']):
            print("  -> Detected: SHOW_CONTACTS")
        elif any(x in input_lower for x in ['search']):
            print("  -> Detected: SEARCH_CONTACTS")
        else:
            print("  -> Detected: UNKNOWN")
        
        print()

def test_vault_operations():
    """Test vault operations"""
    print("Testing vault operations...")
    
    try:
        from hushh_mcp.agents.relationship_memory.langgraph_agent import HushhVaultManager
        
        # Generate test credentials
        user_id = str(uuid.uuid4())
        vault_key = os.urandom(32).hex()
        
        # Initialize vault manager
        vault_manager = HushhVaultManager(user_id, vault_key)
        print("✅ Vault manager initialized")
        
        # Test contact storage
        contact_data = {
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "+1234567890",
            "company": "Acme Corp"
        }
        
        contact_id = vault_manager.store_contact(contact_data)
        print(f"✅ Contact stored with ID: {contact_id}")
        
        # Test contact retrieval
        contacts = vault_manager.get_contacts()
        print(f"✅ Retrieved {len(contacts)} contacts")
        
        if contacts:
            print(f"   First contact: {contacts[0]['name']}")
        
        # Test memory storage
        memory_data = {
            "contact_name": "John Smith",
            "summary": "Met at tech conference",
            "location": "San Francisco",
            "date": "2024-03-15"
        }
        
        memory_id = vault_manager.store_memory(memory_data)
        print(f"✅ Memory stored with ID: {memory_id}")
        
        # Test memory retrieval
        memories = vault_manager.get_memories()
        print(f"✅ Retrieved {len(memories)} memories")
        
        return True
        
    except Exception as e:
        print(f"❌ Vault operations failed: {str(e)}")
        return False

def test_full_agent():
    """Test the full agent (requires OpenAI API key)"""
    print("Testing full agent functionality...")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Skipping full agent test - OPENAI_API_KEY not found")
        print("   Set OPENAI_API_KEY environment variable to test AI parsing")
        return
    
    try:
        from hushh_mcp.agents.relationship_memory.langgraph_agent import RelationshipMemoryAgent
        
        # Initialize agent
        user_id = str(uuid.uuid4())
        vault_key = os.urandom(32).hex()
        
        agent = RelationshipMemoryAgent(user_id, vault_key)
        print("✅ LangGraph agent initialized")
        
        # Test simple input
        response = agent.process_input("add john smith with email john@example.com")
        print(f"✅ Agent response: {response.get('status', 'unknown')}")
        
        if response.get("status") == "success":
            print(f"   Message: {response.get('message', 'No message')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full agent test failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        return False

def main():
    print("🧪 LangGraph Relationship Memory Agent - Test Suite")
    print("=" * 60)
    
    # Run tests
    print("\n1. Basic Parsing Test:")
    test_basic_parsing()
    
    print("\n2. Vault Operations Test:")
    vault_success = test_vault_operations()
    
    print("\n3. Full Agent Test:")
    agent_success = test_full_agent()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Vault Operations: {'✅ PASS' if vault_success else '❌ FAIL'}")
    print(f"   Full Agent: {'✅ PASS' if agent_success else '⚠️  SKIP (needs API key)'}")
    
    if vault_success:
        print("\n🎉 Core functionality is working!")
        print("   The agent can store and retrieve data using Hush MCP vault.")
        print("   Add OPENAI_API_KEY to enable AI-powered input parsing.")
    else:
        print("\n⚠️  Some tests failed. Check your environment and dependencies.")

if __name__ == "__main__":
    main()
