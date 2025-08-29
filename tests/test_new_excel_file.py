#!/usr/bin/env python3
"""
Direct test with the new multi_email_test.xlsx file
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

def test_new_multi_email_file():
    """Test directly with the new multi_email_test.xlsx file."""
    
    print("🎯 Testing New Multi-Email Excel File")
    print("=" * 45)
    
    try:
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # Generate consent tokens
        user_id = "test_user_new_file"
        agent_id = "agent_mailerpanda"
        
        consent_tokens = {}
        required_scopes = [
            ConsentScope.VAULT_READ_EMAIL,
            ConsentScope.CUSTOM_TEMPORARY,
            ConsentScope.VAULT_WRITE_EMAIL,
            ConsentScope.VAULT_READ_FILE,
            ConsentScope.VAULT_WRITE_FILE
        ]
        
        print("🔐 Generating consent tokens...")
        for scope in required_scopes:
            token = issue_token(user_id=user_id, agent_id=agent_id, scope=scope, expires_in_ms=3600000)
            consent_tokens[scope.value] = token.token
            print(f"✅ {scope.value}")
        
        # Get API keys
        api_keys = {
            'google_api_key': os.environ.get('GOOGLE_API_KEY'),
            'mailjet_api_key': os.environ.get('MAILJET_API_KEY'),
            'mailjet_api_secret': os.environ.get('MAILJET_API_SECRET')
        }
        
        print(f"\n🚀 Initializing MailerPanda...")
        agent = MassMailerAgent(api_keys=api_keys)
        
        # Test with the new Excel file specifically
        excel_file_path = "hushh_mcp/agents/mailerpanda/multi_email_test.xlsx"
        
        print(f"\n📁 Using Excel file: {excel_file_path}")
        
        # Verify the file exists and show contents
        import pandas as pd
        df = pd.read_excel(excel_file_path)
        print(f"📊 File contains {len(df)} recipients:")
        for i, row in df.iterrows():
            print(f"  {i+1}. {row['name']} ({row['email']}) - {row['description'][:50]}...")
        
        user_input = """
        Send personalized emails about our AI email platform.
        
        Subject: AI Email Platform - Personalized for Your Needs
        
        Customize content based on recipient's background:
        - Gaming developers: Focus on technical APIs and integration
        - Professional engineers: Emphasize efficiency and business value
        - Students: Highlight learning opportunities and educational content
        
        Use their descriptions to personalize the tone and examples.
        """
        
        print(f"\n🔄 Executing campaign with new Excel file...")
        result = agent.handle(
            user_id=user_id,
            consent_tokens=consent_tokens,
            user_input=user_input,
            mode="interactive",
            enable_description_personalization=True,
            excel_file_path=excel_file_path,  # Explicitly specify the new file
            personalization_mode="smart"
        )
        
        print(f"\n📊 Results:")
        print(f"Status: {result.get('status', 'Unknown')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Direct Multi-Email Test")
    print("=" * 30)
    
    result = test_new_multi_email_file()
    
    if result:
        print(f"\n✅ Test completed with status: {result.get('status')}")
    else:
        print(f"\n❌ Test failed!")
