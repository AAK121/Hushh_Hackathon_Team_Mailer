#!/usr/bin/env python3
"""
Test MailerPanda with real consent tokens and Excel personalization
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
    """Generate real consent tokens for MailerPanda testing."""
    
    print("🔐 Generating Real Consent Tokens")
    print("=" * 40)
    
    try:
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        user_id = "test_user_real_consent"
        agent_id = "agent_mailerpanda"
        
        print(f"👤 User ID: {user_id}")
        print(f"🤖 Agent ID: {agent_id}")
        
        # Generate real consent tokens for all required scopes
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
                token_obj = issue_token(
                    user_id=user_id,
                    agent_id=agent_id,
                    scope=scope,
                    expires_in_ms=3600000  # 1 hour
                )
                consent_tokens[scope.value] = token_obj.token
                print(f"✅ Generated token for {scope.value}")
                print(f"   Token: {token_obj.token[:50]}...")
            except Exception as e:
                print(f"❌ Failed to generate token for {scope.value}: {e}")
        
        return consent_tokens, user_id
        
    except Exception as e:
        print(f"❌ Token generation error: {e}")
        return {}, ""

def test_excel_personalization():
    """Test MailerPanda with Excel personalization using real consent tokens."""
    
    print(f"\n📊 Testing Excel Personalization with Real Tokens")
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
        
        # Test input for personalized email campaign
        user_input = """
        Send promotional emails about our new AI chatbot service to contacts in the Excel file.
        
        Subject: Introducing Our Revolutionary AI Chatbot Service
        
        The email should:
        - Welcome each contact personally
        - Introduce our AI chatbot capabilities
        - Highlight how it can solve their specific business challenges
        - Include a call-to-action to schedule a demo
        - Use a professional but friendly tone
        
        Please use the descriptions in the Excel file to personalize each email based on the contact's interests and background.
        """
        
        print(f"\n📧 Testing personalized email campaign...")
        print(f"📋 User Input: {user_input[:100]}...")
        print(f"📊 Excel File: email_list_with_descriptions.xlsx")
        print(f"🎯 Personalization: ENABLED")
        print(f"🧠 Mode: smart")
        
        # Test with personalization enabled
        result = agent.handle(
            user_id=user_id,
            consent_tokens=consent_tokens,
            user_input=user_input,
            mode="interactive",
            enable_description_personalization=True,
            excel_file_path="hushh_mcp/agents/mailerpanda/email_list_with_descriptions.xlsx",
            personalization_mode="smart"
        )
        
        print(f"\n📊 Agent Execution Results:")
        print(f"Status: {result.get('status', 'Unknown')}")
        
        if result.get('status') == 'permission_denied':
            print(f"❌ Permission denied: {result.get('error')}")
            return False
        
        # Check personalization results
        if 'personalized_count' in result:
            print(f"\n🎯 Personalization Statistics:")
            print(f"  📧 Personalized Emails: {result.get('personalized_count', 0)}")
            print(f"  📧 Standard Emails: {result.get('standard_count', 0)}")
            print(f"  📊 Description Column Detected: {result.get('description_column_detected', False)}")
            print(f"  👥 Contacts with Descriptions: {result.get('contacts_with_descriptions', 0)}")
        
        if 'email_template' in result:
            template = result['email_template']
            print(f"\n📧 Generated Email Template:")
            print(f"  Subject: {template.get('subject', 'No subject')}")
            if isinstance(template.get('body'), str):
                print(f"  Body Preview: {template['body'][:200]}...")
            else:
                print(f"  Body: {template.get('body', 'No body')}")
        
        if 'emails_sent' in result:
            print(f"\n📤 Email Sending Results:")
            print(f"  Emails Sent: {result['emails_sent']}")
            
        if 'send_status' in result and result['send_status']:
            print(f"  📋 Send Status: {result['send_status']}")
            
        if result.get('requires_approval'):
            print(f"\n⏳ Campaign requires human approval")
            print(f"🔄 Status: {result.get('approval_status', 'pending')}")
        
        if 'errors' in result and result['errors']:
            print(f"\n⚠️ Errors: {result['errors']}")
        
        return result.get('status') not in ['error', 'permission_denied']
        
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_excel_file():
    """Check if the Excel file with descriptions exists."""
    
    print(f"\n📋 Checking Excel File")
    print("=" * 25)
    
    excel_path = Path("hushh_mcp/agents/mailerpanda/email_list_with_descriptions.xlsx")
    
    if excel_path.exists():
        print(f"✅ Excel file found: {excel_path}")
        
        try:
            import pandas as pd
            df = pd.read_excel(excel_path)
            print(f"📊 Rows: {len(df)}")
            print(f"📊 Columns: {list(df.columns)}")
            
            if 'description' in df.columns:
                print(f"✅ Description column found!")
                desc_count = df['description'].notna().sum()
                print(f"📝 Contacts with descriptions: {desc_count}/{len(df)}")
                
                # Show first few descriptions
                print(f"\n📝 Sample Descriptions:")
                for idx, desc in df[df['description'].notna()]['description'].head(3).items():
                    print(f"  {idx+1}. {desc[:100]}...")
            else:
                print(f"❌ Description column not found!")
                
        except Exception as e:
            print(f"❌ Error reading Excel: {e}")
    else:
        print(f"❌ Excel file not found: {excel_path}")
        print(f"📍 Current directory: {Path.cwd()}")

if __name__ == "__main__":
    print("🧪 MailerPanda Real Consent Tokens & Personalization Test")
    print("=" * 65)
    
    # Check Excel file first
    check_excel_file()
    
    # Test with real consent tokens
    success = test_excel_personalization()
    
    print(f"\n📋 Test Summary:")
    if success:
        print(f"🎉 SUCCESS! MailerPanda personalization test completed successfully!")
        print(f"✅ Real consent tokens working")
        print(f"✅ Excel personalization functional") 
        print(f"📧 Check your email for personalized messages!")
    else:
        print(f"❌ Test failed - check the errors above")
        print(f"💡 Common issues:")
        print(f"   - Consent token validation")
        print(f"   - Excel file path")
        print(f"   - API credentials")
    
    print(f"\n✅ Test completed!")
