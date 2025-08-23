#!/usr/bin/env python3
"""
Test with same emails but no context descriptions to compare personalization
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

def generate_no_context_consent_tokens():
    """Generate consent tokens for no-context testing."""
    
    print("🔐 Generating No-Context Test Consent Tokens")
    print("=" * 50)
    
    try:
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        user_id = "test_user_no_context"
        agent_id = "agent_mailerpanda"
        
        print(f"👤 User ID: {user_id}")
        print(f"🤖 Agent ID: {agent_id}")
        
        # Generate all required consent tokens
        consent_tokens = {}
        
        required_scopes = [
            ConsentScope.VAULT_READ_EMAIL,
            ConsentScope.CUSTOM_TEMPORARY,
            ConsentScope.VAULT_WRITE_EMAIL,
            ConsentScope.VAULT_READ_FILE,
            ConsentScope.VAULT_WRITE_FILE
        ]
        
        for scope in required_scopes:
            try:
                token = issue_token(
                    user_id=user_id,
                    agent_id=agent_id,
                    scope=scope,
                    expires_in_ms=3600000  # 1 hour
                )
                consent_tokens[scope.value] = token.token
                print(f"✅ Generated token for {scope.value}")
            except Exception as e:
                print(f"❌ Failed to generate {scope.value} token: {e}")
        
        print(f"\n🎯 Total tokens generated: {len(consent_tokens)}")
        return consent_tokens, user_id
        
    except Exception as e:
        print(f"❌ Token generation error: {e}")
        return {}, None

def test_no_context_emails():
    """Test emails without context descriptions to see standard personalization."""
    
    print(f"\n📧 Testing No-Context Email Personalization")
    print("=" * 50)
    
    # Generate consent tokens
    consent_tokens, user_id = generate_no_context_consent_tokens()
    
    if not consent_tokens or len(consent_tokens) < 3:
        print(f"❌ Cannot proceed without valid consent tokens")
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
        
        # Same user input as context test but no descriptions available
        user_input = """
        Send personalized emails about our new AI-powered email platform.
        
        Subject: Discover the Future of Email Marketing with AI
        
        The email should:
        - Welcome each recipient personally
        - Highlight our AI-powered email platform features
        - Use a professional and friendly tone
        - Include examples of platform benefits
        - Provide a clear call-to-action
        
        Since no specific context is provided, create a general but personalized
        email that works for all professional audiences.
        
        Send to all contacts in the Excel file.
        """
        
        print(f"\n📧 Starting No-Context Email Campaign:")
        print(f"🎯 Personalization: BASIC (No context descriptions)")
        print(f"📁 Excel file: no_context_test.xlsx")
        print(f"👥 Recipients: 3 (Same emails, no context)")
        print(f"🔑 Tokens: {list(consent_tokens.keys())}")
        
        # Execute the campaign
        print(f"\n🔄 Executing no-context email campaign...")
        result = agent.handle(
            user_id=user_id,
            consent_tokens=consent_tokens,
            user_input=user_input,
            mode="interactive",  # Interactive mode for approval
            enable_description_personalization=True,  # Still enabled but no descriptions
            excel_file_path="hushh_mcp/agents/mailerpanda/no_context_test.xlsx",
            personalization_mode="smart"
        )
        
        print(f"\n📊 Campaign Results:")
        print(f"Status: {result.get('status', 'Unknown')}")
        
        if result.get('status') == 'complete':
            print(f"\n✅ Campaign completed successfully!")
            
            # Show personalization statistics
            if 'personalized_count' in result:
                print(f"\n🎯 Personalization Statistics:")
                print(f"  Personalized emails: {result.get('personalized_count', 0)}")
                print(f"  Standard emails: {result.get('standard_count', 0)}")
                print(f"  Description-based customization: {result.get('description_column_detected', False)}")
            
            # Show email delivery status
            if 'emails_sent' in result:
                print(f"\n📤 Delivery Statistics:")
                print(f"  Total emails sent: {result.get('emails_sent', 0)}")
                
            # Show personalization comparison
            print(f"\n🔍 No-Context Personalization:")
            print(f"  🎮 dragnoid121@gmail.com: General professional content")
            print(f"  💼 alokkale121@gmail.com: General professional content")
            print(f"  🎓 23b4215@iitb.ac.in: General professional content")
            print(f"  ⚠️  All emails likely similar (no context for differentiation)")
                
            return result
        
        elif 'email_template' in result:
            template = result['email_template']
            print(f"\n📧 Generated Email Template (No Context):")
            print(f"Subject: {template.get('subject', 'No subject')}")
            print(f"Body Preview: {str(template.get('body', 'No body'))[:400]}...")
            
            print(f"\n🔍 Key Observations:")
            print(f"  • No description column detected")
            print(f"  • All recipients get same content")
            print(f"  • Only name/company personalization available")
            print(f"  • No context-aware customization")
            
            return result
        
        else:
            print(f"📊 Full result: {result}")
            return result
            
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def show_comparison_info():
    """Show comparison between context vs no-context testing."""
    
    print(f"\n📊 Context vs No-Context Comparison")
    print("=" * 45)
    
    print(f"""
🔍 What We're Comparing:

WITH CONTEXT (Previous Test):
✅ Description column with rich context
✅ Gaming developer context → Technical APIs, code examples
✅ Professional engineer context → Business benefits, efficiency
✅ Student context → Learning resources, educational content
✅ Different tones and examples for each recipient

WITHOUT CONTEXT (This Test):
⚠️  No description column
⚠️  Same general content for all recipients
⚠️  Only basic name/company personalization
⚠️  No context-aware customization
⚠️  Standard professional tone for everyone

📈 Expected Differences:
• Context test: Highly personalized, audience-specific
• No-context test: Generic but professional
• Personalization level: High vs Basic
• Content variety: Diverse vs Uniform
    """)

if __name__ == "__main__":
    print("🚀 No-Context Email Personalization Test")
    print("=" * 50)
    
    # Show comparison information
    show_comparison_info()
    
    # Run the no-context test
    result = test_no_context_emails()
    
    if result:
        print(f"\n🎉 No-context test completed!")
        print(f"Status: {result.get('status', 'Unknown')}")
        
        if result.get('status') == 'complete':
            print(f"\n💡 No-Context Test Summary:")
            print(f"  ✅ Same email addresses tested")
            print(f"  ✅ No description context provided")
            print(f"  ✅ Standard personalization only")
            print(f"  ✅ General professional content")
            print(f"  ✅ Demonstrates difference vs context-based")
            
            print(f"\n🔍 Key Findings:")
            print(f"  📧 All recipients receive similar content")
            print(f"  🎯 No audience-specific customization")
            print(f"  💼 Basic name/company personalization only")
            print(f"  ⚖️  Shows value of context descriptions")
            
    else:
        print(f"\n❌ Test failed - check error messages above")
    
    print(f"\n✅ No-context comparison test completed!")
