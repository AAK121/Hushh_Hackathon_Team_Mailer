#!/usr/bin/env python3
"""
Fixed MailerPanda test with proper consent tokens and updated credentials
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_with_fixed_tokens():
    """Test with properly generated consent tokens."""
    
    print("🔧 Testing MailerPanda with Fixed Consent Tokens")
    print("=" * 55)
    
    try:
        # Import consent token creation
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        # Generate real consent tokens (without duration_hours)
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
                # Generate token without duration_hours parameter
                token = issue_token(
                    user_id=user_id,
                    scope=scope
                )
                consent_tokens[scope.value] = token
                print(f"✅ Generated token for {scope.value}")
            except Exception as e:
                print(f"❌ Failed to generate token for {scope.value}: {e}")
        
        # Import and test the agent
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # PLACEHOLDER: You need to update these with fresh Mailjet credentials
        api_keys = {
            'google_api_key': 'AIzaSyDZ7zdMZE-HDGsJAVEMQBo6PF7HppI7HDQ',
            'mailjet_api_key': 'YOUR_NEW_MAILJET_API_KEY',  # ⚠️ UPDATE THIS
            'mailjet_api_secret': 'YOUR_NEW_MAILJET_SECRET'  # ⚠️ UPDATE THIS
        }
        
        print(f"\n📧 Initializing agent...")
        agent = MassMailerAgent(api_keys=api_keys)
        
        user_input = """
        Send a test email to verify the MailerPanda functionality.
        
        Subject: MailerPanda Test - Email Sending Verification
        
        Please send a simple test email with:
        - Confirmation that MailerPanda is working
        - Timestamp of when this email was sent
        - Brief description of the personalization features
        
        Send to: your-email@gmail.com
        """
        
        print(f"\n🚀 Testing email campaign with valid tokens...")
        result = agent.handle(
            user_id=user_id,
            consent_tokens=consent_tokens,
            user_input=user_input,
            mode="interactive",
            enable_description_personalization=False
        )
        
        print(f"\n📊 Agent Result:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def provide_mailjet_setup_instructions():
    """Provide step-by-step instructions for Mailjet setup."""
    
    print(f"\n📧 How to Fix Mailjet Email Sending")
    print("=" * 45)
    
    print(f"""
🔑 Step 1: Get New Mailjet API Credentials
   1. Go to https://app.mailjet.com/dashboard
   2. Log into your account (or create one if needed)
   3. Navigate to "Account Settings" > "API Key Management"
   4. Click "Generate a new API Key"
   5. Copy the API Key and Secret Key

📧 Step 2: Verify Sender Domain
   1. In Mailjet dashboard, go to "Account Settings" > "Sender addresses & domains"
   2. Add and verify your sender domain (e.g., your-domain.com)
   3. Or use a verified email address like your Gmail

🔧 Step 3: Update Credentials in Code
   1. Replace 'YOUR_NEW_MAILJET_API_KEY' with your actual API key
   2. Replace 'YOUR_NEW_MAILJET_SECRET' with your actual secret
   3. Update sender email to a verified address

✅ Step 4: Test Email Sending
   1. Run the test script again
   2. Check your inbox for the test email
   3. If successful, MailerPanda will be able to send emails!

⚠️ Important Notes:
   - Free Mailjet accounts have sending limits
   - All sender addresses must be verified
   - Check spam folder if emails don't appear in inbox
   - Monitor Mailjet dashboard for delivery statistics
    """)

if __name__ == "__main__":
    print("🚨 MailerPanda Email Sending Fix Guide")
    print("=" * 50)
    
    # Provide setup instructions
    provide_mailjet_setup_instructions()
    
    # Test with current setup (will show what needs to be fixed)
    print(f"\n🧪 Testing Current Setup (Expected to Fail):")
    test_result = test_with_fixed_tokens()
    
    if test_result:
        print(f"\n🎉 SUCCESS: MailerPanda email sending is working!")
    else:
        print(f"\n❌ EXPECTED: Email sending failed due to invalid Mailjet credentials")
        print(f"📝 Action Required: Follow the setup instructions above to fix email sending")
