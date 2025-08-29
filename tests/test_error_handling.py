#!/usr/bin/env python3
"""
Test script to verify that the improved error handling works for Google API quota errors
"""
import requests
import json

# Test request that should trigger AI generation (and potentially quota error)
test_request = {
    "user_id": "test_user",
    "user_input": "Create a welcome email for new subscribers to our newsletter",
    "consent_tokens": {
        "vault.read.email": "test_token_read_email",
        "vault.write.email": "test_token_write_email", 
        "vault.read.file": "test_token_read_file",
        "vault.write.file": "test_token_write_file",
        "custom.temporary": "test_token_temporary"
    },
    "mode": "interactive",
    "require_approval": False,
    "use_ai_generation": True,
    "use_context_personalization": False,
    "excel_file_data": "bmFtZSxlbWFpbCxkZXNjcmlwdGlvbgpKb2huIERvZSxqb2huQHRlc3QuY29tLFRlc3QgdXNlciBmb3IgZGVtbw==",  # Base64 for basic CSV
    "excel_file_name": "test_contacts.csv",
    "google_api_key": "test_key_that_will_cause_quota_error"
}

try:
    print("🧪 Testing improved error handling...")
    print("📝 This should trigger Google API quota error and return proper error response")
    
    response = requests.post(
        'http://127.0.0.1:8001/agents/mailerpanda/mass-email',
        headers={'Content-Type': 'application/json'},
        json=test_request,
        timeout=30
    )
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response received successfully")
        print(f"   Status: {data.get('status')}")
        print(f"   Errors: {data.get('errors')}")
        print(f"   Message: {data.get('message')}")
        
        if data.get('status') == 'error' and data.get('errors'):
            print("✅ Error handling working correctly!")
        else:
            print("⚠️  Expected error status but got different response")
            
    elif response.status_code == 500:
        print("❌ Server crashed (500 error) - error handling not working")
        print(f"   Response: {response.text}")
    else:
        print(f"📄 Response: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request Exception: {e}")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
