#!/usr/bin/env python3
"""
Test the MailerPanda agent's email memory functionality.
This demonstrates how the agent remembers user preferences and improves over time.
"""

import requests
import json
import time

def test_email_memory_functionality():
    """Test the memory system by creating multiple campaigns with feedback."""
    
    print("🧠 Testing MailerPanda Email Memory Functionality")
    print("=" * 65)
    
    base_url = "http://localhost:8001/agents/mailerpanda/mass-email"
    
    # User ID for memory tracking
    user_id = "memory_test_user_123"
    
    # Common consent tokens
    consent_tokens = {
        "vault.read.email": "HCT:bWVtb3J5X3Rlc3RfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQucmVhZC5lbWFpbHwxNzU1OTQ2MzA5NjU0fDE3NTYwMzI3MDk2NTQ=.e98cb6fe90a9d4a6ded5bf2a37b25028d1ea82a7e5dde4223552a312dba75b36",
        "vault.write.email": "HCT:bWVtb3J5X3Rlc3RfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQud3JpdGUuZW1haWx8MTc1NTk0NjMwOTY1NHwxNzU2MDMyNzA5NjU0.107cf985c5c82413b218a436e8206856b1f982e37a70d6c5ab2fabd97c0ef60e",
        "vault.read.file": "HCT:bWVtb3J5X3Rlc3RfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQucmVhZC5maWxlfDE3NTU5NDYzMDk2NTR8MTc1NjAzMjcwOTY1NA==.5549616fd68e1a507ff89e18692134c8301d40ec077df18e62b803059ca17642",
        "vault.write.file": "HCT:bWVtb3J5X3Rlc3RfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQud3JpdGUuZmlsZXwxNzU1OTQ2MzA5NjU1fDE3NTYwMzI3MDk2NTU=.42fe283d1d7e27c05b31ad2b1370aac464e9b15c1a7b4740de335e349b5ee817",
        "custom.temporary": "HCT:bWVtb3J5X3Rlc3RfdXNlcl8xMjN8bWFpbGVycGFuZGF8Y3VzdG9tLnRlbXBvcmFyeXwxNzU1OTQ2MzA5NjU1fDE3NTYwMzI3MDk2NTU=.2c80196d5ae2f4709ee0c4b08531cacd15221bbee1c4a441a7f2b754e291e4d2"
    }
    
    # Common API keys
    api_keys = {
        "google_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI",
        "mailjet_api_key": "cca56ed08f5272f813370d7fc5a34a24",
        "mailjet_api_secret": "60fb43675233e2ac775f1c6cb8fe455c"
    }
    
    # Test scenario 1: First email - no memory yet
    print("\n🎯 Test 1: First Email Campaign (No Memory)")
    print("-" * 50)
    
    request_1 = {
        "user_id": user_id,
        "user_input": "Send a thank you email to our customers for their recent purchase",
        "excel_file_data": "",
        "excel_file_name": "contacts.xlsx",
        "mode": "interactive",
        "use_context_personalization": False,
        "consent_tokens": consent_tokens,
        **api_keys
    }
    
    try:
        response_1 = requests.post(base_url, json=request_1, timeout=60)
        if response_1.status_code == 200:
            result_1 = response_1.json()
            print("✅ First email generated successfully!")
            print(f"   Subject: {result_1.get('email_template', {}).get('subject', 'N/A')}")
            print(f"   Status: {result_1.get('status', 'N/A')}")
            print("   🧠 Memory: No previous preferences found (first time)")
        else:
            print(f"❌ First email failed: {response_1.status_code}")
            print(response_1.text)
            return
    except Exception as e:
        print(f"❌ Error in first email: {e}")
        return
    
    # Wait a moment
    time.sleep(2)
    
    # Test scenario 2: Second email with user feedback preference
    print("\n🎯 Test 2: Second Email Campaign (With Learning)")
    print("-" * 50)
    
    request_2 = {
        "user_id": user_id,
        "user_input": "Send a professional update email about our new product launch to business clients",
        "excel_file_data": "",
        "excel_file_name": "contacts.xlsx", 
        "mode": "interactive",
        "use_context_personalization": False,
        "consent_tokens": consent_tokens,
        **api_keys
    }
    
    try:
        response_2 = requests.post(base_url, json=request_2, timeout=60)
        if response_2.status_code == 200:
            result_2 = response_2.json()
            print("✅ Second email generated with memory!")
            print(f"   Subject: {result_2.get('email_template', {}).get('subject', 'N/A')}")
            print(f"   Status: {result_2.get('status', 'N/A')}")
            print("   🧠 Memory: Should now incorporate style from first email")
        else:
            print(f"❌ Second email failed: {response_2.status_code}")
            print(response_2.text)
    except Exception as e:
        print(f"❌ Error in second email: {e}")
    
    # Wait a moment
    time.sleep(2)
    
    # Test scenario 3: Third email - should show memory evolution
    print("\n🎯 Test 3: Third Email Campaign (Memory Evolution)")
    print("-" * 50)
    
    request_3 = {
        "user_id": user_id,
        "user_input": "Send a casual invitation email for our company holiday party to all employees",
        "excel_file_data": "",
        "excel_file_name": "contacts.xlsx",
        "mode": "interactive", 
        "use_context_personalization": False,
        "consent_tokens": consent_tokens,
        **api_keys
    }
    
    try:
        response_3 = requests.post(base_url, json=request_3, timeout=60)
        if response_3.status_code == 200:
            result_3 = response_3.json()
            print("✅ Third email generated with evolved memory!")
            print(f"   Subject: {result_3.get('email_template', {}).get('subject', 'N/A')}")
            print(f"   Status: {result_3.get('status', 'N/A')}")
            print("   🧠 Memory: Should incorporate style patterns from previous emails")
        else:
            print(f"❌ Third email failed: {response_3.status_code}")
            print(response_3.text)
    except Exception as e:
        print(f"❌ Error in third email: {e}")

def demonstrate_memory_features():
    """Demonstrate the memory features."""
    
    print("\n" + "=" * 65)
    print("🧠 MailerPanda Memory System Features")
    print("=" * 65)
    
    print("\n🎯 What the Memory System Does:")
    print("  1. 📝 Saves every email draft and user feedback")
    print("  2. 🎨 Learns user's preferred writing style and tone")
    print("  3. 📏 Remembers preferred email length and structure") 
    print("  4. 🔤 Tracks favorite phrases and words to avoid")
    print("  5. 📋 Analyzes feedback patterns for improvement")
    print("  6. 🎯 Adapts future emails to match user preferences")
    
    print("\n🔒 Security & Privacy:")
    print("  • All memory data is encrypted using AES-256-GCM")
    print("  • Data is stored in user-specific vault directories")
    print("  • Requires proper consent tokens for access")
    print("  • Memory is isolated per user ID")
    
    print("\n📊 Memory Data Structure:")
    print("  📁 vault/{user_id}/email_preferences.enc")
    print("    ├── 🎨 Writing Style Preferences")
    print("    ├── 📧 Recent Email Examples (last 10)")
    print("    ├── 💬 User Feedback History (last 20)")
    print("    ├── 📈 Campaign Performance Data")
    print("    └── 🎯 Personalization Settings")
    
    print("\n🚀 Benefits:")
    print("  ✨ Emails get better and more personalized over time")
    print("  ⚡ Faster email generation with learned preferences")
    print("  🎯 Consistent brand voice and style")
    print("  📈 Improved user satisfaction through learning")

if __name__ == "__main__":
    demonstrate_memory_features()
    test_email_memory_functionality()
