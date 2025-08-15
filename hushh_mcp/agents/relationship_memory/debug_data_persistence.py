#!/usr/bin/env python3
"""
Debug script to check if data is actually being saved to the vault database
"""

import os
import sys
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgent
from hushh_mcp.agents.relationship_memory.utils.vault_manager import VaultManager

def check_database_contents():
    """Check what's actually in the database"""
    print("🔍 Checking database contents...")
    
    # Find database files
    data_dir = Path(__file__).parent / "utils" / "data"
    if data_dir.exists():
        db_files = list(data_dir.glob("*.db"))
        print(f"Found {len(db_files)} database files:")
        for db_file in db_files:
            print(f"  - {db_file}")
            
            # Check contents
            with sqlite3.connect(db_file) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"    Tables: {[t[0] for t in tables]}")
                
                if 'vault_records' in [t[0] for t in tables]:
                    cursor = conn.execute("SELECT COUNT(*) FROM vault_records;")
                    count = cursor.fetchone()[0]
                    print(f"    Total records: {count}")
                    
                    if count > 0:
                        cursor = conn.execute("""
                            SELECT record_type, record_id, user_id, scope, created_at, deleted 
                            FROM vault_records 
                            ORDER BY created_at DESC 
                            LIMIT 10;
                        """)
                        records = cursor.fetchall()
                        print("    Recent records:")
                        for record in records:
                            print(f"      {record}")
    else:
        print("No data directory found!")

def test_direct_vault_operations():
    """Test vault operations directly"""
    print("\n🧪 Testing direct vault operations...")
    
    user_id = "debug_user"
    vault_key = "e2d989c4d382c80beebbe58c6f07f94b42e554f691ab11738115a489350584b8"
    
    # Initialize vault manager directly
    vault_manager = VaultManager(user_id=user_id, vault_key=vault_key)
    
    # Test storing a contact
    print("Storing test contact...")
    contact_data = {
        "name": "Test Contact",
        "email": "test@example.com",
        "phone": "555-1234"
    }
    
    try:
        result = vault_manager.store_contact(contact_data)
        print(f"✅ Contact stored: {result}")
    except Exception as e:
        print(f"❌ Failed to store contact: {e}")
    
    # Test retrieving contacts
    print("Retrieving contacts...")
    try:
        contacts = vault_manager.get_all_contacts()
        print(f"✅ Retrieved {len(contacts)} contacts:")
        for contact in contacts:
            print(f"  - {contact}")
    except Exception as e:
        print(f"❌ Failed to retrieve contacts: {e}")

def test_agent_with_direct_commands():
    """Test the agent with direct database checks"""
    print("\n🤖 Testing agent with database verification...")
    
    load_dotenv()
    
    # Initialize agent
    agent = RelationshipMemoryAgent()
    user_id = "debug_agent_user"
    vault_key = "e2d989c4d382c80beebbe58c6f07f94b42e554f691ab11738115a489350584b8"
    
    # Issue tokens
    tokens = {}
    for scope in agent.required_scopes:
        token_obj = issue_token(
            user_id=user_id,
            agent_id=agent.agent_id,
            scope=scope,
            expires_in_ms=24 * 60 * 60 * 1000
        )
        tokens[scope.value] = token_obj.token
    
    # Test adding a contact
    print("Adding contact via agent...")
    result = agent.handle(
        user_id=user_id,
        tokens=tokens,
        user_input="Add contact: Debug User, email: debug@test.com",
        vault_key=vault_key
    )
    print(f"Agent result: {result}")
    
    # Check database directly after agent operation
    print("\nChecking database after agent operation...")
    vault_manager = VaultManager(user_id=user_id, vault_key=vault_key)
    contacts = vault_manager.get_all_contacts()
    print(f"Contacts in database: {len(contacts)}")
    for contact in contacts:
        print(f"  - {contact}")

def check_langgraph_usage():
    """Check if the agent is using LangGraph"""
    print("\n🔍 Checking for LangGraph usage...")
    
    # Check imports in agent files
    agent_files = [
        "index.py",
        "utils/llm.py",
        "utils/vault_manager.py"
    ]
    
    for file_path in agent_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                content = f.read()
                if 'langgraph' in content.lower():
                    print(f"✅ LangGraph found in {file_path}")
                    # Find specific lines
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'langgraph' in line.lower():
                            print(f"    Line {i+1}: {line.strip()}")
                else:
                    print(f"❌ No LangGraph found in {file_path}")

if __name__ == "__main__":
    print("🚀 Starting comprehensive debug session...\n")
    
    # Check database contents
    check_database_contents()
    
    # Test direct vault operations
    test_direct_vault_operations()
    
    # Test agent with verification
    test_agent_with_direct_commands()
    
    # Check for LangGraph usage
    check_langgraph_usage()
    
    # Final database check
    print("\n📊 Final database state:")
    check_database_contents()
    
    print("\n✅ Debug session completed!")
