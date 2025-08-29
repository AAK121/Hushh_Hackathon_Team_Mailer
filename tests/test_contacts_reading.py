#!/usr/bin/env python3
"""
Test the _read_contacts_with_consent function directly to debug the issue.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import tempfile

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope

def create_test_excel():
    """Create a test Excel file with contacts."""
    data = {
        'name': ['Test User 1', 'Test User 2'],  # lowercase
        'email': ['test1@example.com', 'test2@example.com'],  # lowercase  
        'description': ['Testing email 1', 'Testing email 2']  # lowercase
    }
    df = pd.DataFrame(data)
    
    # Create temporary Excel file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        return tmp_file.name

def generate_test_tokens():
    """Generate test consent tokens."""
    user_id = "test_debug_user"
    agent_id = "agent_mailerpanda"
    
    consent_tokens = {}
    required_scopes = [
        ConsentScope.VAULT_READ_EMAIL,
        ConsentScope.VAULT_WRITE_EMAIL,
        ConsentScope.VAULT_READ_FILE,
        ConsentScope.VAULT_WRITE_FILE,
        ConsentScope.CUSTOM_TEMPORARY
    ]
    
    for scope in required_scopes:
        try:
            token_obj = issue_token(
                user_id=user_id,
                agent_id=agent_id,
                scope=scope,
                expires_in_ms=3600000
            )
            consent_tokens[scope.value] = token_obj.token
        except Exception as e:
            print(f"❌ Failed to generate token for {scope.value}: {e}")
    
    return consent_tokens, user_id

def test_contacts_reading():
    """Test the _read_contacts_with_consent function directly."""
    print("🧪 Testing Contact Reading Function")
    print("=" * 45)
    
    # Create test Excel file
    excel_path = create_test_excel()
    print(f"📁 Created test Excel file: {excel_path}")
    print(f"   File exists: {os.path.exists(excel_path)}")
    
    # Generate tokens
    consent_tokens, user_id = generate_test_tokens()
    print(f"🔐 Generated consent tokens for user: {user_id}")
    
    # Create agent
    agent = MassMailerAgent()
    
    try:
        print(f"\n📊 Calling _read_contacts_with_consent...")
        print(f"   Excel path: {excel_path}")
        print(f"   User ID: {user_id}")
        print(f"   Consent tokens: {len(consent_tokens)} tokens")
        
        contacts = agent._read_contacts_with_consent(
            user_id=user_id,
            consent_tokens=consent_tokens,
            excel_file_path=excel_path
        )
        
        print(f"\n✅ SUCCESS: Read {len(contacts)} contacts")
        for i, contact in enumerate(contacts):
            print(f"   Contact {i+1}: {contact.get('Name', 'N/A')} - {contact.get('Email', 'N/A')} - Validated: {contact.get('email_validated', False)}")
        
        return len(contacts) > 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if os.path.exists(excel_path):
            os.unlink(excel_path)

if __name__ == "__main__":
    success = test_contacts_reading()
    print(f"\n{'✅ Contact reading working' if success else '❌ Contact reading failed'}")
