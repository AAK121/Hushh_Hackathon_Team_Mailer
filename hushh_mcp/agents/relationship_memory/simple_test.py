#!/usr/bin/env python3
"""
Simple Test Script - Test the LangGraph agent with a single command
Usage: python simple_test.py "Your command here"
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

def test_single_command(command):
    """Test a single command with the agent"""
    
    print(f"🧪 Testing: {command}")
    print("-" * 50)
    
    # Setup
    load_dotenv()
    agent = RelationshipMemoryAgent()
    user_id = "user_simple_test"
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
    
    # Test the command
    try:
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input=command,
            vault_key=vault_key
        )
        
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Action: {result.get('action_taken', 'none')}")
        print(f"Message: {result.get('message', 'No message')}")
        
        if result.get('data'):
            data = result['data']
            if isinstance(data, list):
                print(f"Data: {len(data)} items returned")
                for i, item in enumerate(data[:2]):  # Show first 2 items
                    if 'name' in item:
                        print(f"  - Contact: {item.get('name')}")
                    elif 'contact_name' in item:
                        summary = item.get('summary', item.get('title', ''))
                        print(f"  - {item.get('contact_name')}: {summary}")
            else:
                print(f"Data: {data}")
        
        return result
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        test_single_command(command)
    else:
        print("🎯 Simple Test Examples:")
        print("python simple_test.py \"Add John Smith with email john@example.com\"")
        print("python simple_test.py \"Remember that John loves hiking\"")
        print("python simple_test.py \"Show me all my contacts\"")
        print("python simple_test.py \"What do you know about John?\"")
        print("\nOr run without arguments to see this help.")
