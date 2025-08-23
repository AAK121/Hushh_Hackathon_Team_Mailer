#!/usr/bin/env python3
"""
Test the MailerPanda API with real HCT tokens
"""

import requests
import json

def test_mailerpanda_with_hct_tokens():
    """Test the MailerPanda API with real cryptographic HCT tokens."""
    
    # Real HCT tokens generated for frontend_user_123
    consent_tokens = {
        'vault.read.email': 'HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQucmVhZC5lbWFpbHwxNzU1OTQ1MDk5MDQzfDE3NTYwMzE0OTkwNDM=.b557087d1e18f9ebb87caf02c677c64260d694ad2a22efef5b05ba530758bf25',
        'vault.write.email': 'HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQud3JpdGUuZW1haWx8MTc1NTk0NTA5OTA0M3wxNzU2MDMxNDk5MDQz.38f2beedbf850635a2fd13272daf0ba10da6e8d80b0b6ea382f2cdd88f8d4a19',
        'vault.read.file': 'HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQucmVhZC5maWxlfDE3NTU5NDUwOTkwNDN8MTc1NjAzMTQ5OTA0Mw==.efb46eced3aa4d4d3e5e5f565bb8df654189e5ad8aba86d77ac6c749566dc286',
        'vault.write.file': 'HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQud3JpdGUuZmlsZXwxNzU1OTQ1MDk5MDQzfDE3NTYwMzE0OTkwNDM=.387dd564813ac3be6fc09176bf5d4dae4b70f1aaf9051b8c06d6f1bdcc7b8aa4',
        'custom.temporary': 'HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8Y3VzdG9tLnRlbXBvcmFyeXwxNzU1OTQ1MDk5MDQzfDE3NTYwMzE0OTkwNDM=.cc9f3db85ae6ecfca369da582ecc248ad1c6de6c1824ed79a9d5d971c7e3410f'
    }
    
    # Prepare test data
    test_data = {
        "user_id": "frontend_user_123",  # Match the user_id in the tokens
        "user_input": "Send a welcome email to new subscribers",
        "excel_file_data": "",  # Empty for this test
        "excel_file_name": "",
        "mode": "interactive",
        "consent_tokens": consent_tokens
    }
    
    print("🔍 Testing MailerPanda API with Real HCT Tokens")
    print("=" * 60)
    print(f"Backend URL: http://127.0.0.1:8001/agents/mailerpanda/mass-email")
    print(f"User ID: {test_data['user_id']}")
    print(f"Mode: {test_data['mode']}")
    print(f"Consent Tokens: {len(consent_tokens)} tokens provided")
    print("-" * 60)
    
    try:
        # Send the request with a longer timeout and smaller test case
        response = requests.post(
            "http://127.0.0.1:8001/agents/mailerpanda/mass-email",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=60  # Increased timeout
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")
        
        # Print the raw response for debugging
        response_text = response.text
        print(f"📄 Raw Response: {response_text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("🎉 SUCCESS! API Request Successful")
                print(f"📋 Campaign ID: {result.get('campaign_id', 'N/A')}")
                print(f"📊 Status: {result.get('status', 'N/A')}")
                print(f"👥 Recipient Count: {result.get('recipient_count', 'N/A')}")
                print(f"✉️ Email Subject: {result.get('email_template', {}).get('subject', 'N/A')}")
                print("\n📝 Generated Email Body:")
                print("-" * 40)
                print(result.get('email_template', {}).get('body', 'N/A'))
                print("-" * 40)
                
                # Check if there are any errors in the response
                if result.get('status') == 'error':
                    print(f"\n❌ API returned error status")
                    print(f"🔍 Error details: {result}")
                    return False
                    
                return True
            except Exception as e:
                print(f"💥 JSON parsing error: {e}")
                return False
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"📄 Response Text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"🚨 Connection Error: {e}")
        return False
    except Exception as e:
        print(f"💥 Unexpected Error: {e}")
        return False

def main():
    """Main test function."""
    print("🐼 MailerPanda HCT Token Integration Test")
    print("=" * 60)
    
    success = test_mailerpanda_with_hct_tokens()
    
    if success:
        print("\n🚀 Integration test completed successfully!")
        print("✅ Frontend can now use these tokens for API calls")
        print("🌐 Frontend URL: http://localhost:5174")
        print("🔗 Backend URL: http://127.0.0.1:8001")
    else:
        print("\n❌ Integration test failed!")
        print("🔧 Check backend logs for more details")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
