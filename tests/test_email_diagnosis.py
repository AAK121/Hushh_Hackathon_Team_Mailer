#!/usr/bin/env python3
"""
Test MailerPanda with valid consent tokens and proper email setup
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_with_valid_consent_tokens():
    """Test with properly generated consent tokens."""
    
    print("🧪 Testing MailerPanda with Valid Consent Tokens")
    print("=" * 55)
    
    try:
        # Import consent token creation
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        # Generate real consent tokens
        user_id = "test_user_email_001"
        
        print("🔐 Generating valid consent tokens...")
        consent_tokens = {}
        
        required_scopes = [
            ConsentScope.VAULT_READ_EMAIL,
            ConsentScope.VAULT_WRITE_EMAIL,
            ConsentScope.VAULT_READ_FILE,
            ConsentScope.VAULT_WRITE_FILE,
            ConsentScope.CUSTOM_TEMPORARY
        ]
        
        for scope in required_scopes:
            try:
                token = issue_token(
                    user_id=user_id,
                    scope=scope,
                    duration_hours=1
                )
                consent_tokens[scope.value] = token
                print(f"✅ Generated token for {scope.value}")
            except Exception as e:
                print(f"❌ Failed to generate token for {scope.value}: {e}")
        
        if len(consent_tokens) < len(required_scopes):
            print("⚠️ Not all tokens generated, proceeding with available tokens...")
        
        # Import and test the agent
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # Use updated Mailjet credentials (you may need to get new ones)
        api_keys = {
            'google_api_key': 'AIzaSyDZ7zdMZE-HDGsJAVEMQBo6PF7HppI7HDQ',
            'mailjet_api_key': '72aa1e9f80b97bb74e71c4aa6e5c6e44',
            'mailjet_api_secret': '4bc7b4ced53de9e6ace69ad90aade5d8'
        }
        
        print(f"\n📧 Initializing agent with real credentials...")
        agent = MassMailerAgent(api_keys=api_keys)
        
        user_input = """
        Send a welcome email to new MailerPanda users.
        
        Subject: Welcome to MailerPanda - Your AI Email Assistant
        
        Content should include:
        - Welcome message
        - Brief overview of personalization features
        - Next steps to get started
        
        Send to: test@example.com
        """
        
        print(f"\n🚀 Testing email campaign...")
        result = agent.handle(
            user_id=user_id,
            consent_tokens=consent_tokens,
            user_input=user_input,
            mode="interactive",
            enable_description_personalization=False  # Disable for simpler test
        )
        
        print(f"\n📊 Result: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_direct_mailjet_with_domain():
    """Test Mailjet with a verified domain."""
    
    print(f"\n📧 Testing Mailjet with Different Sender Domain")
    print("=" * 50)
    
    try:
        from mailjet_rest import Client
        
        # Test with different sender domains
        test_domains = [
            "noreply@mailerpanda.com",
            "test@gmail.com",  # If you have Gmail verification
            "no-reply@yourdomain.com",  # Replace with your verified domain
        ]
        
        mailjet = Client(
            auth=('72aa1e9f80b97bb74e71c4aa6e5c6e44', '4bc7b4ced53de9e6ace69ad90aade5d8'),
            version='v3.1'
        )
        
        for sender_email in test_domains:
            print(f"\n📤 Testing with sender: {sender_email}")
            
            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": sender_email,
                            "Name": "MailerPanda Test"
                        },
                        "To": [
                            {
                                "Email": "test@example.com",
                                "Name": "Test User"
                            }
                        ],
                        "Subject": f"Test from {sender_email}",
                        "TextPart": f"Test email from {sender_email}",
                        "HTMLPart": f"<h1>Test Email</h1><p>Sent from {sender_email}</p>"
                    }
                ]
            }
            
            try:
                result = mailjet.send.create(data=data)
                print(f"Status: {result.status_code}")
                print(f"Response: {result.json()}")
                
                if result.status_code == 200:
                    print(f"✅ Success with {sender_email}")
                    return True
                    
            except Exception as e:
                print(f"❌ Error with {sender_email}: {e}")
                
        return False
        
    except Exception as e:
        print(f"❌ Mailjet test error: {e}")
        return False

def check_mailjet_account_status():
    """Check Mailjet account status and configuration."""
    
    print(f"\n🔍 Checking Mailjet Account Status")
    print("=" * 40)
    
    try:
        from mailjet_rest import Client
        
        mailjet = Client(
            auth=('72aa1e9f80b97bb74e71c4aa6e5c6e44', '4bc7b4ced53de9e6ace69ad90aade5d8'),
            version='v3'
        )
        
        # Check API key info
        print("📊 Checking API key information...")
        try:
            result = mailjet.apikey.get()
            print(f"API Key Status: {result.status_code}")
            if result.status_code == 200:
                data = result.json()
                print(f"API Key Data: {data}")
            else:
                print(f"❌ API Key check failed: {result.json()}")
        except Exception as e:
            print(f"❌ API Key check error: {e}")
        
        # Check sender addresses
        print(f"\n📧 Checking sender addresses...")
        try:
            result = mailjet.sender.get()
            print(f"Senders Status: {result.status_code}")
            if result.status_code == 200:
                data = result.json()
                print(f"Verified Senders: {data}")
            else:
                print(f"❌ Senders check failed: {result.json()}")
        except Exception as e:
            print(f"❌ Senders check error: {e}")
            
    except Exception as e:
        print(f"❌ Account status check error: {e}")

if __name__ == "__main__":
    print("🔧 MailerPanda Email Diagnosis & Testing")
    print("=" * 50)
    
    # Test 1: Check Mailjet account status
    check_mailjet_account_status()
    
    # Test 2: Test with different domains
    domain_test = test_direct_mailjet_with_domain()
    
    # Test 3: Test with valid consent tokens
    agent_test = test_with_valid_consent_tokens()
    
    print(f"\n📋 Final Test Results:")
    print(f"  Domain Test: {'✅ PASS' if domain_test else '❌ FAIL'}")
    print(f"  Agent Test: {'✅ PASS' if agent_test else '❌ FAIL'}")
    
    if not domain_test:
        print(f"\n💡 Email Sending Recommendations:")
        print(f"  1. Update Mailjet API credentials")
        print(f"  2. Verify sender domain in Mailjet dashboard")
        print(f"  3. Check Mailjet account status and limits")
        print(f"  4. Try using a verified sender email address")
