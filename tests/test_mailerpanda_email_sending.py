#!/usr/bin/env python3
"""
Test actual email sending capabilities of MailerPanda agent
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the actual MailerPanda agent
from hushh_mcp.agents.mailerpanda.index import MassMailerAgent

def test_mailerpanda_email_sending():
    """Test the actual MailerPanda agent email sending functionality."""
    
    print("🧪 Testing Actual MailerPanda Email Sending")
    print("=" * 50)
    
    # Real API credentials (from your notebook)
    api_keys = {
        'google_api_key': 'AIzaSyDZ7zdMZE-HDGsJAVEMQBo6PF7HppI7HDQ',
        'mailjet_api_key': '72aa1e9f80b97bb74e71c4aa6e5c6e44',
        'mailjet_api_secret': '4bc7b4ced53de9e6ace69ad90aade5d8'
    }
    
    print(f"🔑 Using API Keys:")
    print(f"  Google API Key: {api_keys['google_api_key'][:20]}...")
    print(f"  Mailjet API Key: {api_keys['mailjet_api_key'][:20]}...")
    print(f"  Mailjet Secret: {api_keys['mailjet_api_secret'][:20]}...")
    
    try:
        # Initialize the agent with real credentials
        agent = MassMailerAgent(api_keys=api_keys)
        print("✅ Agent initialized successfully")
        
        # Test consent tokens (demo tokens for testing)
        consent_tokens = {
            "vault.read.email": "demo_token_read_email_123",
            "vault.write.email": "demo_token_write_email_456", 
            "vault.read.file": "demo_token_read_file_789",
            "vault.write.file": "demo_token_write_file_012",
            "custom.temporary": "demo_token_temporary_345"
        }
        
        # User input for email campaign
        user_input = """
        Send a promotional email about our new AI-powered email personalization service.
        
        The email should:
        - Introduce our MailerPanda service
        - Highlight the description-based personalization feature
        - Include a call-to-action to try the service
        - Use a professional but friendly tone
        
        Send to: test@example.com
        Subject: Introducing MailerPanda - AI-Powered Email Personalization
        """
        
        print(f"\n📧 Testing Email Campaign:")
        print(f"User Input: {user_input[:100]}...")
        
        # Test with personalization enabled
        print(f"\n🎯 Testing with Description-Based Personalization:")
        result = agent.handle(
            user_id="test_user_email_001",
            consent_tokens=consent_tokens,
            user_input=user_input,
            mode="interactive",  # Use demo mode for testing
            enable_description_personalization=True,
            excel_file_path="email_list_with_descriptions.xlsx",
            personalization_mode="smart"
        )
        
        print(f"\n📊 Agent Result:")
        print(f"Status: {result.get('status', 'Unknown')}")
        
        if 'email_template' in result:
            template = result['email_template']
            print(f"\n📧 Generated Email Template:")
            print(f"Subject: {template.get('subject', 'No subject')}")
            print(f"Body Preview: {str(template.get('body', 'No body'))[:200]}...")
        
        if 'emails_sent' in result:
            print(f"\n📤 Emails Sent: {result['emails_sent']}")
            
        if 'send_status' in result:
            print(f"📋 Send Status: {result['send_status']}")
            
        # Check personalization stats
        if 'personalized_count' in result:
            print(f"\n🎯 Personalization Statistics:")
            print(f"  Personalized Emails: {result.get('personalized_count', 0)}")
            print(f"  Standard Emails: {result.get('standard_count', 0)}")
            print(f"  Description Column Detected: {result.get('description_column_detected', False)}")
            
        if 'errors' in result and result['errors']:
            print(f"\n⚠️ Errors: {result['errors']}")
            
        # Test direct email sending capability
        print(f"\n📧 Testing Direct Email Send:")
        if hasattr(agent, '_send_email'):
            try:
                direct_result = agent._send_email(
                    to_email="test@example.com",
                    subject="MailerPanda Test Email",
                    html_content="<h1>Test Email</h1><p>This is a test email from MailerPanda agent.</p>",
                    from_email="noreply@mailerpanda.com",
                    from_name="MailerPanda Test"
                )
                print(f"✅ Direct email send result: {direct_result}")
            except Exception as e:
                print(f"❌ Direct email send error: {str(e)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Agent Test Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_mailjet_connection():
    """Test direct Mailjet API connection."""
    
    print(f"\n🔗 Testing Direct Mailjet Connection")
    print("=" * 40)
    
    try:
        from mailjet_rest import Client
        
        # Initialize Mailjet client with your credentials
        mailjet = Client(
            auth=('72aa1e9f80b97bb74e71c4aa6e5c6e44', '4bc7b4ced53de9e6ace69ad90aade5d8'),
            version='v3.1'
        )
        
        # Test email data
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "noreply@mailerpanda.com",
                        "Name": "MailerPanda Test"
                    },
                    "To": [
                        {
                            "Email": "test@example.com",
                            "Name": "Test Recipient"
                        }
                    ],
                    "Subject": "MailerPanda Direct Test",
                    "TextPart": "Hello from MailerPanda! This is a direct test email.",
                    "HTMLPart": "<h1>Hello from MailerPanda!</h1><p>This is a direct test email from the MailerPanda service.</p><p>If you receive this, the email functionality is working correctly.</p>"
                }
            ]
        }
        
        print(f"📤 Sending test email via Mailjet...")
        result = mailjet.send.create(data=data)
        
        print(f"📊 Mailjet Response:")
        print(f"Status Code: {result.status_code}")
        print(f"Response: {result.json()}")
        
        if result.status_code == 200:
            print("✅ Email sent successfully via Mailjet!")
            return True
        else:
            print(f"❌ Failed to send email. Status: {result.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Mailjet Connection Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 MailerPanda Email Sending Test Suite")
    print("=" * 60)
    
    # Test 1: Direct Mailjet connection
    mailjet_success = test_mailjet_connection()
    
    # Test 2: MailerPanda agent functionality  
    agent_result = test_mailerpanda_email_sending()
    
    print(f"\n📋 Test Summary:")
    print(f"  Mailjet Direct Test: {'✅ PASS' if mailjet_success else '❌ FAIL'}")
    print(f"  MailerPanda Agent Test: {'✅ PASS' if agent_result else '❌ FAIL'}")
    
    if not mailjet_success:
        print(f"\n💡 Troubleshooting Tips:")
        print(f"  1. Check if Mailjet API credentials are correct")
        print(f"  2. Verify your Mailjet account status")
        print(f"  3. Check if sender email domain is verified in Mailjet")
        print(f"  4. Ensure recipient email is valid")
    
    print(f"\n✅ Test completed!")
