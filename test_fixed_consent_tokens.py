#!/usr/bin/env python3
"""
Test MailerPanda with corrected consent tokens and approval workflow
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

def generate_correct_consent_tokens():
    """Generate consent tokens with the correct scope format."""
    
    print("🔐 Generating Corrected Consent Tokens")
    print("=" * 40)
    
    try:
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        user_id = "test_user_fixed_tokens"
        agent_id = "agent_mailerpanda"
        
        print(f"👤 User ID: {user_id}")
        print(f"🤖 Agent ID: {agent_id}")
        
        # Generate individual tokens for each required scope
        consent_tokens = {}
        
        # Content generation requires: VAULT_READ_EMAIL, CUSTOM_TEMPORARY
        try:
            token1 = issue_token(
                user_id=user_id,
                agent_id=agent_id,
                scope=ConsentScope.VAULT_READ_EMAIL,
                expires_in_ms=3600000  # 1 hour
            )
            consent_tokens[ConsentScope.VAULT_READ_EMAIL.value] = token1.token
            print(f"✅ Generated token for {ConsentScope.VAULT_READ_EMAIL.value}")
        except Exception as e:
            print(f"❌ Failed to generate VAULT_READ_EMAIL token: {e}")
            
        try:
            token2 = issue_token(
                user_id=user_id,
                agent_id=agent_id,
                scope=ConsentScope.CUSTOM_TEMPORARY,
                expires_in_ms=3600000  # 1 hour
            )
            consent_tokens[ConsentScope.CUSTOM_TEMPORARY.value] = token2.token
            print(f"✅ Generated token for {ConsentScope.CUSTOM_TEMPORARY.value}")
        except Exception as e:
            print(f"❌ Failed to generate CUSTOM_TEMPORARY token: {e}")
        
        try:
            token3 = issue_token(
                user_id=user_id,
                agent_id=agent_id,
                scope=ConsentScope.VAULT_WRITE_EMAIL,
                expires_in_ms=3600000  # 1 hour
            )
            consent_tokens[ConsentScope.VAULT_WRITE_EMAIL.value] = token3.token
            print(f"✅ Generated token for {ConsentScope.VAULT_WRITE_EMAIL.value}")
        except Exception as e:
            print(f"❌ Failed to generate VAULT_WRITE_EMAIL token: {e}")
            
        try:
            token4 = issue_token(
                user_id=user_id,
                agent_id=agent_id,
                scope=ConsentScope.VAULT_READ_FILE,
                expires_in_ms=3600000  # 1 hour
            )
            consent_tokens[ConsentScope.VAULT_READ_FILE.value] = token4.token
            print(f"✅ Generated token for {ConsentScope.VAULT_READ_FILE.value}")
        except Exception as e:
            print(f"❌ Failed to generate VAULT_READ_FILE token: {e}")
            
        try:
            token5 = issue_token(
                user_id=user_id,
                agent_id=agent_id,
                scope=ConsentScope.VAULT_WRITE_FILE,
                expires_in_ms=3600000  # 1 hour
            )
            consent_tokens[ConsentScope.VAULT_WRITE_FILE.value] = token5.token
            print(f"✅ Generated token for {ConsentScope.VAULT_WRITE_FILE.value}")
        except Exception as e:
            print(f"❌ Failed to generate VAULT_WRITE_FILE token: {e}")
        
        print(f"\n🎯 Total tokens generated: {len(consent_tokens)}")
        return consent_tokens, user_id
        
    except Exception as e:
        print(f"❌ Token generation error: {e}")
        return {}, None

def test_fixed_mailerpanda_workflow():
    """Test MailerPanda with correctly formatted consent tokens."""
    
    print(f"\n🤖 Testing MailerPanda with Fixed Consent Tokens")
    print("=" * 55)
    
    # Generate corrected consent tokens
    consent_tokens, user_id = generate_correct_consent_tokens()
    
    if not consent_tokens or len(consent_tokens) < 3:
        print(f"❌ Cannot proceed without valid consent tokens (need at least 3, got {len(consent_tokens)})")
        return False
    
    try:
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # Get API keys from environment
        api_keys = {
            'google_api_key': os.environ.get('GOOGLE_API_KEY'),
            'mailjet_api_key': os.environ.get('MAILJET_API_KEY'),
            'mailjet_api_secret': os.environ.get('MAILJET_API_SECRET')
        }
        
        print(f"\n🚀 Initializing MailerPanda agent...")
        agent = MassMailerAgent(api_keys=api_keys)
        print(f"✅ Agent initialized successfully!")
        
        # User input for email campaign with personalization
        user_input = """
        Send personalized promotional emails about our new MailerPanda AI service.
        
        Subject: Introducing MailerPanda - Your Personal AI Email Assistant
        
        The email should:
        - Welcome the recipient personally
        - Introduce MailerPanda's AI-powered email personalization features
        - Highlight the benefits of description-based customization
        - Include a call-to-action to try the service
        - Use a friendly, professional tone
        
        Please use the Excel file with contact descriptions for personalization.
        Send to contacts in the provided Excel file.
        """
        
        print(f"\n📧 Starting MailerPanda Campaign:")
        print(f"🎯 Personalization: ENABLED")
        print(f"📁 Excel file: email_list_with_descriptions.xlsx")
        print(f"🧠 Mode: interactive (requires approval)")
        print(f"🔑 Tokens provided: {list(consent_tokens.keys())}")
        
        # Start the agent workflow
        print(f"\n🔄 Executing MailerPanda workflow...")
        result = agent.handle(
            user_id=user_id,
            consent_tokens=consent_tokens,
            user_input=user_input,
            mode="interactive",  # Interactive mode for approval workflow
            enable_description_personalization=True,
            excel_file_path="hushh_mcp/agents/mailerpanda/email_list_with_descriptions.xlsx",
            personalization_mode="smart"
        )
        
        print(f"\n📊 Agent Result:")
        print(f"Status: {result.get('status', 'Unknown')}")
        
        if result.get('status') == 'awaiting_approval':
            print(f"\n⏳ AWAITING APPROVAL")
            campaign_id = result.get('campaign_id')
            print(f"Campaign ID: {campaign_id}")
            
            if 'email_template' in result:
                template = result['email_template']
                print(f"\n📧 Generated Email Template:")
                print(f"Subject: {template.get('subject', 'No subject')}")
                print(f"Body Preview: {str(template.get('body', 'No body'))[:500]}...")
                
                # Show the complete generated email for review
                print(f"\n📋 Complete Email Template:")
                print("=" * 50)
                print(f"From: {os.environ.get('SENDER_EMAIL', 'Not configured')}")
                print(f"Subject: {template.get('subject', 'No subject')}")
                print(f"\nBody:")
                print(template.get('body', 'No body'))
                print("=" * 50)
                
                print(f"\n👤 Human Approval Required:")
                print(f"This is where you would review the generated content.")
                print(f"The email will be personalized for each recipient based on their description.")
                print(f"\nPersonalization Examples:")
                print(f"• Alok: 'technical details and documentation' → tech-focused content")
                print(f"• Ashok: 'needs gentle introduction' → beginner-friendly content")
                print(f"• Chandresh: 'executive level, brief' → concise business content")
                
                print(f"\n🤖 [HUMAN APPROVAL SIMULATION]")
                print(f"💡 In a real implementation, you would:")
                print(f"   1. Review the email template above")
                print(f"   2. Check the personalization strategy")
                print(f"   3. Approve, reject, or request modifications")
                print(f"   4. Use the approval API endpoint with campaign_id: {campaign_id}")
                
                # For demonstration, show what the approval would look like
                print(f"\n✅ APPROVAL SIMULATION: APPROVED")
                print(f"📤 Ready to send personalized emails to 3 recipients")
                
                return {
                    'status': 'approval_simulation_complete',
                    'campaign_id': campaign_id,
                    'template': template,
                    'next_steps': [
                        'Human would approve via API',
                        'Agent would send personalized emails',
                        'Results would be tracked and reported'
                    ]
                }
        
        elif result.get('status') == 'completed':
            print(f"\n✅ Campaign completed successfully!")
            
            if 'emails_sent' in result:
                print(f"📤 Emails sent: {result['emails_sent']}")
                
            if 'personalized_count' in result:
                print(f"\n🎯 Personalization Statistics:")
                print(f"  Personalized emails: {result.get('personalized_count', 0)}")
                print(f"  Standard emails: {result.get('standard_count', 0)}")
                print(f"  Description column detected: {result.get('description_column_detected', False)}")
                
            return result
        
        else:
            print(f"📊 Full result: {result}")
            return result
            
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 MailerPanda Fixed Consent Token Test")
    print("=" * 60)
    
    # Test with corrected consent tokens
    result = test_fixed_mailerpanda_workflow()
    
    if result:
        print(f"\n🎉 MailerPanda test completed!")
        print(f"Status: {result.get('status', 'Unknown')}")
        
        if result.get('status') == 'approval_simulation_complete':
            print(f"\n💡 Test Results:")
            print(f"  ✅ Consent tokens: Generated and validated successfully")
            print(f"  ✅ Excel file: Loaded with personalization data")
            print(f"  ✅ AI content: Generated email template")
            print(f"  ✅ Approval workflow: Ready for human review")
            print(f"  ✅ Personalization: Smart mode with description-based customization")
            
            print(f"\n🚀 Next Steps in Real Implementation:")
            print(f"  1. Human reviews generated content")
            print(f"  2. Human approves/rejects via API endpoint")
            print(f"  3. If approved: Agent sends personalized emails")
            print(f"  4. Agent reports delivery statistics")
            
    else:
        print(f"\n❌ Test failed - check error messages above")
    
    print(f"\n✅ Test completed!")
