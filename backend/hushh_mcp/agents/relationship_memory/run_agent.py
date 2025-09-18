# hushh_mcp/agents/relationship_memory/run_agent.py

"""
Standalone script to run the Relationship Memory Agent with proper token issuance.
This script demonstrates how to issue consent tokens and execute the agent.
Following HushhMCP docs pattern.
"""

import os
import sys
from dotenv import load_dotenv

# --- Dynamic Path Configuration ---
# This ensures the script can find the 'hushh_mcp' package from its new location.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --------------------------------

from hushh_mcp.consent.token import issue_token
from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgent
from hushh_mcp.agents.relationship_memory.manifest import manifest

def run():
    """Issues consent tokens and executes the Relationship Memory Agent."""
    # Load .env file from the project root directory
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    
    print("🚀 Initializing Relationship Memory Agent...")
    print("=" * 60)
    
    user_id = "demo_user_relationship_001"
    
    # 1. Issue tokens for all required permissions
    print("📋 Issuing consent tokens...")
    
    tokens = {}
    
    try:
        for scope in manifest["scopes"]:
            token = issue_token(
                user_id=user_id,
                agent_id=manifest["id"],
                scope=scope,
                expires_in_ms=3600 * 1000  # 1 hour
            )
            tokens[scope.value] = token.token
            print(f"✅ Token issued for scope: {scope.value}")
    
    except Exception as e:
        print(f"❌ Error issuing tokens: {e}")
        return
    
    print(f"\n🎯 Total tokens issued: {len(tokens)}")
    
    # 2. Initialize and run the agent
    try:
        print("\n🤖 Initializing agent...")
        agent = RelationshipMemoryAgent()
        
        # Interactive mode
        print("\n📝 Relationship Memory Agent is ready!")
        print("Example commands:")
        print("• add john smith with email john@example.com")
        print("• remember that I met sarah at the conference")
        print("• remind me to call mike on 2024-03-15")
        print("• show my contacts")
        print("• search for contacts at google")
        print("\nType 'quit' to exit")
        
        while True:
            try:
                user_input = input("\n❓ What would you like to do? > ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Process the request
                result = agent.handle(user_id, tokens, user_input)
                
                # Display result
                status = result.get('status', 'unknown')
                message = result.get('message', 'No message')
                
                if status == 'success':
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

def run_demo():
    """Run a quick demo with predefined commands"""
    print("🚀 Running Relationship Memory Agent Demo...")
    print("=" * 50)
    
    # Load environment
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    
    user_id = "demo_user_quick_test"
    
    # Issue tokens
    tokens = {}
    try:
        for scope in manifest["scopes"]:
            token = issue_token(
                user_id=user_id,
                agent_id=manifest["id"],
                scope=scope,
                expires_in_ms=3600 * 1000
            )
            tokens[scope.value] = token.token
            
    except Exception as e:
        print(f"❌ Error issuing tokens: {e}")
        return
    
    # Initialize agent
    agent = RelationshipMemoryAgent()
    
    # Use consistent vault key for demo
    vault_key = "1b0166345f10bd91dbd7da0f6f92384229a9c6d0858ba08b5a1e45a6af388134"  # 32-byte hex key
    
    # Test commands
    test_commands = [
        "add alok as a contact with email 23b2223@iitb.ac.in",
        "add sarah with phone 9876543210",
        "show my contacts", 
        "remember that I met alok at the conference",
        "remind me to call sarah on 2024-03-20"
    ]
    
    for command in test_commands:
        print(f"\n🔍 Testing: {command}")
        try:
            result = agent.handle(
                user_id=user_id,
                tokens=tokens,
                user_input=command,
                vault_key=vault_key  # Use consistent vault key
            )
            print(f"📋 Status: {result.get('status', 'unknown')}")
            print(f"📋 Message: {result.get('message', 'No message')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    # Check if demo mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo()
    else:
        run()
