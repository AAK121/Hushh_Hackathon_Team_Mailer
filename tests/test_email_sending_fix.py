#!/usr/bin/env python3
"""
Test email sending afterdef create_test_excel():
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
        return tmp_file.nameLI input blocking issue.
This test verifies that emails are actually sent via the API.
"""

import requests
import json
import time
import base64
import pandas as pd
import tempfile
import os

# API endpoint
BASE_URL = "http://localhost:8001"

def generate_consent_tokens():
    """Generate proper consent tokens for the test."""
    try:
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        user_id = "test_user_fix"
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
                    expires_in_ms=3600000  # 1 hour
                )
                consent_tokens[scope.value] = token_obj.token
                print(f"✅ Generated token for {scope.value}")
            except Exception as e:
                print(f"❌ Failed to generate token for {scope.value}: {e}")
        
        return consent_tokens, user_id
    except Exception as e:
        print(f"❌ Failed to generate consent tokens: {e}")
        return {}, "test_user_fix"

def create_test_excel():
    """Create a test Excel file with contacts."""
    data = {
        'Name': ['Test User 1', 'Test User 2'],
        'Email': ['test1@example.com', 'test2@example.com'],
        'description': ['Testing email 1', 'Testing email 2']  # lowercase 'description'
    }
    df = pd.DataFrame(data)
    
    # Create temporary Excel file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        return tmp_file.name

def encode_excel_file(file_path):
    """Encode Excel file to base64."""
    with open(file_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    return encoded

def test_email_sending():
    """Test the email sending functionality."""
    print("🧪 Testing Email Sending After CLI Fix")
    print("=" * 50)
    
    # Generate proper consent tokens
    print("🔐 Generating consent tokens...")
    consent_tokens, user_id = generate_consent_tokens()
    
    if not consent_tokens:
        print("❌ Failed to generate consent tokens - test cannot proceed")
        return False
    
    # Create test Excel file
    excel_path = create_test_excel()
    excel_data = encode_excel_file(excel_path)
    
    # Test data
    test_request = {
        "user_id": user_id,
        "consent_tokens": consent_tokens,  # Use real consent tokens
        "user_input": "Send a test email to verify the CLI fix is working",
        "mode": "interactive",  # This should now work without CLI blocking
        "use_context_personalization": True,
        "personalization_mode": "conservative",
        "excel_file_data": excel_data,
        "excel_filename": "test_contacts.xlsx"
    }
    
    try:
        print("📤 Sending mass email request...")
        response = requests.post(
            f"{BASE_URL}/agents/mailerpanda/mass-email",
            json=test_request,
            timeout=180  # 3 minutes timeout
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Call Successful!")
            print(f"Campaign ID: {result.get('campaign_id')}")
            print(f"Status: {result.get('status')}")
            print(f"Emails Sent: {result.get('emails_sent', 0)}")
            print(f"Personalized Count: {result.get('personalized_count', 0)}")
            print(f"Standard Count: {result.get('standard_count', 0)}")
            print(f"Requires Approval: {result.get('requires_approval', False)}")
            print(f"Approval Status: {result.get('approval_status', 'N/A')}")
            
            # Show Excel analysis details
            excel_analysis = result.get('excel_analysis', {})
            print(f"\n📊 Excel Analysis:")
            print(f"  File Uploaded: {excel_analysis.get('file_uploaded', False)}")
            print(f"  Total Contacts: {excel_analysis.get('total_contacts', 0)}")
            print(f"  Columns Found: {excel_analysis.get('columns_found', [])}")
            print(f"  Description Column Exists: {excel_analysis.get('description_column_exists', False)}")
            print(f"  Contacts with Descriptions: {excel_analysis.get('contacts_with_descriptions', 0)}")
            print(f"  Context Toggle Status: {excel_analysis.get('context_toggle_status', 'N/A')}")
            
            # Check if emails were actually sent
            if result.get('emails_sent', 0) > 0:
                print("🎉 SUCCESS: Emails were sent! CLI blocking issue fixed!")
                return True
            else:
                print("⚠️ WARNING: No emails sent - checking status...")
                if result.get('status') == 'awaiting_send_approval':
                    print("❌ Still awaiting approval - backend issue not fully fixed")
                elif excel_analysis.get('total_contacts', 0) == 0:
                    print("❌ No contacts found in Excel file - file processing issue")
                else:
                    print("❌ Contacts found but emails not sent - sending logic issue")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error Details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - server might be processing")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(excel_path):
            os.unlink(excel_path)

def test_server_availability():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔍 Checking server availability...")
    if not test_server_availability():
        print("❌ Server not available at http://localhost:8000")
        print("Please start the server first with: python api.py")
        exit(1)
    
    print("✅ Server is running")
    print()
    
    # Wait a moment for server to be fully ready
    time.sleep(2)
    
    # Run the test
    success = test_email_sending()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST PASSED: Email sending is working!")
    else:
        print("❌ TEST FAILED: Email sending still has issues")
