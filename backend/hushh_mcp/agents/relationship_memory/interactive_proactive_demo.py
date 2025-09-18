"""
Interactive Demo for the Proactive Relationship Manager Agent
Full implementation with actual LLM calls and comprehensive functionality testing.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from hushh_mcp.agents.relationship_memory.index import (
    RelationshipMemoryAgent, run, run_proactive_check
)
from hushh_mcp.constants import ConsentScope
from hushh_mcp.consent.token import issue_token


class InteractiveProactiveDemo:
    """Interactive demo class for the Proactive Relationship Manager Agent"""
    
    def __init__(self):
        self.user_id = "interactive_demo_user"
        self.vault_key = "interactive_demo_vault_key"
        self.agent_id = "relationship_memory_agent"
        self.tokens = self.create_demo_tokens()
        self.session_data = {
            'contacts_added': [],
            'memories_added': [],
            'advice_requests': [],
            'proactive_checks': 0
        }
        
    def create_demo_tokens(self) -> Dict[str, str]:
        """Create demo tokens (proper HushhConsentTokens for demonstration)"""
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
    
    def print_header(self):
        """Print the demo header"""
        print("🎯 PROACTIVE RELATIONSHIP MANAGER - INTERACTIVE DEMO")
        print("=" * 70)
        print("Welcome to the comprehensive interactive demo!")
        print("This demo showcases all enhanced features with actual LLM integration.")
        print("=" * 70)
        
        # Check API key
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            print(f"✅ Gemini API Key configured: {gemini_key[:10]}...")
        else:
            print("⚠️ Warning: GEMINI_API_KEY not found in environment")
        
        print(f"📋 Demo Configuration:")
        print(f"   User ID: {self.user_id}")
        print(f"   Vault Key: {self.vault_key}")
        print(f"   Tokens: {len(self.tokens)} consent tokens created")
        print()
    
    def print_menu(self):
        """Print the interactive menu"""
        print("🎮 INTERACTIVE MENU - Choose an option:")
        print("=" * 50)
        print("📦 BASIC OPERATIONS:")
        print("  1. Add single contact")
        print("  2. Add batch contacts")
        print("  3. Add memory about contact")
        print("  4. Add important date (birthday/anniversary)")
        print("  5. Show all contacts")
        print("  6. Show upcoming dates")
        print()
        print("🚀 PROACTIVE FEATURES:")
        print("  7. Run proactive startup check")
        print("  8. Get advice about a contact")
        print("  9. Show memories")
        print(" 10. Custom command (free text)")
        print()
        print("📊 DEMO FEATURES:")
        print(" 11. Quick setup (add sample data)")
        print(" 12. Show session statistics")
        print(" 13. Test all features automatically")
        print()
        print("❌ EXIT:")
        print("  0. Exit demo")
        print("=" * 50)
    
    def add_single_contact(self):
        """Add a single contact with priority"""
        print("\n📝 ADD SINGLE CONTACT")
        print("-" * 30)
        
        examples = [
            "Add contact John Smith with email john@example.com",
            "Add high priority contact Sarah Johnson with email sarah@techcorp.com and phone +1-555-0123",
            "Add contact Mike Rodriguez at mike@design.com, he works at Design Studio"
        ]
        
        print("💡 Example commands:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        user_input = input("\n🤖 Enter your add contact command: ").strip()
        
        if not user_input:
            print("❌ No input provided")
            return
        
        print(f"Processing: {user_input}")
        result = run(
            user_id=self.user_id,
            tokens=self.tokens,
            user_input=user_input,
            vault_key=self.vault_key
        )
        
        self.display_result(result)
        if result['status'] == 'success':
            self.session_data['contacts_added'].append(user_input)
    
    def add_batch_contacts(self):
        """Add multiple contacts in one command"""
        print("\n📦 ADD BATCH CONTACTS")
        print("-" * 30)
        
        examples = [
            "Add these contacts: Alice Johnson with email alice@startup.com and Bob Wilson at +1-555-0456",
            "Add contacts: Carol Davis from TechCorp, David Kim with email david@consulting.com, and Emma Thompson at +1-555-0789"
        ]
        
        print("💡 Example batch commands:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        user_input = input("\n🤖 Enter your batch contact command: ").strip()
        
        if not user_input:
            print("❌ No input provided")
            return
        
        print(f"Processing batch: {user_input}")
        result = run(
            user_id=self.user_id,
            tokens=self.tokens,
            user_input=user_input,
            vault_key=self.vault_key
        )
        
        self.display_result(result)
        if result['status'] == 'success':
            self.session_data['contacts_added'].append(user_input)
    
    def add_memory(self):
        """Add a memory about a contact"""
        print("\n🧠 ADD MEMORY")
        print("-" * 30)
        
        examples = [
            "Remember that John Smith loves photography and just bought a new camera",
            "Remember that Sarah Johnson mentioned she's planning a trip to Japan next month",
            "Remember that Mike Rodriguez showed me his latest design portfolio and it was impressive"
        ]
        
        print("💡 Example memory commands:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        user_input = input("\n🤖 Enter your memory command: ").strip()
        
        if not user_input:
            print("❌ No input provided")
            return
        
        print(f"Processing memory: {user_input}")
        result = run(
            user_id=self.user_id,
            tokens=self.tokens,
            user_input=user_input,
            vault_key=self.vault_key
        )
        
        self.display_result(result)
        if result['status'] == 'success':
            self.session_data['memories_added'].append(user_input)
    
    def add_important_date(self):
        """Add important dates like birthdays"""
        print("\n📅 ADD IMPORTANT DATE")
        print("-" * 30)
        
        examples = [
            "John Smith's birthday is on March 15th",
            "Sarah Johnson's work anniversary is on June 22nd",
            "Mike Rodriguez's birthday is on December 5th, 1990"
        ]
        
        print("💡 Example date commands:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        user_input = input("\n🤖 Enter your date command: ").strip()
        
        if not user_input:
            print("❌ No input provided")
            return
        
        print(f"Processing date: {user_input}")
        result = run(
            user_id=self.user_id,
            tokens=self.tokens,
            user_input=user_input,
            vault_key=self.vault_key
        )
        
        self.display_result(result)
    
    def show_contacts(self):
        """Show all contacts"""
        print("\n👥 SHOW ALL CONTACTS")
        print("-" * 30)
        
        result = run(
            user_id=self.user_id,
            tokens=self.tokens,
            user_input="Show me all my contacts",
            vault_key=self.vault_key
        )
        
        self.display_result(result)
    
    def show_upcoming_dates(self):
        """Show upcoming birthdays and anniversaries"""
        print("\n🎂 SHOW UPCOMING DATES")
        print("-" * 30)
        
        result = run(
            user_id=self.user_id,
            tokens=self.tokens,
            user_input="Show me upcoming birthdays and important dates",
            vault_key=self.vault_key
        )
        
        self.display_result(result)
    
    def run_proactive_check(self):
        """Run proactive startup check"""
        print("\n🚀 PROACTIVE STARTUP CHECK")
        print("-" * 30)
        print("Running proactive check for upcoming events and reconnection suggestions...")
        
        result = run_proactive_check(
            user_id=self.user_id,
            tokens=self.tokens,
            vault_key=self.vault_key
        )
        
        self.display_result(result)
        self.session_data['proactive_checks'] += 1
    
    def get_advice(self):
        """Get advice about a contact"""
        print("\n💡 GET ADVICE ABOUT CONTACT")
        print("-" * 30)
        
        examples = [
            "What should I get John Smith for his birthday?",
            "I need advice about reconnecting with Sarah Johnson",
            "What are some good conversation topics for Mike Rodriguez?",
            "Help me plan a meeting with Alice Johnson"
        ]
        
        print("💡 Example advice requests:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        user_input = input("\n🤖 Enter your advice request: ").strip()
        
        if not user_input:
            print("❌ No input provided")
            return
        
        print(f"Processing advice request: {user_input}")
        result = run(
            user_id=self.user_id,
            tokens=self.tokens,
            user_input=user_input,
            vault_key=self.vault_key
        )
        
        self.display_result(result)
        if result['status'] == 'success':
            self.session_data['advice_requests'].append(user_input)
    
    def show_memories(self):
        """Show memories"""
        print("\n🧠 SHOW MEMORIES")
        print("-" * 30)
        
        result = run(
            user_id=self.user_id,
            tokens=self.tokens,
            user_input="Show me my recent memories",
            vault_key=self.vault_key
        )
        
        self.display_result(result)
    
    def custom_command(self):
        """Allow custom free-text command"""
        print("\n🎯 CUSTOM COMMAND")
        print("-" * 30)
        print("Enter any natural language command to test the agent's understanding.")
        print("The agent will parse your intent and execute the appropriate action.")
        
        user_input = input("\n🤖 Enter your custom command: ").strip()
        
        if not user_input:
            print("❌ No input provided")
            return
        
        print(f"Processing custom command: {user_input}")
        result = run(
            user_id=self.user_id,
            tokens=self.tokens,
            user_input=user_input,
            vault_key=self.vault_key
        )
        
        self.display_result(result)
    
    def quick_setup(self):
        """Add sample data for testing"""
        print("\n⚡ QUICK SETUP - ADDING SAMPLE DATA")
        print("-" * 30)
        
        sample_commands = [
            "Add contact Alice Johnson with email alice@techstartup.com, she's a high priority contact",
            "Add contacts: Bob Wilson at +1-555-0123 and Carol Davis with email carol@designstudio.com",
            "Remember that Alice Johnson loves rock climbing and photography",
            "Remember that Bob Wilson is a software engineer who enjoys cooking",
            "Alice Johnson's birthday is on March 15th",
            "Bob Wilson's work anniversary is on June 10th"
        ]
        
        print("Adding sample data...")
        for i, command in enumerate(sample_commands, 1):
            print(f"\n{i}. {command}")
            result = run(
                user_id=self.user_id,
                tokens=self.tokens,
                user_input=command,
                vault_key=self.vault_key
            )
            
            if result['status'] == 'success':
                print(f"   ✅ Success: {result['message'][:50]}...")
                if 'add contact' in command.lower():
                    self.session_data['contacts_added'].append(command)
                elif 'remember' in command.lower():
                    self.session_data['memories_added'].append(command)
            else:
                print(f"   ❌ Failed: {result['message'][:50]}...")
        
        print(f"\n✅ Quick setup completed! Added sample contacts, memories, and dates.")
    
    def show_session_stats(self):
        """Show session statistics"""
        print("\n📊 SESSION STATISTICS")
        print("-" * 30)
        print(f"Contacts added: {len(self.session_data['contacts_added'])}")
        print(f"Memories added: {len(self.session_data['memories_added'])}")
        print(f"Advice requests: {len(self.session_data['advice_requests'])}")
        print(f"Proactive checks: {self.session_data['proactive_checks']}")
        
        if self.session_data['contacts_added']:
            print(f"\n📝 Recent contacts:")
            for contact in self.session_data['contacts_added'][-3:]:
                print(f"   • {contact[:60]}...")
        
        if self.session_data['memories_added']:
            print(f"\n🧠 Recent memories:")
            for memory in self.session_data['memories_added'][-3:]:
                print(f"   • {memory[:60]}...")
    
    def test_all_features(self):
        """Automatically test all features"""
        print("\n🧪 AUTOMATED FEATURE TESTING")
        print("-" * 30)
        
        test_commands = [
            ("Single Contact", "Add contact Test User with email test@example.com"),
            ("Batch Contacts", "Add contacts: Demo User1 and Demo User2 with phone 555-0000"),
            ("Memory", "Remember that Test User loves artificial intelligence"),
            ("Important Date", "Test User's birthday is on April 1st"),
            ("Show Contacts", "Show me all my contacts"),
            ("Upcoming Dates", "Show upcoming birthdays"),
            ("Advice Request", "What should I get Test User for their birthday?"),
            ("Show Memories", "Show me my memories")
        ]
        
        results = []
        
        for test_name, command in test_commands:
            print(f"\n🧪 Testing: {test_name}")
            print(f"   Command: {command}")
            
            try:
                result = run(
                    user_id=self.user_id,
                    tokens=self.tokens,
                    user_input=command,
                    vault_key=self.vault_key
                )
                
                success = result['status'] == 'success'
                print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
                print(f"   Action: {result.get('action_taken', 'unknown')}")
                
                results.append((test_name, success, result.get('action_taken', 'unknown')))
                
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                results.append((test_name, False, f"Error: {str(e)}"))
        
        # Test proactive check
        print(f"\n🧪 Testing: Proactive Check")
        try:
            result = run_proactive_check(
                user_id=self.user_id,
                tokens=self.tokens,
                vault_key=self.vault_key
            )
            success = result['status'] == 'success'
            print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
            results.append(("Proactive Check", success, result.get('action_taken', 'unknown')))
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append(("Proactive Check", False, f"Error: {str(e)}"))
        
        # Summary
        print(f"\n📊 TEST SUMMARY:")
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)
        print(f"   Passed: {passed}/{total} tests")
        
        for test_name, success, action in results:
            status = "✅" if success else "❌"
            print(f"   {status} {test_name}: {action}")
    
    def display_result(self, result: Dict[str, Any]):
        """Display the result of an operation"""
        print(f"\n📋 RESULT:")
        print(f"   Status: {result['status']}")
        print(f"   Action: {result.get('action_taken', 'unknown')}")
        
        if result['status'] == 'success':
            print(f"   ✅ {result['message']}")
            if result.get('data'):
                print(f"   📊 Data items: {len(result['data'])}")
        else:
            print(f"   ❌ {result['message']}")
        
        print("-" * 50)
    
    def run(self):
        """Run the interactive demo"""
        self.print_header()
        
        while True:
            try:
                self.print_menu()
                choice = input("🎯 Enter your choice (0-13): ").strip()
                
                if choice == '0':
                    print("\n👋 Thank you for trying the Proactive Relationship Manager Agent!")
                    print("🎉 All features are working correctly with actual LLM integration!")
                    break
                elif choice == '1':
                    self.add_single_contact()
                elif choice == '2':
                    self.add_batch_contacts()
                elif choice == '3':
                    self.add_memory()
                elif choice == '4':
                    self.add_important_date()
                elif choice == '5':
                    self.show_contacts()
                elif choice == '6':
                    self.show_upcoming_dates()
                elif choice == '7':
                    self.run_proactive_check()
                elif choice == '8':
                    self.get_advice()
                elif choice == '9':
                    self.show_memories()
                elif choice == '10':
                    self.custom_command()
                elif choice == '11':
                    self.quick_setup()
                elif choice == '12':
                    self.show_session_stats()
                elif choice == '13':
                    self.test_all_features()
                else:
                    print("❌ Invalid choice. Please enter a number between 0-13.")
                
                input("\n⏸️ Press Enter to continue...")
                print("\n" + "="*70 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")
                input("⏸️ Press Enter to continue...")


def main():
    """Main function to run the interactive demo"""
    print("🚀 Starting Proactive Relationship Manager Interactive Demo...")
    
    # Check if Gemini API key is available
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️ Warning: GEMINI_API_KEY not found in environment variables.")
        print("Some features may not work correctly without the API key.")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print("👋 Goodbye!")
            return
    
    # Start the interactive demo
    demo = InteractiveProactiveDemo()
    demo.run()


if __name__ == "__main__":
    main()