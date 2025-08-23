#!/usr/bin/env python3
"""
Test MailerPanda with real consent tokens and human-in-the-loop approval workflow
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

def generate_real_consent_tokens():
    """Generate real consent tokens for testing."""
    
    print("🔐 Generating Real Consent Tokens")
    print("=" * 40)
    
    try:
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        user_id = "test_user_real_tokens"
        agent_id = "agent_mailerpanda"
        
        print(f"👤 User ID: {user_id}")
        print(f"🤖 Agent ID: {agent_id}")
        
        # Required scopes for MailerPanda
        required_scopes = [
            ConsentScope.VAULT_READ_EMAIL,
            ConsentScope.VAULT_WRITE_EMAIL,
            ConsentScope.VAULT_READ_FILE,
            ConsentScope.VAULT_WRITE_FILE,
            ConsentScope.CUSTOM_TEMPORARY
        ]
        
        consent_tokens = {}
        
        for scope in required_scopes:
            try:
                token = issue_token(
                    user_id=user_id,
                    agent_id=agent_id,
                    scope=scope,
                    expires_in_ms=3600000  # 1 hour
                )
                consent_tokens[scope.value] = token
                print(f"✅ Generated token for {scope.value}")
            except Exception as e:
                print(f"❌ Failed to generate token for {scope.value}: {e}")
        
        return consent_tokens, user_id
        
    except Exception as e:
        print(f"❌ Token generation error: {e}")
        return {}, None

def test_mailerpanda_with_approval_workflow():
    """Test MailerPanda with human-in-the-loop approval workflow."""
    
    print(f"\n🤖 Testing MailerPanda with Approval Workflow")
    print("=" * 55)
    
    # Generate real consent tokens
    consent_tokens, user_id = generate_real_consent_tokens()
    
    if not consent_tokens:
        print("❌ Cannot proceed without valid consent tokens")
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
            print(f"Campaign ID: {result.get('campaign_id')}")
            
            if 'email_template' in result:
                template = result['email_template']
                print(f"\n📧 Generated Email Template:")
                print(f"Subject: {template.get('subject', 'No subject')}")
                print(f"Body Preview: {str(template.get('body', 'No body'))[:300]}...")
                
                # Simulate human approval
                print(f"\n👤 Human Approval Required:")
                print(f"1. Review the generated email content above")
                print(f"2. Choose your action:")
                print(f"   - Type 'approve' to send emails")
                print(f"   - Type 'reject' to cancel")
                print(f"   - Type 'modify' to request changes")
                
                # For testing, we'll auto-approve after showing the content
                print(f"\n🤖 [AUTO-APPROVAL FOR TESTING]")
                approval_action = "approve"
                print(f"💡 Action: {approval_action}")
                
                return result
        
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

def show_approval_workflow_info():
    """Explain the approval workflow."""
    
    print(f"\n📋 MailerPanda Approval Workflow")
    print("=" * 40)
    
    print(f"""
🔄 How the Approval Workflow Works:

1. 📝 Content Generation Phase:
   - Agent analyzes user input
   - Generates email template using AI
   - Detects Excel file structure
   - Applies personalization rules

2. ⏳ Human Review Phase:
   - Agent presents generated content
   - Human reviews email template
   - Human can approve, reject, or request modifications

3. 📤 Email Sending Phase:
   - If approved: Agent sends emails via Mailjet
   - If rejected: Campaign is cancelled
   - If modified: Agent regenerates content

4. 📊 Results & Statistics:
   - Reports delivery status
   - Shows personalization statistics
   - Provides campaign analytics

🎯 Interactive Mode Benefits:
   - Quality control before sending
   - Human oversight of AI-generated content
   - Ability to fine-tune campaigns
   - Protection against unwanted sends
    """)

if __name__ == "__main__":
    print("🚀 MailerPanda Real Consent Token & Approval Test")
    print("=" * 60)
    
    # Show workflow information
    show_approval_workflow_info()
    
    # Test with real consent tokens and approval workflow
    result = test_mailerpanda_with_approval_workflow()
    
    if result:
        print(f"\n🎉 MailerPanda test completed!")
        print(f"Status: {result.get('status', 'Unknown')}")
        
        if result.get('status') == 'awaiting_approval':
            print(f"\n💡 Next Steps:")
            print(f"  1. The agent has generated email content")
            print(f"  2. Human approval is required to proceed")
            print(f"  3. Use the approval API endpoint to continue")
            print(f"  4. Campaign ID: {result.get('campaign_id')}")
            
    else:
        print(f"\n❌ Test failed - check error messages above")
    
    print(f"\n✅ Test completed!")
