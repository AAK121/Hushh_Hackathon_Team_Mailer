#!/usr/bin/env python3
"""
Check which email is currently configured for sending in MailerPanda
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_sender_email_configuration():
    """Check all sources of sender email configuration."""
    
    print("📧 MailerPanda Sender Email Configuration")
    print("=" * 50)
    
    # Check 1: Environment variable
    sender_email_env = os.environ.get("SENDER_EMAIL")
    print(f"🔍 Environment Variable SENDER_EMAIL: {sender_email_env or 'Not set'}")
    
    # Check 2: .env file
    env_file_path = Path(__file__).parent / ".env"
    sender_email_file = None
    
    if env_file_path.exists():
        print(f"📄 Checking .env file...")
        with open(env_file_path, 'r') as f:
            for line in f:
                if line.strip().startswith("SENDER_EMAIL="):
                    sender_email_file = line.split("=", 1)[1].strip()
                    break
        
        print(f"🔍 .env file SENDER_EMAIL: {sender_email_file or 'Not found'}")
    else:
        print(f"❌ .env file not found")
    
    # Check 3: Default fallback in code
    default_email = "default@sender.com"
    print(f"🔍 Code default fallback: {default_email}")
    
    # Check 4: What would actually be used
    actual_sender = sender_email_env or sender_email_file or default_email
    print(f"\n✅ ACTUAL SENDER EMAIL USED: {actual_sender}")
    
    # Check 5: Notebook configuration
    print(f"\n📓 Notebook Configuration:")
    print(f"🔍 Old notebook uses: dragnoid121@gmail.com (hardcoded)")
    print(f"🔍 Previous test emails sent from: alokkale121@gmail.com")
    
    # Check 6: Current MailerPanda agent
    try:
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        print(f"\n🤖 MailerPanda Agent Configuration:")
        print(f"📧 The agent will use: {actual_sender}")
        print(f"📧 From name: 'MailerPanda Agent'")
    except Exception as e:
        print(f"❌ Error checking agent: {e}")
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"  Current sender email: {actual_sender}")
    print(f"  Source: {'Environment' if sender_email_env else '.env file' if sender_email_file else 'Default fallback'}")
    
    if actual_sender == "default@sender.com":
        print(f"\n⚠️  WARNING: Using default fallback email!")
        print(f"   This email will likely be rejected by recipients")
        print(f"   Configure SENDER_EMAIL in .env file or environment")
    
    return actual_sender

def show_email_configuration_fix():
    """Show how to properly configure sender email."""
    
    print(f"\n🛠️  How to Configure Sender Email")
    print("=" * 40)
    
    print(f"""
📝 Option 1: Add to .env file
   Add this line to your .env file:
   SENDER_EMAIL=your-verified-email@yourdomain.com

📝 Option 2: Set environment variable
   In terminal: set SENDER_EMAIL=your-email@domain.com

📝 Option 3: Use verified domain
   Examples of good sender emails:
   - noreply@yourdomain.com (if domain is verified in Mailjet)
   - your-email@gmail.com (if Gmail is verified in Mailjet)
   - hello@yourcompany.com (if company domain is verified)

⚠️  Important Notes:
   - The sender email MUST be verified in your Mailjet account
   - Unverified emails will be rejected by Mailjet
   - Use a professional sender address for better deliverability
    """)

if __name__ == "__main__":
    print("🔍 Checking MailerPanda Email Configuration")
    print("=" * 55)
    
    sender_email = check_sender_email_configuration()
    show_email_configuration_fix()
    
    print(f"\n✅ Check completed!")
    print(f"📧 Current sender: {sender_email}")
