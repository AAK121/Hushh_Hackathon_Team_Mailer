"""
Interactive Chat Demo for the Proactive Relationship Manager Agent
Natural conversation interface - just type what you want to do!
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from hushh_mcp.agents.relationship_memory.index import (
    RelationshipMemoryAgent, run, run_proactive_check
)
from hushh_mcp.constants import ConsentScope
from hushh_mcp.consent.token import issue_token


class ChatDemo:
    """Natural language chat interface for the Proactive Relationship Manager Agent"""
    
    def __init__(self):
        self.user_id = "chat_demo_user"
        self.vault_key = "chat_demo_vault_key"
        self.agent_id = "relationship_memory_agent"
        self.tokens = self.create_demo_tokens()
        self.conversation_count = 0
        
    def create_demo_tokens(self) -> Dict[str, str]:
        """Create demo tokens for the session"""
        # Create proper HushhConsentTokens
        scopes = [
            ConsentScope.VAULT_READ_CONTACTS,
            ConsentScope.VAULT_WRITE_CONTACTS,
            ConsentScope.VAULT_READ_MEMORY,
            ConsentScope.VAULT_WRITE_MEMORY,
        ]
        
        tokens = {}
        for scope in scopes:
            token = issue_token(
                user_id=self.user_id,
                agent_id=self.agent_id,
                scope=scope,
                expires_in_ms=1000 * 60 * 60 * 24  # 24 hours
            )
            tokens[scope.value] = token.token
        
        return tokens
    
    def print_welcome(self):
        """Print welcome message"""
        print("🎯 PROACTIVE RELATIONSHIP MANAGER - CHAT DEMO")
        print("=" * 60)
        print("Welcome! Just type what you want to do in natural language.")
        print("The agent will automatically understand and execute your request.")
        print("=" * 60)
        
        # Check API key
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            print(f"✅ Gemini API Key: {gemini_key[:10]}...")
        else:
            print("⚠️ Warning: GEMINI_API_KEY not found")
        
        print(f"\n💡 Try saying things like:")
        print(f"  • 'add contact John Smith with email john@example.com'")
        print(f"  • 'add contacts: Alice and Bob with phone 555-1234'")
        print(f"  • 'remember that Sarah loves photography'")
        print(f"  • 'what should I get Mike for his birthday?'")
        print(f"  • 'show my contacts'")
        print(f"  • 'upcoming birthdays'")
        print(f"  • 'proactive check' (for startup notifications)")
        print(f"  • 'help' (for more examples)")
        print(f"  • 'quit' or 'exit' to leave")
        print()
    
    def show_help(self):
        """Show help with examples"""
        print("\n💡 HELP - EXAMPLE COMMANDS")
        print("=" * 50)
        print("📝 ADDING CONTACTS:")
        print("  • add contact John Smith with email john@example.com")
        print("  • add high priority contact Sarah Johnson at sarah@techcorp.com")
        print("  • add contacts: Mike Rodriguez and Lisa Wang with phone 555-0123")
        print()
        print("🧠 ADDING MEMORIES:")
        print("  • remember that John loves photography")
        print("  • remember that Sarah mentioned she's planning a trip to Japan")
        print("  • John told me he just bought a new camera")
        print()
        print("📅 IMPORTANT DATES:")
        print("  • John's birthday is on March 15th")
        print("  • Sarah's work anniversary is June 22nd")
        print("  • add birthday for Mike on December 5th")
        print()
        print("💡 GETTING ADVICE:")
        print("  • what should I get John for his birthday?")
        print("  • I need advice about reconnecting with Sarah")
        print("  • help me plan a conversation with Mike")
        print()
        print("📋 VIEWING INFORMATION:")
        print("  • show my contacts")
        print("  • show upcoming birthdays")
        print("  • show my memories")
        print("  • tell me about John Smith")
        print()
        print("🚀 PROACTIVE FEATURES:")
        print("  • proactive check")
        print("  • startup check")
        print("  • check for upcoming events")
        print("-" * 50)
    
    def handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands like help, quit, etc. Returns True if handled."""
        user_input_lower = user_input.lower().strip()
        
        if user_input_lower in ['quit', 'exit', 'bye', 'goodbye']:
            print("\n👋 Thank you for trying the Proactive Relationship Manager Agent!")
            print("🎉 Hope you enjoyed exploring all the enhanced features!")
            return True
        
        elif user_input_lower in ['help', '?', 'examples']:
            self.show_help()
            return True
        
        elif user_input_lower in ['proactive check', 'startup check', 'proactive', 'check for events']:
            print("\n🚀 Running proactive startup check...")
            result = run_proactive_check(
                user_id=self.user_id,
                tokens=self.tokens,
                vault_key=self.vault_key
            )
            self.display_result(result)
            return True
        
        elif user_input_lower in ['clear', 'cls']:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_welcome()
            return True
        
        return False
    
    def display_result(self, result: Dict[str, Any]):
        """Display the result in a conversational way"""
        print(f"\n🤖 Agent Response:")
        print("-" * 30)
        
        if result['status'] == 'success':
            print(f"✅ {result['message']}")
            
            # Show additional info if available
            if result.get('data') and len(result['data']) > 0:
                data_count = len(result['data'])
                action = result.get('action_taken', '')
                
                if 'contact' in action:
                    print(f"📊 Processed {data_count} contact(s)")
                elif 'memory' in action:
                    print(f"📊 Found {data_count} memory/memories")
                elif 'reminder' in action:
                    print(f"📊 Found {data_count} reminder(s)")
                else:
                    print(f"📊 Retrieved {data_count} item(s)")
            
            # Show action taken for debugging (optional)
            if result.get('action_taken'):
                print(f"🔧 Action: {result['action_taken']}")
        
        else:
            print(f"❌ {result['message']}")
        
        print("-" * 30)
    
    def process_input(self, user_input: str):
        """Process user input through the agent"""
        print(f"\n🔄 Processing: {user_input}")
        
        try:
            result = run(
                user_id=self.user_id,
                tokens=self.tokens,
                user_input=user_input,
                vault_key=self.vault_key
            )
            
            self.display_result(result)
            
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("💡 Try rephrasing your request or type 'help' for examples.")
    
    def run(self):
        """Run the interactive chat demo"""
        self.print_welcome()
        
        # Optional: Run initial proactive check
        print("🚀 Demo ready! Starting interactive session...")
        # Disable proactive check for now due to workflow issues
        # try:
        #     initial_result = run_proactive_check(
        #         user_id=self.user_id,
        #         tokens=self.tokens,
        #         vault_key=self.vault_key
        #     )
        #     if initial_result['message'].strip():
        #         self.display_result(initial_result)
        #     else:
        #         print("✅ No proactive notifications at this time.")
        # except:
        #     print("⚠️ Initial proactive check skipped.")
        print("✅ Ready for your commands!")
        
        print(f"\n💬 Start chatting! (Type 'help' for examples, 'quit' to exit)")
        print("=" * 60)
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n[{self.conversation_count + 1}] 🗣️ You: ").strip()
                
                if not user_input:
                    print("💭 (Please say something or type 'help' for examples)")
                    continue
                
                # Handle special commands
                if self.handle_special_commands(user_input):
                    if user_input.lower().strip() in ['quit', 'exit', 'bye', 'goodbye']:
                        break
                    continue
                
                # Process through the agent
                self.process_input(user_input)
                self.conversation_count += 1
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")
                print("💡 Try again or type 'quit' to exit.")


def main():
    """Main function to start the chat demo"""
    print("🚀 Starting Proactive Relationship Manager Chat Demo...")
    
    # Check environment
    if not os.getenv('GEMINI_API_KEY'):
        print("\n⚠️ Warning: GEMINI_API_KEY not found in environment variables.")
        print("The agent needs this API key for natural language understanding.")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print("👋 Goodbye!")
            return
    
    # Start the chat demo
    try:
        demo = ChatDemo()
        demo.run()
    except Exception as e:
        print(f"\n❌ Failed to start demo: {str(e)}")
        print("Please check your environment and try again.")


if __name__ == "__main__":
    main()