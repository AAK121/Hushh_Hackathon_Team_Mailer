#!/usr/bin/env python3
"""
Test the MailerPanda agent with placeholder replacement fix.
"""

import requests
import json

def test_mailerpanda_with_placeholders():
    """Test the MailerPanda agent API with a template containing placeholders."""
    
    print("🧪 Testing MailerPanda Agent with Placeholders")
    print("=" * 60)
    
    # API endpoint
    url = "http://localhost:8001/agents/mailerpanda/execute"
    
    # Test data with placeholders
    test_data = {
        "user_id": "test_user_123",
        "consent_tokens": {
            "content_generation": "temp_token_content",
            "email_sending": "temp_token_email", 
            "contact_management": "temp_token_contacts"
        },
        "user_input": "Send a personalized thank you email to all contacts based on their descriptions",
        "mode": "headless",
        "frontend_approved": True,
        "send_approved": True,
        "pre_approved_template": """Dear {name},

I am writing to express my sincere appreciation based on the {description} you provided.

We value your interest in our services and look forward to working with you.

Thank you for your time and effort.

Sincerely,
The MailerPanda Team""",
        "pre_approved_subject": "Thank you for your interest, {name}!"
    }
    
    print("📤 Sending request to MailerPanda API...")
    print(f"📧 Template includes placeholders: {{name}} and {{description}}")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response:")
            print(json.dumps(result, indent=2))
            
            if "total_sent" in result:
                print(f"\n🎉 SUCCESS! Emails sent: {result['total_sent']}")
                print("📧 Check your inbox - placeholders should now be replaced!")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_mailerpanda_with_placeholders()
