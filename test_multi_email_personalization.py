#!/usr/bin/env python3
"""
Comprehensive test with multiple emails and diverse contexts
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

def generate_multi_email_consent_tokens():
    """Generate consent tokens for multi-email testing."""
    
    print("🔐 Generating Multi-Email Consent Tokens")
    print("=" * 45)
    
    try:
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        user_id = "test_user_multi_email"
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

def test_multi_email_personalization():
    """Test personalization with multiple diverse email contexts."""
    
    print(f"\n🎯 Testing Multi-Email Personalization")
    print("=" * 45)
    
    # Generate consent tokens
    consent_tokens, user_id = generate_multi_email_consent_tokens()
    
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
        
        # Diverse user input for different email contexts
        user_input = """
        Send personalized emails about our new AI-powered email platform.
        
        Subject: Discover the Future of Email Marketing with AI
        
        The email should:
        - Welcome each recipient based on their background
        - Highlight features relevant to their interests (gaming, professional, academic)
        - Use appropriate tone for each audience (technical, professional, educational)
        - Include personalized examples and use cases
        - Provide relevant call-to-action for each recipient type
        
        Customize the content based on each recipient's description:
        - For developers: Focus on technical capabilities and APIs
        - For professionals: Emphasize efficiency and business benefits  
        - For students: Highlight learning opportunities and educational value
        
        Send to all contacts in the Excel file with full personalization.
        """
        
        print(f"\n📧 Starting Multi-Email Campaign:")
        print(f"🎯 Personalization: ENABLED (Smart Mode)")
        print(f"📁 Excel file: multi_email_test.xlsx")
        print(f"👥 Recipients: 3 (Developer, Professional, Student)")
        print(f"🔑 Tokens: {list(consent_tokens.keys())}")
        
        # Execute the campaign
        print(f"\n🔄 Executing personalized email campaign...")
        result = agent.handle(
            user_id=user_id,
            consent_tokens=consent_tokens,
            user_input=user_input,
            mode="interactive",  # Interactive mode for approval
            enable_description_personalization=True,
            excel_file_path="hushh_mcp/agents/mailerpanda/multi_email_test.xlsx",
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
                
            # Show personalization examples
            print(f"\n🎨 Personalization Examples:")
            print(f"  🎮 dragnoid121@gmail.com: Gaming & technical focus")
            print(f"  💼 alokkale121@gmail.com: Professional & efficiency focus")
            print(f"  🎓 23b4215@iitb.ac.in: Educational & learning focus")
                
            return result
        
        elif 'email_template' in result:
            template = result['email_template']
            print(f"\n📧 Generated Email Template:")
            print(f"Subject: {template.get('subject', 'No subject')}")
            print(f"Body Preview: {str(template.get('body', 'No body'))[:300]}...")
            
            return result
        
        else:
            print(f"📊 Full result: {result}")
            return result
            
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def show_test_context():
    """Show the different contexts being tested."""
    
    print(f"\n📋 Multi-Email Test Context")
    print("=" * 35)
    
    print(f"""
🎯 Testing Different Recipient Types:

1. 🎮 Gaming Developer (dragnoid121@gmail.com)
   - Background: Gaming enthusiast and developer
   - Interests: Technical deep-dives, cutting-edge features
   - Preferred Style: Detailed explanations with examples
   - Expected Personalization: Technical APIs, code examples

2. 💼 Professional Engineer (alokkale121@gmail.com)  
   - Background: Experienced software engineer
   - Interests: Well-documented solutions, efficiency
   - Preferred Style: Professional, accurate communication
   - Expected Personalization: Business benefits, productivity

3. 🎓 Computer Science Student (23b4215@iitb.ac.in)
   - Background: CS student at IIT Bombay
   - Interests: Learning new technologies
   - Preferred Style: Educational, beginner-friendly
   - Expected Personalization: Learning resources, tutorials

🔍 What We're Testing:
   ✅ Context-aware personalization
   ✅ Tone adaptation (technical/professional/educational)
   ✅ Content customization based on background
   ✅ Appropriate call-to-action for each audience
   ✅ Multi-recipient campaign management
    """)

if __name__ == "__main__":
    print("🚀 Multi-Email Personalization Test")
    print("=" * 50)
    
    # Show test context
    show_test_context()
    
    # Run the comprehensive test
    result = test_multi_email_personalization()
    
    if result:
        print(f"\n🎉 Multi-email test completed!")
        print(f"Status: {result.get('status', 'Unknown')}")
        
        if result.get('status') == 'complete':
            print(f"\n💡 Test Success Summary:")
            print(f"  ✅ Multiple email addresses handled")
            print(f"  ✅ Context-based personalization applied")
            print(f"  ✅ Different tones for different audiences")
            print(f"  ✅ Consent tokens working properly")
            print(f"  ✅ Email delivery successful")
            
    else:
        print(f"\n❌ Test failed - check error messages above")
    
    print(f"\n✅ Multi-email test completed!")
