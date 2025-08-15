#!/usr/bin/env python3
"""
Comprehensive test script for Relationship Memory Agent with proper token validation
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from hushh_mcp.consent.token import issue_token, validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgent

def test_token_validation():
    """Test token validation independently"""
    print("🔐 Testing token validation...")
    
    user_id = "user_test_456"
    agent_id = "relationship_memory"
    
    # Issue a token
    token_obj = issue_token(
        user_id=user_id,
        agent_id=agent_id,
        scope=ConsentScope.VAULT_READ_CONTACTS,
        expires_in_ms=24 * 60 * 60 * 1000  # 24 hours
    )
    
    print(f"✅ Issued token: {token_obj.token[:50]}...")
    
    # Validate the token
    valid, reason, parsed = validate_token(
        token_obj.token,
        expected_scope=ConsentScope.VAULT_READ_CONTACTS
    )
    
    print(f"Token validation: {valid}, Reason: {reason}")
    if parsed:
        print(f"Parsed user_id: {parsed.user_id}, agent_id: {parsed.agent_id}")
    
    return token_obj.token

def test_comprehensive_agent_functionality():
    """Test comprehensive agent functionality with data persistence"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize agent
    agent = RelationshipMemoryAgent()
    
    # User details
    user_id = "user_comprehensive_test"
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
    
    print(f"\n🤖 Testing comprehensive functionality for agent: {agent.agent_id}")
    
    # Test data creation and retrieval
    test_scenarios = [
        # Add data
        ("Add contact: Alice Johnson, email: alice@example.com, phone: 555-0123", "contact"),
        ("Add contact: Bob Smith, works at Microsoft, lives in Seattle", "contact"), 
        ("Remember: Alice loves hiking and photography", "memory"),
        ("Remember: Bob is working on a new AI project", "memory"),
        ("Reminder: Call Alice next week about the hiking trip", "reminder"),
        ("Reminder: Send Bob the project proposal by Friday", "reminder"),
        
        # Retrieve data
        ("Show me all my contacts", "query"),
        ("What do you know about Alice?", "query"),
        ("What do you know about Bob?", "query"),
        ("What reminders do I have?", "query"),
        ("Show me all memories", "query"),
    ]
    
    results = {}
    
    for i, (test_input, category) in enumerate(test_scenarios, 1):
        print(f"\n--- Test {i} ({category}): {test_input} ---")
        
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
            
            results[f"test_{i}"] = result
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results[f"test_{i}"] = {"status": "error", "error": str(e)}
    
    # Summary
    print("\n📊 Test Summary:")
    success_count = sum(1 for r in results.values() if r.get('status') == 'success')
    total_count = len(results)
    print(f"✅ Successful tests: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All tests passed! The agent is working correctly with HushhMCP tokens.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return results

if __name__ == "__main__":
    print("🚀 Starting comprehensive HushhMCP token tests...\n")
    
    # Test token validation
    test_token = test_token_validation()
    
    print("\n" + "="*50 + "\n")
    
    # Test agent functionality
    results = test_comprehensive_agent_functionality()
    
    print("\n✅ All tests completed!")
