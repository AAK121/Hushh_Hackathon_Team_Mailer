"""
Demo for the LangGraph-based Relationship Memory Agent
"""

import uuid
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, project_root)

from hushh_mcp.agents.relationship_memory.langgraph_agent import RelationshipMemoryAgent

def generate_test_vault_key():
    """Generate a test vault key for demo purposes"""
    return os.urandom(32).hex()

def format_response(response):
    """Format the response for better display"""
    if response.get("status") == "success":
        print(f"\n✅ {response.get('message', 'Success')}")
        
        # Display contacts
        if "contacts" in response:
            contacts = response["contacts"]
            if contacts:
                print("\n📇 Contacts:")
                for contact in contacts:
                    print(f"  • {contact.get('name', 'Unknown')}")
                    if contact.get('email'):
                        print(f"    📧 {contact['email']}")
                    if contact.get('phone'):
                        print(f"    📱 {contact['phone']}")
                    if contact.get('company'):
                        print(f"    🏢 {contact['company']}")
                    print()
            else:
                print("  No contacts found")
        
        # Display memories
        if "memories" in response:
            memories = response["memories"]
            if memories:
                print("\n🧠 Memories:")
                for memory in memories:
                    print(f"  • {memory.get('contact_name', 'Unknown')}: {memory.get('summary', 'No summary')}")
                    if memory.get('location'):
                        print(f"    📍 {memory['location']}")
                    if memory.get('date'):
                        print(f"    📅 {memory['date']}")
                    print()
            else:
                print("  No memories found")
        
        # Display reminders
        if "reminders" in response:
            reminders = response["reminders"]
            if reminders:
                print("\n⏰ Reminders:")
                for reminder in reminders:
                    print(f"  • {reminder.get('title', 'No title')} - {reminder.get('contact_name', 'Unknown')}")
                    print(f"    📅 {reminder.get('date', 'No date')} (Priority: {reminder.get('priority', 'medium')})")
                    print()
            else:
                print("  No reminders found")
        
        # Display added contact
        if "contact" in response:
            contact = response["contact"]
            print(f"\n📇 Added Contact: {contact.get('name', 'Unknown')}")
            if contact.get('email'):
                print(f"    📧 {contact['email']}")
            if contact.get('phone'):
                print(f"    📱 {contact['phone']}")
            if contact.get('company'):
                print(f"    🏢 {contact['company']}")
        
        # Display added memory
        if "memory" in response:
            memory = response["memory"]
            print(f"\n🧠 Added Memory: {memory.get('contact_name', 'Unknown')}")
            print(f"    💭 {memory.get('summary', 'No summary')}")
        
        # Display added reminder
        if "reminder" in response:
            reminder = response["reminder"]
            print(f"\n⏰ Added Reminder: {reminder.get('title', 'No title')}")
            print(f"    👤 For: {reminder.get('contact_name', 'Unknown')}")
            print(f"    📅 Date: {reminder.get('date', 'No date')}")
    
    elif response.get("status") == "error":
        print(f"\n❌ Error: {response.get('message', 'Unknown error')}")
        
        suggestions = response.get("suggestions", [])
        if suggestions:
            print("\n💡 Suggestions:")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
    
    else:
        print(f"\n🤔 Unexpected response: {response}")

def main():
    print("🤖 LangGraph Relationship Memory Agent Demo")
    print("=" * 50)
    print("\nThis agent uses AI to understand your natural language input!")
    print("\n✨ Example commands:")
    print("  • Add John Smith with email john@example.com")
    print("  • Remember that I met Sarah at the tech conference")
    print("  • Remind me to call Mike on 2024-03-15")
    print("  • Show my contacts")
    print("  • Search for contacts at Google")
    print("  • Show memories about John")
    print("\n💬 Just type naturally - the AI will understand!")
    print("\n⚠️  Note: You need an OpenAI API key set in your environment for AI parsing to work.")
    print("    If not available, the agent will fall back to error handling.")
    print("\nType 'quit' to exit\n")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("   The AI parsing will not work without it. Set it with:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   Or add it to your .env file\n")
    
    # Initialize the agent
    user_id = str(uuid.uuid4())
    vault_key = generate_test_vault_key()
    
    try:
        agent = RelationshipMemoryAgent(user_id=user_id, vault_key=vault_key)
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        print("   This might be due to missing OpenAI API key or LangGraph dependencies.")
        return
    
    while True:
        try:
            user_input = input("💬 What would you like to do? > ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            
            if not user_input:
                print("Please enter a command or type 'quit' to exit.")
                continue
            
            print("\n🤔 Processing...")
            result = agent.process_input(user_input)
            format_response(result)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("   Please try again or type 'quit' to exit.")
    
    print("\n👋 Thank you for using the LangGraph Relationship Memory Agent!")
    print("🔒 All your data was stored securely using Hush MCP vault encryption.")

if __name__ == "__main__":
    main()
