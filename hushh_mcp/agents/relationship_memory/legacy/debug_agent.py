"""
Debug script to test the LangGraph agent parsing
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from main project folder
project_root = str(Path(__file__).parent.parent.parent.parent)
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Add the project root to Python path
sys.path.insert(0, project_root)

from hushh_mcp.agents.relationship_memory.langgraph_agent import RelationshipMemoryAgent
import uuid

def debug_parsing():
    """Debug the parsing functionality"""
    print("🔍 Debugging LangGraph Agent Parsing")
    print("=" * 50)
    
    # Check environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    print(f"✅ Gemini API Key: {gemini_key[:10]}..." if gemini_key else "❌ No Gemini API Key")
    
    # Initialize agent
    user_id = str(uuid.uuid4())
    vault_key = os.urandom(32).hex()
    
    try:
        agent = RelationshipMemoryAgent(user_id=user_id, vault_key=vault_key)
        print("✅ Agent initialized successfully!")
        
        # Test input parsing directly
        test_input = "add alok as a contact with email 23b2223@iitb.ac.in"
        print(f"\n🔍 Testing input: {test_input}")
        
        # Create initial state manually to debug
        from hushh_mcp.agents.relationship_memory.langgraph_agent import RelationshipMemoryState
        
        test_state = RelationshipMemoryState(
            user_input=test_input,
            user_id=user_id,
            agent_id="relationship_memory",
            vault_key=vault_key,
            parsed_intent=None,
            contacts=[],
            memories=[],
            reminders=[],
            response={},
            error=None,
            conversation_history=[]
        )
        
        # Test parsing node directly
        print("🧠 Testing parsing node...")
        parsed_state = agent._parse_input_node(test_state)
        
        print(f"📋 Parsed intent: {parsed_state.get('parsed_intent')}")
        print(f"📋 Error: {parsed_state.get('error')}")
        
        # Test the full pipeline
        print("\n🚀 Testing full pipeline...")
        result = agent.process_input(test_input)
        print(f"📋 Final result: {result}")
        
        # Test showing contacts
        print("\n📋 Testing show contacts...")
        show_result = agent.process_input("show my contacts")
        print(f"📋 Show contacts result: {show_result}")
        
        # Test memory functionality
        print("\n📋 Testing memory...")
        memory_input = "Remember that Alok loves playing cricket and is from IIT Bombay"
        memory_result = agent.process_input(memory_input)
        print(f"📋 Memory result: {memory_result}")
        
        # Test reminder functionality
        print("\n📋 Testing reminder...")
        reminder_input = "Set a reminder to call Alok next Friday"
        reminder_result = agent.process_input(reminder_input)
        print(f"📋 Reminder result: {reminder_result}")
        
        # Check vault manager directly
        print(f"\n🔍 Direct vault check - contacts: {len(agent.vault_manager.get_contacts())}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_parsing()
