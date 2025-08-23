#!/usr/bin/env python3
"""
Test script to simulate a working response vs a quota error response
"""
import requests
import json

def test_working_response():
    """Test with valid tokens to see normal flow"""
    print("🧪 Testing normal response flow...")
    
    test_request = {
        "user_id": "test_user",
        "user_input": "Create a simple welcome email",
        "consent_tokens": {
            "vault.read.email": "valid_token",
            "vault.write.email": "valid_token",
            "vault.read.file": "valid_token", 
            "vault.write.file": "valid_token",
            "custom.temporary": "valid_token"
        },
        "mode": "interactive",
        "require_approval": False,
        "use_ai_generation": True,
        "use_context_personalization": False,
        "excel_file_data": "",
        "excel_file_name": ""
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:8001/agents/mailerpanda/mass-email',
            headers={'Content-Type': 'application/json'},
            json=test_request,
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response Status: {data.get('status')}")
            print(f"   Campaign ID: {data.get('campaign_id')}")
            print(f"   Errors: {data.get('errors')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Backend Response Handling")
    print("="*50)
    
    success = test_working_response()
    
    if success:
        print("\n✅ Backend is responding properly!")
        print("💡 The issue was likely the numpy serialization error (now fixed)")
        print("💡 Frontend should now receive proper responses")
    else:
        print("\n❌ Backend still has issues")
        
    print("\n📋 Next steps:")
    print("1. Test the frontend with the improved timeout handling")
    print("2. Check if multiple requests are being sent")
    print("3. Verify the campaign ID is not being reused")
