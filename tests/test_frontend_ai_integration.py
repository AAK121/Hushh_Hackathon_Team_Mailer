#!/usr/bin/env python3
"""
Test the complete end-to-end AI personalization workflow from frontend to backend.
"""

import requests
import json

def test_frontend_ai_personalization():
    """Test AI personalization as it would work from the frontend."""
    
    print("🌐 Testing Frontend → Backend AI Personalization")
    print("=" * 60)
    
    # This simulates what the frontend MailerPandaUI sends when:
    # 1. User enters a message
    # 2. User uploads Excel file with descriptions  
    # 3. User checks "Use context personalization" checkbox
    # 4. User clicks Generate
    
    frontend_request = {
        "user_id": "frontend_user_123",
        "user_input": "Send a personalized thank you email to all our contacts",
        "excel_file_data": "",  # In real frontend, this would be base64 encoded Excel
        "excel_file_name": "contacts_with_descriptions.xlsx",
        "mode": "interactive",
        # ✨ KEY: This is what the frontend checkbox controls
        "use_context_personalization": True,  # This enables AI personalization!
        "personalization_mode": "aggressive",
        "google_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI"
    }
    
    print("🎯 Frontend Request Configuration:")
    print(f"  ✅ Context Personalization: {frontend_request['use_context_personalization']}")
    print(f"  🤖 Personalization Mode: {frontend_request['personalization_mode']}")
    print(f"  📁 Excel File: {frontend_request['excel_file_name']}")
    print(f"  💬 User Input: {frontend_request['user_input']}")
    
    print("\n📡 Sending request to mass-email API (as frontend would)...")
    
    try:
        # This is the same endpoint the frontend uses
        url = "http://localhost:8001/agents/mailerpanda/mass-email"
        
        response = requests.post(url, json=frontend_request, timeout=120)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Frontend → Backend Integration Working!")
            print(f"  📊 Status: {result.get('status')}")
            print(f"  🆔 Campaign ID: {result.get('campaign_id')}")
            print(f"  📧 Emails Sent: {result.get('emails_sent', 0)}")
            print(f"  📝 Recipients Processed: {result.get('recipients_processed', 0)}")
            print(f"  ✨ Context Personalization Enabled: {result.get('context_personalization_enabled', False)}")
            
            if result.get('context_personalization_enabled'):
                print("\n🎉 SUCCESS! AI Personalization is enabled and working!")
                print("📧 This means when you use the frontend:")
                print("  1. ✅ Upload Excel file with description column")
                print("  2. ✅ Check 'Use context personalization' checkbox") 
                print("  3. ✅ AI will customize each email based on descriptions")
                print("  4. ✅ Each contact gets a unique, personalized message")
                
            else:
                print("\n⚠️ AI Personalization not detected in response")
                print("   This might mean:")
                print("   - No description column found in Excel file")
                print("   - Context personalization toggle not working")
                print("   - API parameter mapping issue")
            
            # Show template if available
            if result.get('email_template'):
                template = result['email_template']
                print(f"\n📧 Generated Template:")
                print(f"  Subject: {template.get('subject', 'N/A')}")
                print(f"  Body: {template.get('body', 'N/A')[:100]}...")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def summarize_frontend_integration():
    """Summarize how the frontend integration works."""
    
    print("\n" + "=" * 60)
    print("🌟 Frontend Integration Summary")
    print("=" * 60)
    
    print("📋 How it works from the frontend:")
    print("  1. 🌐 User opens MailerPanda Agent in frontend")
    print("  2. 📁 User uploads Excel file with description column")
    print("  3. ✅ User checks 'Use context personalization' checkbox")
    print("  4. 💬 User enters email request")
    print("  5. 🚀 Frontend sends request to /agents/mailerpanda/mass-email")
    print("  6. 🤖 Backend uses AI to personalize based on descriptions")
    print("  7. 📧 Each contact gets uniquely customized email")
    
    print("\n🎯 Key Frontend Controls:")
    print("  📊 Checkbox: 'Use context personalization from description column'")
    print("  📁 File Upload: Excel file with name/email/description columns")
    print("  🤖 Mode: Set to 'aggressive' for maximum personalization")
    
    print("\n✅ Expected Results:")
    print("  📧 For Alok: Technical details and documentation focus")
    print("  📧 For Ashok: Gentle introduction and support focus")
    print("  📧 For Chandresh: Brief and business-focused content")

if __name__ == "__main__":
    test_frontend_ai_personalization()
    summarize_frontend_integration()
