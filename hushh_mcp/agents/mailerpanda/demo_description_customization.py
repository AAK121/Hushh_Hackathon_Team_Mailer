"""
Demo script to test the new description-based email customization feature in MailerPanda agent.

This script demonstrates:
1. Reading Excel file with description column
2. AI-powered personalization based on individual descriptions
3. Fallback to standard templates for contacts without descriptions
"""

import os
import sys
from datetime import datetime

# Add parent directory to path to import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from index import MassMailerAgent
from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope

def demo_description_customization():
    """
    Demonstrates the new description-based email customization feature.
    """
    print("🚀 MailerPanda Description-Based Customization Demo")
    print("=" * 60)
    
    # Initialize agent (you can provide API keys here)
    agent = MassMailerAgent({
        'google_api_key': os.environ.get('GOOGLE_API_KEY', ''),
        'mailjet_api_key': os.environ.get('MAILJET_API_KEY', ''),
        'mailjet_api_secret': os.environ.get('MAILJET_API_SECRET', '')
    })
    
    # Generate consent tokens for demo
    user_id = "demo_user_123"
    consent_tokens = {
        'vault_read_email': issue_token(user_id, ConsentScope.VAULT_READ_EMAIL, expires_in_hours=24),
        'vault_write_email': issue_token(user_id, ConsentScope.VAULT_WRITE_EMAIL, expires_in_hours=24),
        'vault_read_file': issue_token(user_id, ConsentScope.VAULT_READ_FILE, expires_in_hours=24),
        'vault_write_file': issue_token(user_id, ConsentScope.VAULT_WRITE_FILE, expires_in_hours=24),
        'custom_temporary': issue_token(user_id, ConsentScope.CUSTOM_TEMPORARY, expires_in_hours=24)
    }
    
    print(f"👤 User ID: {user_id}")
    print(f"🔑 Generated {len(consent_tokens)} consent tokens")
    print()
    
    # Demo user input for email campaign
    user_input = """
    Create a professional email campaign announcing our new AI-powered project management tool. 
    Include key features like automated task scheduling, smart resource allocation, and real-time collaboration.
    Make it engaging and highlight the benefits for different types of users.
    """
    
    print("📧 Email Campaign Request:")
    print(f"   {user_input.strip()}")
    print()
    
    try:
        # Execute the agent with interactive mode first to see the generated template
        print("🎯 Step 1: Testing in interactive mode to see base template...")
        result = agent.handle(
            user_id=user_id,
            consent_tokens=consent_tokens,
            user_input=user_input,
            mode="interactive"
        )
        
        if result['status'] == 'complete':
            print("✅ Demo mode completed successfully")
            print(f"📊 Campaign ID: {result.get('campaign_summary', {}).get('campaign_id', 'N/A')}")
            print()
        
        # Now test the description-based customization
        print("🎯 Step 2: Testing description-based customization...")
        print("📋 This will use the email_list_with_descriptions.xlsx file")
        print("✨ Each contact will get a personalized email based on their description")
        print()
        
        # Ask user if they want to proceed with actual sending
        proceed = input("⚠️  Do you want to proceed with sending actual emails? (y/N): ").lower().strip()
        
        if proceed == 'y':
            print("🚀 Executing interactive mode with description-based customization...")
            
            # Execute in interactive mode
            result = agent.handle(
                user_id=user_id,
                consent_tokens=consent_tokens,
                user_input=user_input,
                mode="interactive"
            )
            
            print("\n🎉 Campaign Execution Results:")
            print(f"   Status: {result.get('status', 'unknown')}")
            
            if result.get('campaign_summary'):
                summary = result['campaign_summary']
                print(f"   Campaign ID: {summary.get('campaign_id', 'N/A')}")
                print(f"   Emails Sent: {summary.get('total_sent', 0)}")
                print(f"   Failed: {summary.get('total_failed', 0)}")
                print(f"   Vault Keys: {list(summary.get('vault_storage', {}).keys())}")
                print(f"   Trust Links: {len(summary.get('trust_links', []))}")
        else:
            print("✅ Demo completed without sending actual emails")
            
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        return False
    
    return True

def show_feature_overview():
    """Shows an overview of the new description-based customization feature."""
    print("\n📚 New Feature Overview: Description-Based Email Customization")
    print("=" * 70)
    
    features = [
        "✨ AI-powered email personalization based on individual contact descriptions",
        "📊 Automatic detection of 'description' column in Excel files",
        "🎯 Customized content while maintaining core message and placeholders",
        "🔄 Fallback to standard templates for contacts without descriptions",
        "🔒 Full HushMCP consent validation for AI personalization",
        "📝 Professional tone maintenance with relevant context integration",
        "⚡ Seamless integration with existing MailerPanda workflow"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"{i:2d}. {feature}")
    
    print("\n📋 Excel File Requirements:")
    print("   - Standard columns: name, email, company_name")
    print("   - New optional column: description")
    print("   - Description example: 'Long-time customer, prefers technical details'")
    print("   - Leave description empty for standard template")
    
    print("\n🔧 How It Works:")
    print("   1. Agent detects if 'description' column exists in Excel")
    print("   2. For each contact with description:")
    print("      - Validates consent for AI content generation")
    print("      - Uses Gemini AI to customize base email template")
    print("      - Incorporates contact-specific context naturally")
    print("   3. For contacts without description: uses standard template")
    print("   4. All emails maintain placeholders and professional tone")

if __name__ == "__main__":
    show_feature_overview()
    
    proceed = input("\n🚀 Run the demo? (y/N): ").lower().strip()
    if proceed == 'y':
        success = demo_description_customization()
        if success:
            print("\n✅ Demo completed successfully!")
        else:
            print("\n❌ Demo encountered errors.")
    else:
        print("\n👋 Demo cancelled. Run this script again when ready!")
