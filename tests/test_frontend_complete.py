#!/usr/bin/env python3
"""
Test the frontend AI personalization with proper consent tokens.
"""

import requests
import json

def test_frontend_with_consent():
    """Test with proper consent tokens as the frontend sends."""
    
    print("🔐 Testing Frontend AI Personalization with Consent Tokens")
    print("=" * 65)
    
    # This exactly matches what MailerPandaUI.tsx sends
    frontend_request = {
        "user_id": "frontend_user_123",
        "user_input": "Send a personalized thank you email to all our contacts based on their individual descriptions",
        "excel_file_data": "",  # Empty for now, but frontend would populate this
        "excel_file_name": "contacts_with_descriptions.xlsx",
        "mode": "interactive",
        "use_context_personalization": True,  # ✨ This enables AI personalization!
        "personalization_mode": "aggressive",
        "google_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI",
        "mailjet_api_key": "cca56ed08f5272f813370d7fc5a34a24",
        "mailjet_api_secret": "60fb43675233e2ac775f1c6cb8fe455c",
        "consent_tokens": {
            "vault.read.email": "HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQucmVhZC5lbWFpbHwxNzU1OTQ2MzA5NjU0fDE3NTYwMzI3MDk2NTQ=.e98cb6fe90a9d4a6ded5bf2a37b25028d1ea82a7e5dde4223552a312dba75b36",
            "vault.write.email": "HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQud3JpdGUuZW1haWx8MTc1NTk0NjMwOTY1NHwxNzU2MDMyNzA5NjU0.107cf985c5c82413b218a436e8206856b1f982e37a70d6c5ab2fabd97c0ef60e",
            "vault.read.file": "HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQucmVhZC5maWxlfDE3NTU5NDYzMDk2NTR8MTc1NjAzMjcwOTY1NA==.5549616fd68e1a507ff89e18692134c8301d40ec077df18e62b803059ca17642",
            "vault.write.file": "HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQud3JpdGUuZmlsZXwxNzU1OTQ2MzA5NjU1fDE3NTYwMzI3MDk2NTU=.42fe283d1d7e27c05b31ad2b1370aac464e9b15c1a7b4740de335e349b5ee817",
            "custom.temporary": "HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8Y3VzdG9tLnRlbXBvcmFyeXwxNzU1OTQ2MzA5NjU1fDE3NTYwMzI3MDk2NTU=.2c80196d5ae2f4709ee0c4b08531cacd15221bbee1c4a441a7f2b754e291e4d2"
        }
    }
    
    print("🎯 Configuration:")
    print(f"  ✅ AI Personalization: {frontend_request['use_context_personalization']}")
    print(f"  🤖 Mode: {frontend_request['personalization_mode']}")
    print(f"  🔐 Consent Tokens: {len(frontend_request['consent_tokens'])} provided")
    print(f"  📁 Excel File: {frontend_request['excel_file_name']}")
    
    print("\n📡 Sending frontend request...")
    
    try:
        url = "http://localhost:8001/agents/mailerpanda/mass-email"
        response = requests.post(url, json=frontend_request, timeout=120)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS! Frontend Integration Working!")
            print(f"  📊 Status: {result.get('status')}")
            print(f"  🆔 Campaign ID: {result.get('campaign_id')}")
            print(f"  📧 Emails Sent: {result.get('emails_sent', 0)}")
            print(f"  ✨ Context Personalization: {result.get('context_personalization_enabled', False)}")
            print(f"  📝 Recipients Processed: {result.get('recipients_processed', 0)}")
            print(f"  ⏱️ Processing Time: {result.get('processing_time', 0):.2f}s")
            
            if result.get('context_personalization_enabled'):
                print("\n🎉 AI PERSONALIZATION IS ACTIVE!")
                print("📧 The agent is using descriptions to customize emails!")
                
            if result.get('requires_approval'):
                print("\n✅ Campaign ready for approval via frontend")
                print("📧 Template has been generated and awaits user approval")
                
                # Show the generated template
                if result.get('email_template'):
                    template = result['email_template']
                    print(f"\n📧 Generated Template:")
                    print(f"  Subject: {template.get('subject', 'N/A')}")
                    print(f"  Body: {template.get('body', 'N/A')[:200]}...")
                    
            else:
                print(f"\n📧 Emails sent immediately: {result.get('emails_sent', 0)}")
                
        elif response.status_code == 422:
            print("❌ Validation Error (422)")
            error_detail = response.json()
            print(f"   Details: {error_detail}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def explain_frontend_flow():
    """Explain the complete frontend flow."""
    
    print("\n" + "=" * 65)
    print("🌟 Complete Frontend Flow Explanation")
    print("=" * 65)
    
    print("📱 Frontend User Experience:")
    print("  1. 🌐 User opens MailerPanda Agent")
    print("  2. 📁 User uploads Excel file with description column:")
    print("     - name: Contact names") 
    print("     - email: Email addresses")
    print("     - description: AI personalization context")
    print("  3. ✅ User enables 'Use context personalization' checkbox")
    print("  4. 💬 User enters email campaign description")
    print("  5. 🚀 User clicks Generate/Send")
    
    print("\n🔧 Technical Flow:")
    print("  1. 📡 Frontend sends request to /agents/mailerpanda/mass-email")
    print("  2. 🔐 Backend validates consent tokens")
    print("  3. 📂 Backend reads Excel file and detects description column")
    print("  4. 🤖 AI generates base template from user input")
    print("  5. ✨ AI personalizes each email using individual descriptions")
    print("  6. 📧 Each contact receives uniquely customized content")
    
    print("\n🎯 Key Result:")
    print("  📧 Instead of: 'Dear John, Thank you for your partnership...'")
    print("  📧 You get: 'Dear John, Given your technical background and")
    print("     preference for detailed documentation, I wanted to...'")

if __name__ == "__main__":
    test_frontend_with_consent()
    explain_frontend_flow()
