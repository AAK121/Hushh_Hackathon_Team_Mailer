import uuid
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, project_root)

from hushh_mcp.agents.relationship_memory.agent import RelationshipMemoryAgent

def generate_test_vault_key():
    """Generate a test vault key for demo purposes"""
    return os.urandom(32).hex()

def main():
    # Initialize the agent with test credentials
    user_id = str(uuid.uuid4())
    vault_key = generate_test_vault_key()
    agent = RelationshipMemoryAgent(user_id=user_id, vault_key=vault_key)
    
    print("Relationship Memory Agent Demo")
    print("=============================")
    print("\nExample commands:")
    print("- Add John Smith as a contact")
    print("- Remember that I met Sarah at the conference")
    print("- Remind me to call Mike on 2024-03-15")
    print("- Show my contacts")
    print("- Show memories about John")
    print("\nType 'quit' to exit")
    
    while True:
        try:
            user_input = input("\nWhat would you like to do? > ")
            if user_input.lower() == 'quit':
                break
                
            result = agent.process_input(user_input)
            
            # Pretty print the result
            if isinstance(result, dict):
                if "error" in result:
                    print(f"\nError: {result['error']}")
                else:
                    if "status" in result and result["status"] == "success":
                        print(f"\nSuccess: {result['message']}")
                    if "contact" in result:
                        print(f"Contact added: {result['contact']['name']}")
                        if "details" in result["contact"] and result["contact"]["details"]:
                            print("Details:")
                            for key, value in result["contact"]["details"].items():
                                print(f"  {key}: {value}")
                    if "memory" in result:
                        print(f"Memory: {result['memory']['summary']}")
                    if "reminder" in result:
                        print(f"Reminder set for {result['reminder']['contact_name']}: {result['reminder']['title']} on {result['reminder']['date']}")
                    if "contacts" in result:
                        if result["contacts"]:
                            print("\nContacts:")
                            for contact in result["contacts"]:
                                print(f"- {contact['name']}")
                        else:
                            print("No contacts found")
                    if "memories" in result:
                        if result["memories"]:
                            print(f"\nMemories:")
                            for memory in result["memories"]:
                                print(f"- {memory['summary']} ({memory['created_at']})")
                        else:
                            print("No memories found")
            else:
                print("\nReceived unexpected response format")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            
    print("\nThank you for using the Relationship Memory Agent!")

if __name__ == "__main__":
    main()
