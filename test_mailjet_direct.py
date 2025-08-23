#!/usr/bin/env python3
"""
Direct test of Mailjet email sending to verify configuration.
"""

import os
from dotenv import load_dotenv
from mailjet_rest import Client

# Load environment variables
load_dotenv()

def test_mailjet_direct():
    """Test Mailjet API directly."""
    print("📧 Testing Mailjet Configuration")
    print("=" * 40)
    
    # Get API keys
    api_key = os.environ.get("MAILJET_API_KEY")
    api_secret = os.environ.get("MAILJET_API_SECRET")
    
    print(f"API Key: {api_key[:10]}..." if api_key else "❌ No API Key")
    print(f"API Secret: {api_secret[:10]}..." if api_secret else "❌ No API Secret")
    
    if not api_key or not api_secret:
        print("❌ Mailjet credentials not found in .env file")
        return False
    
    try:
        # Initialize Mailjet client
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        print("✅ Mailjet client initialized")
        
        # Test email data
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "test@example.com",
                        "Name": "Test Sender"
                    },
                    "To": [
                        {
                            "Email": "recipient@example.com",
                            "Name": "Test Recipient"
                        }
                    ],
                    "Subject": "Test Email from MailerPanda",
                    "TextPart": "This is a test email to verify Mailjet configuration.",
                    "HTMLPart": "<h3>Test Email</h3><p>This is a test email to verify Mailjet configuration.</p>"
                }
            ]
        }
        
        print("📤 Attempting to send test email...")
        result = mailjet.send.create(data=data)
        
        print(f"📥 Response Status: {result.status_code}")
        print(f"Response Data: {result.json()}")
        
        if result.status_code == 200:
            print("✅ SUCCESS: Mailjet is configured correctly!")
            return True
        else:
            print(f"❌ FAILED: Mailjet returned status {result.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_mailjet_direct()
    print(f"\n{'✅ Mailjet working' if success else '❌ Mailjet not working'}")
