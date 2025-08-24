#!/usr/bin/env python3
"""
End-to-end test for MailerPanda placeholder replacement.
This test will verify that templates with placeholders get properly personalized.
"""

import requests
import json
import sys
import os

def test_end_to_end_placeholders():
    """Test the complete placeholder replacement workflow."""
    
    print("🚀 End-to-End MailerPanda Placeholder Test")
    print("=" * 60)
    
    # Test with a template that has placeholders
    test_data = {
        "user_id": "test_user_placeholders",
        "consent_tokens": {
            "content_generation": "test_token_content_123",
            "email_sending": "test_token_email_123", 
            "contact_management": "test_token_contacts_123"
        },
        "user_input": "Send a personalized appreciation email to all contacts",
        "mode": "headless",
        "frontend_approved": True,
        "send_approved": True,
        "pre_approved_template": """Dear {name},

I hope this email finds you well! I wanted to personally reach out to express my sincere appreciation based on the {description} context.

Your association with {company_name} has been valuable to us.

Thank you for your continued trust and partnership.

Best regards,
The MailerPanda Team

---
Email sent to: {email}""",
        "pre_approved_subject": "Thank you for your partnership, {name}!",
        # Use the file with descriptions
        "excel_file_path": r"c:\Users\Asus\Desktop\Pda_mailer\hushh_mcp\agents\mailerpanda\email_list_with_descriptions.xlsx",
        "enable_description_personalization": True,
        "personalization_mode": "conservative"
    }
    
    print("📧 Template with placeholders:")
    print("  - {name}")
    print("  - {description}")  
    print("  - {company_name}")
    print("  - {email}")
    print("\n📤 Sending API request...")
    
    try:
        url = "http://localhost:8001/agents/mailerpanda/execute"
        response = requests.post(url, json=test_data, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Response Summary:")
            print(f"  📊 Status: {result.get('status')}")
            print(f"  📧 Emails Sent: {result.get('emails_sent', 0)}")
            print(f"  ❌ Failed: {result.get('standard_count', 0) - result.get('emails_sent', 0)}")
            print(f"  📝 Personalized Count: {result.get('personalized_count', 0)}")
            print(f"  📋 Description Column Detected: {result.get('description_column_detected', False)}")
            
            if result.get('emails_sent', 0) > 0:
                print("\n🎉 SUCCESS! Emails were sent with placeholder replacement!")
                print("📧 Check the inboxes of:")
                print("  - alokkale121@gmail.com (Alok)")
                print("  - kaleashok92@gmail.com (Ashok)")
                print("  - chandresht149@gmail.com (Chandresh)")
                print("\n✅ The emails should now contain:")
                print("  - Actual names instead of {name}")
                print("  - Actual descriptions instead of {description}")
                print("  - Actual company names instead of {company_name}")
                print("  - Actual email addresses instead of {email}")
            else:
                print("\n⚠️ No emails were sent. Possible reasons:")
                print("  1. Mailjet API keys not configured")
                print("  2. Email validation failed")
                print("  3. Consent validation failed")
                print("  4. Rate limiting")
                
                # Show detailed response for debugging
                print(f"\n🔍 Full Response:")
                print(json.dumps(result, indent=2))
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_end_to_end_placeholders()
