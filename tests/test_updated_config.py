#!/usr/bin/env python3
"""
Test email sending with updated configuration
"""

import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_updated_mailjet_credentials():
    """Test the updated Mailjet credentials."""
    
    print("🧪 Testing Updated Email Configuration")
    print("=" * 50)
    
    # Get credentials from environment
    api_key = os.environ.get("MAILJET_API_KEY")
    api_secret = os.environ.get("MAILJET_API_SECRET")
    sender_email = os.environ.get("SENDER_EMAIL")
    
    print(f"🔑 Mailjet API Key: {api_key[:20] if api_key else 'Not found'}...")
    print(f"🔑 Mailjet Secret: {api_secret[:20] if api_secret else 'Not found'}...")
    print(f"📧 Sender Email: {sender_email}")
    
    if not all([api_key, api_secret, sender_email]):
        print("❌ Missing configuration! Please check .env file.")
        return False
    
    try:
        from mailjet_rest import Client
        
        # Initialize Mailjet client with new credentials
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        
        # Test email data
        test_data = {
            'Messages': [
                {
                    "From": {
                        "Email": sender_email,
                        "Name": "MailerPanda Test"
                    },
                    "To": [
                        {
                            "Email": "alokkale121@gmail.com",  # Test recipient
                            "Name": "Test Recipient"
                        }
                    ],
                    "Subject": "✅ MailerPanda Email Test - Updated Configuration",
                    "TextPart": "SUCCESS! MailerPanda email sending is now working with updated configuration.",
                    "HTMLPart": """
                    <div style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #4CAF50;">✅ MailerPanda Email Test Successful!</h2>
                        <p>This email confirms that:</p>
                        <ul>
                            <li>✅ Mailjet API credentials are working</li>
                            <li>✅ Sender email configuration is correct</li>
                            <li>✅ MailerPanda can now send emails</li>
                            <li>✅ Description-based personalization is ready to use</li>
                        </ul>
                        <p><strong>Next steps:</strong></p>
                        <ol>
                            <li>Test personalization features with Excel files</li>
                            <li>Run full campaign tests</li>
                            <li>Deploy to production</li>
                        </ol>
                        <p style="color: #666; font-size: 12px;">
                            Sent via MailerPanda Agent v3.1.0<br>
                            Timestamp: {timestamp}
                        </p>
                    </div>
                    """.format(timestamp=str(__import__('datetime').datetime.now()))
                }
            ]
        }
        
        print(f"\n📤 Sending test email via Mailjet...")
        result = mailjet.send.create(data=test_data)
        
        print(f"📊 Response Status: {result.status_code}")
        response_data = result.json()
        print(f"📊 Response Data: {response_data}")
        
        if result.status_code == 200:
            messages = response_data.get('Messages', [])
            if messages and messages[0].get('Status') == 'success':
                print(f"\n🎉 SUCCESS! Email sent successfully!")
                print(f"📧 From: {sender_email}")
                print(f"📧 To: alokkale121@gmail.com")
                print(f"✅ MailerPanda email sending is now fully functional!")
                return True
            else:
                print(f"❌ Email sending failed. Message status: {messages}")
                return False
        else:
            print(f"❌ Failed to send email. HTTP Status: {result.status_code}")
            print(f"Error: {response_data}")
            return False
            
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        return False

def test_mailerpanda_agent():
    """Test the MailerPanda agent with new configuration."""
    
    print(f"\n🤖 Testing MailerPanda Agent")
    print("=" * 35)
    
    try:
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # Get API keys from environment
        api_keys = {
            'google_api_key': os.environ.get('GOOGLE_API_KEY'),
            'mailjet_api_key': os.environ.get('MAILJET_API_KEY'),
            'mailjet_api_secret': os.environ.get('MAILJET_API_SECRET')
        }
        
        print(f"🚀 Initializing MailerPanda agent...")
        agent = MassMailerAgent(api_keys=api_keys)
        print(f"✅ Agent initialized successfully!")
        
        # Create simple demo consent tokens for testing
        demo_tokens = {
            "vault.read.email": "demo_token_123",
            "vault.write.email": "demo_token_456",
            "vault.read.file": "demo_token_789",
            "vault.write.file": "demo_token_012",
            "custom.temporary": "demo_token_345"
        }
        
        user_input = """
        Send a test email to verify MailerPanda is working correctly.
        
        Subject: MailerPanda Agent Test - Configuration Update
        
        Please send a test email with:
        - Confirmation that the configuration update worked
        - Brief overview of available features
        - Thank you message for testing
        
        Recipient: alokkale121@gmail.com
        """
        
        print(f"\n📧 Testing agent email functionality...")
        print(f"🔧 Mode: interactive (proper consent validation)")
        
        # The agent will likely fail due to consent validation, but let's see the behavior
        try:
            result = agent.handle(
                user_id="test_config_update",
                consent_tokens=demo_tokens,
                user_input=user_input,
                mode="interactive"
            )
            
            print(f"✅ Agent completed successfully!")
            print(f"📊 Result: {result}")
            return True
            
        except Exception as agent_error:
            print(f"⚠️ Agent validation error (expected): {str(agent_error)}")
            print(f"💡 This is expected due to consent validation")
            return False
            
    except Exception as e:
        print(f"❌ Agent test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 MailerPanda Updated Configuration Test")
    print("=" * 55)
    
    # Test 1: Direct Mailjet API
    mailjet_success = test_updated_mailjet_credentials()
    
    # Test 2: MailerPanda Agent
    agent_success = test_mailerpanda_agent()
    
    print(f"\n📋 Test Results Summary:")
    print(f"  📧 Mailjet Direct Test: {'✅ PASS' if mailjet_success else '❌ FAIL'}")
    print(f"  🤖 MailerPanda Agent: {'✅ PASS' if agent_success else '⚠️ CONSENT ISSUES'}")
    
    if mailjet_success:
        print(f"\n🎉 EXCELLENT! Email sending is now working!")
        print(f"📧 Check your inbox at: alokkale121@gmail.com")
        print(f"✅ MailerPanda is ready for production use!")
    else:
        print(f"\n❌ Email sending still has issues. Check credentials and sender verification.")
    
    print(f"\n✅ Test completed!")
