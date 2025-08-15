#!/usr/bin/env python3
"""
Demo showing the memory storage format and structure
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgent
from hushh_mcp.consent.token import issue_token
from hushh_mcp.types import ConsentScope

def test_memory_format():
    """Test and display the memory storage format"""
    print("🧠 Memory Storage Format Demo")
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
        
        # Test 1: Add a contact first
        print("\n👤 Step 1: Adding a contact")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="add Sarah Johnson to contacts",
            vault_key=vault_key
        )
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 2: Add different types of memories
        print("\n🧠 Step 2: Adding various memories")
        
        memory_tests = [
            "Remember that Sarah loves hiking in the mountains",
            "Sarah mentioned she studied computer science at Stanford",
            "Met Sarah at the coffee shop on 5th street yesterday",
            "Sarah is working on a machine learning project",
            "Remember Sarah has a dog named Max"
        ]
        
        for i, memory_input in enumerate(memory_tests, 1):
            print(f"\n   Memory {i}: {memory_input}")
            result = agent.handle(
                user_id=user_id,
                tokens=tokens,
                user_input=memory_input,
                vault_key=vault_key
            )
            print(f"   Action: {result.get('action_taken', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            
            # Show the parsed memory data if available
            if result.get('result_data'):
                data = result.get('result_data', [{}])[0]
                print(f"   Memory ID: {data.get('memory_id', 'N/A')}")
        
        # Test 3: Show all memories to see the storage format
        print("\n📋 Step 3: Showing all memories for Sarah")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="show me all memories about Sarah",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 4: Show contact details (includes memories)
        print("\n🔍 Step 4: Getting Sarah's complete details")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="show me Sarah's details",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Message: {result.get('message', 'No message')}")
        
        # Test 5: Add memory with specific location and tags
        print("\n📍 Step 5: Adding memory with location and context")
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input="Remember Sarah and I discussed AI ethics at the tech conference in San Francisco",
            vault_key=vault_key
        )
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        print(f"   Status: {result.get('status', 'unknown')}")
        
        print("\n" + "=" * 50)
        print("📊 MEMORY STORAGE FORMAT ANALYSIS:")
        print("=" * 50)
        
        print("\n🏗️  MEMORY DATA STRUCTURE:")
        print("```json")
        print("{")
        print('  "contact_name": "Sarah Johnson",')
        print('  "summary": "Sarah loves hiking in the mountains",')
        print('  "location": null,  // Optional field')
        print('  "date": null,      // Optional field') 
        print('  "tags": [],        // List of tags for categorization')
        print('  "id": "memory_1692123456"  // Auto-generated timestamp ID')
        print("}")
        print("```")
        
        print("\n🔧 STORAGE MECHANISM:")
        print("• Stored in encrypted vault using AES-256-GCM")
        print("• Each memory has unique ID: memory_<timestamp>")
        print("• Linked to contact via contact_name field")
        print("• Supports optional location and date metadata")
        print("• Tags system for categorization and retrieval")
        print("• Full HushhMCP compliance with consent scopes")
        
        print("\n🎯 RETRIEVAL METHODS:")
        print("• By contact name: get_memories_for_contact()")
        print("• All memories: get_all_memories()")
        print("• Integrated in contact details view")
        print("• Search and filter capabilities")
        
        print("\n📝 SUPPORTED MEMORY TYPES:")
        print("• Personal interactions and conversations")
        print("• Professional context (work, projects)")
        print("• Preferences and interests")
        print("• Educational background")
        print("• Location-based memories")
        print("• Any contextual information about the person")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_format()
