"""
Interactive demo for the LangGraph-based Relationship Memory Agent with Gemini AI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, project_root)

from langgraph_agent import RelationshipMemoryAgent

def main():
    print("🤖 LangGraph Relationship Memory Agent with Gemini AI")
    print("=" * 60)
    
    # Check environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ ERROR: GEMINI_API_KEY environment variable not set!")
        return
    
    # Initialize agent
    user_id = str(uuid.uuid4())
    vault_key = os.urandom(32).hex()
    
    print(f"🔧 Initializing agent...")
    try:
        agent = RelationshipMemoryAgent(user_id=user_id, vault_key=vault_key)
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    print("\n📝 Example commands:")
    print("• add alok as a contact with email 23b2223@iitb.ac.in")
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
            
            print("🤔 Processing...")
            result = agent.process_input(user_input)
            
            # Pretty print the result
            print(f"\n📋 Result:")
            if isinstance(result, dict):
                for key, value in result.items():
                    if key == 'contacts' and isinstance(value, list):
                        print(f"  {key}: {len(value)} contacts")
                        for contact in value:
                            print(f"    - {contact.get('name', 'Unknown')} ({contact.get('email', 'No email')})")
                    elif key == 'memories' and isinstance(value, list):
                        print(f"  {key}: {len(value)} memories")
                        for memory in value:
                            print(f"    - {memory.get('summary', 'No summary')}")
                    elif key == 'reminders' and isinstance(value, list):
                        print(f"  {key}: {len(value)} reminders")
                        for reminder in value:
                            print(f"    - {reminder.get('title', 'No title')} on {reminder.get('date', 'No date')}")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"  {result}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
