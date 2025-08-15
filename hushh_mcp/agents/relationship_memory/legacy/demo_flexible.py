"""
Relationship Memory Agent Demo
This demo shows how to use the agent with natural language input.
"""

def main():
    print("\nWelcome to the Relationship Memory Agent!")
    print("\nYou can use natural language to:")
    print("1. Add contacts - examples:")
    print("   - Add John Smith to my contacts")
    print("   - Create contact for Sarah who works at Microsoft")
    print("   - Add my friend Tom with email tom@gmail.com")
    print("\n2. Record memories - examples:")
    print("   - Remember that I met John at the coffee shop")
    print("   - Note that Sarah helped me with the project")
    print("   - Add memory: had lunch with Tom at the park")
    print("\n3. Set reminders - examples:")
    print("   - Remind me to call John next week")
    print("   - Set reminder for Sarah's birthday on 2025-09-15")
    print("   - Remember to follow up with Tom about the meeting")
    print("\n4. View information - examples:")
    print("   - Show my contacts")
    print("   - What do I remember about Sarah?")
    print("   - Show me all reminders")
    print("\nNo need to use exact formats - just type naturally!")
    print("Type 'quit' to exit.\n")

    import os
    from hushh_mcp.agents.relationship_memory.agent import RelationshipMemoryAgent
    
    # Generate a proper hex key for the vault
    vault_key = os.urandom(32).hex()
    agent = RelationshipMemoryAgent("demo_user", vault_key)

    while True:
        try:
            user_input = input("\nWhat would you like to do? > ")
            if user_input.lower() == 'quit':
                break

            result = agent.process_input(user_input)
            
            if 'error' in result:
                print("\n❌ " + result['error'])
            elif 'status' in result and result['status'] == 'success':
                print("\n✅ " + result['message'])
                # Show additional details if available
                if 'contact' in result:
                    print("\nContact details:")
                    for key, value in result['contact'].items():
                        if key != 'details':
                            print(f"  {key}: {value}")
                    if result['contact'].get('details'):
                        print("  Additional details:")
                        for key, value in result['contact']['details'].items():
                            print(f"    {key}: {value}")
                elif 'memory' in result:
                    print("\nMemory details:")
                    print(f"  About: {result['memory']['contact_name']}")
                    print(f"  What happened: {result['memory']['summary']}")
                    print(f"  When: {result['memory']['created_at']}")
                elif 'reminder' in result:
                    print("\nReminder details:")
                    print(f"  For: {result['reminder']['contact_name']}")
                    print(f"  What: {result['reminder']['title']}")
                    print(f"  When: {result['reminder']['date']}")
            else:
                print("\nResult:", result)

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
