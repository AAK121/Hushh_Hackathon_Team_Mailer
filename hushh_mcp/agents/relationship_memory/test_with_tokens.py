#!/usr/bin/env python3
"""
Test script for Relationship Memory Agent using proper HushhMCP tokens
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

def test_relationship_agent():
    """Test the relationship memory agent with proper consent tokens"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize agent
    agent = RelationshipMemoryAgent()
    
    # User details
    user_id = "user_test_123"
    vault_key = "e2d989c4d382c80beebbe58c6f07f94b42e554f691ab11738115a489350584b8"
    
    # Issue consent tokens for all required scopes
    tokens = {}
    for scope in agent.required_scopes:
        token_obj = issue_token(
            user_id=user_id,
            agent_id=agent.agent_id,
            scope=scope,
            expires_in_ms=24 * 60 * 60 * 1000  # 24 hours
        )
        tokens[scope.value] = token_obj.token
        print(f"✅ Issued token for scope: {scope.value}")
    
    print(f"\n🤖 Testing agent: {agent.agent_id}")
    print(f"👤 User ID: {user_id}")
    print(f"🔑 Vault key: {vault_key[:16]}...")
    print(f"📋 Required scopes: {[s.value for s in agent.required_scopes]}")
    
    # Test scenarios
    test_scenarios = [
        "I met Sarah today at the coffee shop. She's a software engineer at Google.",
        "Remember that John's birthday is next month",
        "What do you know about Sarah?",
        "Show me all my contacts",
        "What reminders do I have?"
    ]
    
    for i, test_input in enumerate(test_scenarios, 1):
        print(f"\n--- Test {i}: {test_input} ---")
        
        try:
            result = agent.handle(
                user_id=user_id,
                tokens=tokens,
                user_input=test_input,
                vault_key=vault_key
            )
            
            print(f"Status: {result.get('status', 'unknown')}")
            if result.get('message'):
                print(f"Message: {result['message']}")
            if result.get('data'):
                print(f"Data: {result['data']}")
            if result.get('details'):
                print(f"Details: {result['details']}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_relationship_agent()
