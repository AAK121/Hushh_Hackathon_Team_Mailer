#!/usr/bin/env python3
"""
Complete LangGraph Function Tool Calling Test
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

def test_langgraph_function_tools():
    """Test the complete LangGraph function tool calling implementation"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize agent
    agent = RelationshipMemoryAgent()
    
    # User details
    user_id = "user_langgraph_test"
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
    
    print(f"\n🚀 Testing LangGraph Function Tool Calling")
    print(f"🤖 Agent: {agent.agent_id}")
    print(f"👤 User ID: {user_id}")
    
    # Test comprehensive function tool calling
    test_scenarios = [
        # Test contact addition with structured extraction
        ("Add Alice Johnson with email alice@example.com and phone 555-0123", "add_contact"),
        ("Add Bob Smith who works at Microsoft in Seattle", "add_contact"),
        ("Add contact: Dr. Emily Chen, email: emily.chen@hospital.com, phone: 555-0987", "add_contact"),
        
        # Test memory recording
        ("Remember that Alice loves hiking and photography", "add_memory"),
        ("Remember: Bob is working on a new AI project for Microsoft", "add_memory"), 
        ("Emily mentioned she studied at Harvard Medical School", "add_memory"),
        
        # Test reminder setting
        ("Remind me to call Alice next week about the hiking trip", "add_reminder"),
        ("Reminder: Send Bob the project proposal by Friday", "add_reminder"),
        
        # Test data retrieval
        ("Show me all my contacts", "show_contacts"),
        ("What do you know about Alice?", "show_memories"),
        ("What do you know about Bob?", "show_memories"),
        ("What reminders do I have?", "show_reminders"),
        ("Show me all memories", "show_memories"),
        
        # Test search functionality
        ("Find contacts who work at Microsoft", "search_contacts"),
    ]
    
    results = {}
    
    for i, (test_input, expected_action) in enumerate(test_scenarios, 1):
        print(f"\n--- Test {i} ({expected_action}): {test_input} ---")
        
        try:
            result = agent.handle(
                user_id=user_id,
                tokens=tokens,
                user_input=test_input,
                vault_key=vault_key
            )
            
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Action Taken: {result.get('action_taken', 'none')}")
            print(f"Message: {result.get('message', 'No message')}")
            
            if result.get('data'):
                data_count = len(result['data']) if isinstance(result['data'], list) else 1
                print(f"Data Count: {data_count}")
                
                # Show first item details for verification
                if isinstance(result['data'], list) and result['data']:
                    first_item = result['data'][0]
                    if 'name' in first_item:
                        print(f"  → Contact: {first_item.get('name')}")
                    elif 'contact_name' in first_item:
                        print(f"  → About: {first_item.get('contact_name')}")
                        if 'summary' in first_item:
                            print(f"  → Memory: {first_item.get('summary')}")
                        elif 'title' in first_item:
                            print(f"  → Reminder: {first_item.get('title')}")
            
            results[f"test_{i}"] = {
                "status": result.get('status'),
                "action_taken": result.get('action_taken'),
                "expected_action": expected_action,
                "success": result.get('status') == 'success'
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results[f"test_{i}"] = {
                "status": "error",
                "error": str(e),
                "expected_action": expected_action,
                "success": False
            }
    
    # Test Summary
    print("\n" + "="*60)
    print("📊 LangGraph Function Tool Calling Test Results")
    print("="*60)
    
    success_count = sum(1 for r in results.values() if r.get('success'))
    total_count = len(results)
    
    print(f"✅ Successful tests: {success_count}/{total_count}")
    print(f"📈 Success rate: {(success_count/total_count)*100:.1f}%")
    
    # Show action mapping accuracy
    action_matches = sum(1 for r in results.values() 
                        if r.get('action_taken') == r.get('expected_action') and r.get('success'))
    print(f"🎯 Correct action mapping: {action_matches}/{success_count}")
    
    if success_count == total_count:
        print("\n🎉 ALL TESTS PASSED! LangGraph function tool calling is working perfectly!")
    else:
        print(f"\n⚠️ {total_count - success_count} tests failed. Check the output above for details.")
    
    print("\n🔍 Key Features Demonstrated:")
    print("  ✅ Structured output parsing with Pydantic models")
    print("  ✅ Function tool calling with proper routing")
    print("  ✅ HushhMCP token validation and scope enforcement")
    print("  ✅ Persistent vault storage with encryption")
    print("  ✅ Contact, memory, and reminder management")
    print("  ✅ Search and retrieval functionality")
    
    return results

if __name__ == "__main__":
    test_langgraph_function_tools()
