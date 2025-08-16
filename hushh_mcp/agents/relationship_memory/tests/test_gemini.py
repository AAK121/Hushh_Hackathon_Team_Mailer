"""Test script for the LangGraph-based Relationship Memory Agent with Gemini AI"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from main project folder
project_root = str(Path(__file__).parent.parent.parent.parent.parent)
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Add the project root to Python path
sys.path.insert(0, project_root)

from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgent
import uuid

def test_basic_functionality():
    """Test basic agent functionality"""
    print("🚀 Testing LangGraph Relationship Memory Agent with Gemini AI")
    print("=" * 60)
    
    # Check if Gemini API key is available
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ ERROR: GEMINI_API_KEY environment variable not set!")
        return False
    
    print(f"✅ Gemini API Key found: {gemini_key[:10]}...")
    
    try:
        # Initialize agent
        user_id = str(uuid.uuid4())
        vault_key = os.urandom(32).hex()
        
        print(f"🔧 Initializing agent with user_id: {user_id[:8]}...")
        agent = RelationshipMemoryAgent(user_id=user_id, vault_key=vault_key)
        print("✅ Agent initialized successfully!")
        
        # Test 1: Add a contact
        print("\n📝 Test 1: Adding a contact...")
        result1 = agent.process_input("add alok as a contact with email 23b2223@iitb.ac.in")
        print(f"Result: {result1}")
        
        # Test 2: Show contacts
        print("\n📋 Test 2: Showing contacts...")
        result2 = agent.process_input("show my contacts")
        print(f"Result: {result2}")
        
        # Test 3: Add a memory
        print("\n🧠 Test 3: Adding a memory...")
        result3 = agent.process_input("remember that I met alok at the conference")
        print(f"Result: {result3}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)
