#!/usr/bin/env python3
"""
Generate valid consent tokens for testing the approval workflow.
"""

import requests
import json

def generate_test_tokens():
    """Generate test consent tokens that should work with the system."""
    
    # Test with minimal required scopes
    test_tokens = {
        "vault.read.email": "test_vault_read_token_12345",
        "email.send": "test_email_send_token_67890", 
        "contact.read": "test_contact_read_token_abcde",
        "custom.temporary": "test_temp_token_fghij"
    }
    
    print("🔑 Generated Test Consent Tokens:")
    for scope, token in test_tokens.items():
        print(f"   {scope}: {token}")
    
    return test_tokens

def test_with_valid_tokens():
    """Test campaign creation with properly formatted tokens."""
    import base64
    import io
    import pandas as pd
    
    # Create test data
    data = {
        'email': ['test1@example.com', 'test2@example.com'],
        'name': ['User One', 'User Two'],
        'description': ['Tech professional', 'Marketing specialist']
    }
    df = pd.DataFrame(data)
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    excel_data = base64.b64encode(excel_buffer.getvalue()).decode('utf-8')
    
    # Generate tokens
    tokens = generate_test_tokens()
    
    # Create request
    request_data = {
        "user_id": "valid_token_test_user",
        "user_input": "Create a professional email campaign for product announcement",
        "consent_tokens": tokens,
        "use_context_personalization": True,
        "excel_file_data": excel_data,
        "excel_file_name": "test_contacts.xlsx"
    }
    
    print("\n📤 Testing campaign creation with valid token format...")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8001/agents/mailerpanda/mass-email",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response received!")
            print(f"📊 Status: {result.get('status')}")
            print(f"📊 Campaign ID: {result.get('campaign_id')}")
            print(f"📊 Requires Approval: {result.get('requires_approval')}")
            print(f"📊 Processing Time: {result.get('processing_time')}s")
            
            if result.get('status') == 'awaiting_approval':
                print("🎉 SUCCESS: Workflow is properly awaiting approval!")
                print("✅ No infinite loop - waiting for user decision")
            elif result.get('status') == 'permission_denied':
                print("🔒 Permission denied - consent validation failed")
                print("ℹ️  This is expected with test tokens")
            else:
                print(f"ℹ️  Workflow status: {result.get('status')}")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            result = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            print(f"Response: {result}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - possible infinite loop!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_valid_tokens()
