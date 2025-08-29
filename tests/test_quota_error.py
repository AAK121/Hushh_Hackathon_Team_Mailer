#!/usr/bin/env python3
"""
Test script to reproduce the Google API quota error
"""
import requests
import json

# Test minimal request to reproduce the quota error
test_request = {
    "user_id": "test_user",
    "user_input": "Create a welcome email for new subscribers",
    "consent_tokens": {
        "vault.read.email": "test_token",
        "vault.write.email": "test_token",
        "vault.read.file": "test_token", 
        "vault.write.file": "test_token",
        "custom.temporary": "test_token"
    },
    "mode": "interactive",
    "require_approval": False,
    "use_ai_generation": True,
    "use_context_personalization": False,
    "excel_file_data": "",
    "excel_file_name": ""
}

try:
    print("🧪 Testing mass-email endpoint...")
    response = requests.post(
        'http://127.0.0.1:8001/agents/mailerpanda/mass-email',
        headers={'Content-Type': 'application/json'},
        json=test_request,
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data}")
    else:
        print(f"❌ Error Response: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request Exception: {e}")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
