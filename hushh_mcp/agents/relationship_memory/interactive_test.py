#!/usr/bin/env python3
"""
Interactive Test Script for LangGraph Relationship Memory Agent
Run this to test the agent interactively with your own inputs!
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

def setup_agent_and_tokens():
    """Set up the agent and issue all required tokens"""
    print("🚀 Setting up LangGraph Relationship Memory Agent...")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize agent
    agent = RelationshipMemoryAgent()
    
    # User details
    user_id = "user_interactive_test"
    vault_key = "e2d989c4d382c80beebbe58c6f07f94b42e554f691ab11738115a489350584b8"
    
    # Issue consent tokens for all required scopes
    tokens = {}
    print("\n🔐 Issuing consent tokens...")
    for scope in agent.required_scopes:
        token_obj = issue_token(
            user_id=user_id,
            agent_id=agent.agent_id,
            scope=scope,
            expires_in_ms=24 * 60 * 60 * 1000  # 24 hours
        )
        tokens[scope.value] = token_obj.token
        print(f"  ✅ {scope.value}")
    
    print(f"\n🤖 Agent ID: {agent.agent_id}")
    print(f"👤 User ID: {user_id}")
    print(f"🔑 Vault key: {vault_key[:16]}...")
    
    return agent, user_id, vault_key, tokens

def print_help():
    """Print help information about available commands"""
    print("\n" + "="*60)
    print("📚 HELP - Available Commands:")
    print("="*60)
    print("📋 CONTACT MANAGEMENT:")
    print("  • 'Add John Smith with email john@example.com'")
    print("  • 'Add contact: Alice Johnson, phone: 555-0123'")
    print("  • 'Show me all my contacts'")
    print("  • 'Find contacts who work at Google'")
    print("")
    print("🧠 MEMORY MANAGEMENT:")
    print("  • 'Remember that John loves hiking'")
    print("  • 'Alice mentioned she studied at Harvard'")
    print("  • 'What do you know about John?'")
    print("  • 'Show me all memories'")
    print("")
    print("⏰ REMINDER MANAGEMENT:")
    print("  • 'Remind me to call John next week'")
    print("  • 'Reminder: Send Alice the project proposal'")
    print("  • 'What reminders do I have?'")
    print("")
    print("🎮 SPECIAL COMMANDS:")
    print("  • 'help' - Show this help")
    print("  • 'quit' or 'exit' - Exit the program")
    print("  • 'clear' - Clear the screen")
    print("="*60)

def interactive_test():
    """Run interactive test session"""
    
    print("🎯 LangGraph Relationship Memory Agent - Interactive Test")
    print("="*60)
    
    try:
        # Setup
        agent, user_id, vault_key, tokens = setup_agent_and_tokens()
        
        print("\n✅ Setup complete! You can now interact with the agent.")
        print("💡 Type 'help' for available commands or 'quit' to exit.")
        
        while True:
            print("\n" + "-"*40)
            user_input = input("🗣️  You: ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            print("🤖 Agent: Processing...")
            
            try:
                # Call the agent
                result = agent.handle(
                    user_id=user_id,
                    tokens=tokens,
                    user_input=user_input,
                    vault_key=vault_key
                )
                
                # Display result
                print(f"\n📊 Status: {result.get('status', 'unknown')}")
                print(f"🎯 Action: {result.get('action_taken', 'none')}")
                print(f"💬 Response: {result.get('message', 'No message')}")
                
                # Show data if available
                if result.get('data'):
                    data = result['data']
                    if isinstance(data, list) and data:
                        print(f"📄 Data ({len(data)} items):")
                        for i, item in enumerate(data[:3]):  # Show first 3 items
                            if 'name' in item:
                                print(f"  {i+1}. 👤 {item.get('name')} {f'({item.get('email', 'no email')})' if item.get('email') else ''}")
                            elif 'contact_name' in item:
                                if 'summary' in item:
                                    print(f"  {i+1}. 🧠 {item.get('contact_name')}: {item.get('summary', '')}")
                                elif 'title' in item:
                                    print(f"  {i+1}. ⏰ {item.get('contact_name')}: {item.get('title', '')}")
                        
                        if len(data) > 3:
                            print(f"  ... and {len(data) - 3} more items")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print("💡 Try typing 'help' for available commands")
    
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        print("💡 Make sure your environment is properly configured")

def quick_demo():
    """Run a quick demonstration"""
    print("🎬 Quick Demo - LangGraph Function Tool Calling")
    print("="*50)
    
    agent, user_id, vault_key, tokens = setup_agent_and_tokens()
    
    demo_commands = [
        "Add John Smith with email john@example.com",
        "Remember that John loves hiking and photography", 
        "Remind me to call John next week",
        "Show me all my contacts",
        "What do you know about John?",
        "What reminders do I have?"
    ]
    
    for i, command in enumerate(demo_commands, 1):
        print(f"\n--- Demo {i}: {command} ---")
        
        result = agent.handle(
            user_id=user_id,
            tokens=tokens,
            user_input=command,
            vault_key=vault_key
        )
        
        print(f"✅ {result.get('action_taken', 'unknown')}: {result.get('message', 'No message')}")
        
        if result.get('data') and isinstance(result['data'], list):
            print(f"📊 Data: {len(result['data'])} items")

if __name__ == "__main__":
    print("🎯 LangGraph Relationship Memory Agent Tester")
    print("="*50)
    print("Choose an option:")
    print("1. Interactive test (recommended)")
    print("2. Quick demo")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        interactive_test()
    elif choice == "2":
        quick_demo()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Please run the script again.")
