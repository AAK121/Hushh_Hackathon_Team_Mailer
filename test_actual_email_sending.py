#!/usr/bin/env python3
"""
Test actual email sending capabilities with real Mailjet credentials from the notebook
"""

import requests
import json
from datetime import datetime

# API endpoint
API_BASE = "http://localhost:8002"

def test_mailerpanda_actual_sending():
    """Test the MailerPanda API with actual email sending using real credentials."""
    
    # Using the actual Mailjet credentials from the notebook
    test_request = {
        "user_id": "test_user_email_001",
        "consent_tokens": {
            "email.send": "test_token_123",
            "data.process": "test_token_456",
            "vault.read.email": "test_token_789",
            "vault.write.email": "test_token_101"
        },
        "user_input": "Send a congratulatory email to our team members about the successful completion of the MailerPanda personalization feature. Include personalized messages based on their roles.",
        "mode": "headless",  # Try headless mode to avoid user interaction
        "enable_description_personalization": True,
        "excel_file_path": "hushh_mcp/agents/mailerpanda/email_list_with_descriptions.xlsx",
        "personalization_mode": "smart",
        
        # Real Mailjet credentials from the notebook
        "mailjet_api_key": "cca56ed08f5272f813370d7fc5a34a24",
        "mailjet_api_secret": "60fb43675233e2ac775f1c6cb8fe455c",
        
        # Real Google API key from the notebook
        "google_api_key": "AIzaSyAYIuaAQJxmuspF5tyDEpJ3iYm6gVVQZOo",
        
        # Additional parameters for email sending
        "sender_email": "dragnoid121@gmail.com",
        "sender_name": "MailerPanda Team",
        "recipient_emails": [
            "test.mailerpanda@gmail.com",  # Safe test email
            "dragnoid121@gmail.com"        # From the notebook examples
        ],
        "require_approval": False,  # Skip approval for testing
        "use_ai_generation": True
    }
    
    print("🧪 Testing MailerPanda API with Real Email Sending...")
    print(f"📊 Request Data: {json.dumps(test_request, indent=2)}")
    
    try:
        # Test the API endpoint
        response = requests.post(
            f"{API_BASE}/agents/mailerpanda/execute",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for email sending
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ API Response:")
            print(json.dumps(response_data, indent=2))
            
            # Check email sending results
            emails_sent = response_data.get("emails_sent", 0)
            send_status = response_data.get("send_status", [])
            
            print(f"\n📧 Email Sending Results:")
            print(f"   Emails Sent: {emails_sent}")
            
            if send_status:
                print(f"   Send Status Details:")
                for status in send_status:
                    print(f"     - {status}")
            
            # Check personalization results
            personalized_count = response_data.get("personalized_count", 0)
            standard_count = response_data.get("standard_count", 0)
            description_detected = response_data.get("description_column_detected", False)
            
            print(f"\n🎯 Personalization Results:")
            print(f"   Personalized Emails: {personalized_count}")
            print(f"   Standard Emails: {standard_count}")
            print(f"   Description Column Detected: {description_detected}")
            
            # Check for errors
            errors = response_data.get("errors", [])
            if errors:
                print(f"\n❌ Errors Encountered:")
                for error in errors:
                    print(f"     - {error}")
            
            # Check processing time
            processing_time = response_data.get("processing_time", 0)
            print(f"\n⏱️ Processing Time: {processing_time:.2f} seconds")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error Details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("🔌 Connection Error: Make sure the API server is running on port 8002")
        print("💡 Start the server with: python -m uvicorn api:app --host 127.0.0.1 --port 8002")
    except requests.exceptions.Timeout:
        print("⏰ Request Timeout: Email sending may take longer than expected")
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")

def test_interactive_mode():
    """Test with interactive mode to see approval workflow."""
    
    test_request = {
        "user_id": "test_user_interactive_001",
        "consent_tokens": {
            "email.send": "test_token_123",
            "data.process": "test_token_456"
        },
        "user_input": "Send a test email to check if our personalization feature is working correctly",
        "mode": "interactive",  # This should trigger approval workflow
        "enable_description_personalization": True,
        "excel_file_path": "hushh_mcp/agents/mailerpanda/email_list_with_descriptions.xlsx",
        "personalization_mode": "smart",
        "mailjet_api_key": "cca56ed08f5272f813370d7fc5a34a24",
        "mailjet_api_secret": "60fb43675233e2ac775f1c6cb8fe455c",
        "google_api_key": "AIzaSyAYIuaAQJxmuspF5tyDEpJ3iYm6gVVQZOo"
    }
    
    print("\n🔄 Testing Interactive Mode (Approval Workflow)...")
    
    try:
        response = requests.post(
            f"{API_BASE}/agents/mailerpanda/execute",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ Interactive Mode Response:")
            print(json.dumps(response_data, indent=2))
            
            # Check if approval is required
            requires_approval = response_data.get("requires_approval", False)
            campaign_id = response_data.get("campaign_id")
            
            if requires_approval and campaign_id:
                print(f"\n✋ Approval Required for Campaign: {campaign_id}")
                print("📧 Email template generated and waiting for approval")
                
                # Show email template if available
                email_template = response_data.get("email_template", {})
                if email_template:
                    print(f"📝 Generated Email Template:")
                    print(f"   Subject: {email_template.get('subject', 'N/A')}")
                    print(f"   Content Preview: {email_template.get('content', 'N/A')[:200]}...")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error Details: {response.text}")
            
    except Exception as e:
        print(f"❌ Interactive Test Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 MailerPanda Email Sending Test with Real Credentials")
    print("=" * 60)
    
    # Test 1: Headless mode with email sending
    test_mailerpanda_actual_sending()
    
    print("\n" + "=" * 60)
    
    # Test 2: Interactive mode to see approval workflow
    test_interactive_mode()
    
    print("\n✅ Email sending tests completed!")
    print("💡 Check your email inbox for test messages if emails were sent successfully")
