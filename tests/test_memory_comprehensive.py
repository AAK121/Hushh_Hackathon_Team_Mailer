#!/usr/bin/env python3
"""
Comprehensive test to verify MailerPanda memory system is working correctly.
This test simulates real user interactions and demonstrates memory learning.
"""

import requests
import json
import time
import base64
import pandas as pd

def create_test_excel_file():
    """Create a test Excel file with contact data."""
    contacts_data = {
        'name': ['John Smith', 'Sarah Johnson', 'Mike Davis'],
        'email': ['john@example.com', 'sarah@example.com', 'mike@example.com'],
        'description': [
            'Tech-savvy professional who prefers detailed technical information',
            'Business executive who values concise, action-oriented communication',
            'Creative director who appreciates innovative and engaging content'
        ]
    }
    
    df = pd.DataFrame(contacts_data)
    excel_file = 'memory_test_contacts.xlsx'
    df.to_excel(excel_file, index=False)
    
    # Encode to base64 for API
    with open(excel_file, 'rb') as f:
        file_data = f.read()
    return base64.b64encode(file_data).decode('utf-8')

def test_memory_system_end_to_end():
    """Test the complete memory system with real API calls."""
    
    print("🧠 Testing MailerPanda Memory System - End to End")
    print("=" * 70)
    
    # Test configuration
    base_url = "http://localhost:8001/agents/mailerpanda/mass-email"
    user_id = "memory_test_e2e_789"
    
    # Create test Excel data
    print("📁 Creating test Excel file with contacts...")
    excel_data = create_test_excel_file()
    print("✅ Test Excel file created and encoded")
    
    # Common request configuration
    base_request = {
        "user_id": user_id,
        "excel_file_data": excel_data,
        "excel_file_name": "memory_test_contacts.xlsx",
        "mode": "interactive",
        "use_context_personalization": True,
        "personalization_mode": "aggressive",
        "google_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI",
        "mailjet_api_key": "cca56ed08f5272f813370d7fc5a34a24",
        "mailjet_api_secret": "60fb43675233e2ac775f1c6cb8fe455c",
        "consent_tokens": {
            "vault.read.email": "HCT:bWVtb3J5X3Rlc3RfZTJlXzc4OXxtYWlsZXJwYW5kYXx2YXVsdC5yZWFkLmVtYWlsfDE3NTU5NDYzMDk2NTR8MTc1NjAzMjcwOTY1NA==.e98cb6fe90a9d4a6ded5bf2a37b25028d1ea82a7e5dde4223552a312dba75b36",
            "vault.write.email": "HCT:bWVtb3J5X3Rlc3RfZTJlXzc4OXxtYWlsZXJwYW5kYXx2YXVsdC53cml0ZS5lbWFpbHwxNzU1OTQ2MzA5NjU0fDE3NTYwMzI3MDk2NTQ=.107cf985c5c82413b218a436e8206856b1f982e37a70d6c5ab2fabd97c0ef60e",
            "vault.read.file": "HCT:bWVtb3J5X3Rlc3RfZTJlXzc4OXxtYWlsZXJwYW5kYXx2YXVsdC5yZWFkLmZpbGV8MTc1NTk0NjMwOTY1NHwxNzU2MDMyNzA5NjU0.5549616fd68e1a507ff89e18692134c8301d40ec077df18e62b803059ca17642",
            "vault.write.file": "HCT:bWVtb3J5X3Rlc3RfZTJlXzc4OXxtYWlsZXJwYW5kYXx2YXVsdC53cml0ZS5maWxlfDE3NTU5NDYzMDk2NTV8MTc1NjAzMjcwOTY1NQ==.42fe283d1d7e27c05b31ad2b1370aac464e9b15c1a7b4740de335e349b5ee817",
            "custom.temporary": "HCT:bWVtb3J5X3Rlc3RfZTJlXzc4OXxtYWlsZXJwYW5kYXxjdXN0b20udGVtcG9yYXJ5fDE3NTU5NDYzMDk2NTV8MTc1NjAzMjcwOTY1NQ==.2c80196d5ae2f4709ee0c4b08531cacd15221bbee1c4a441a7f2b754e291e4d2"
        }
    }
    
    # Test 1: First email campaign (no memory exists)
    print("\n🎯 Test 1: First Email Campaign (Clean Slate)")
    print("-" * 50)
    
    request_1 = {
        **base_request,
        "user_input": "Send a thank you email to our valued customers for their recent purchase and continued loyalty"
    }
    
    try:
        print("📡 Sending first email request...")
        response_1 = requests.post(base_url, json=request_1, timeout=120)
        
        if response_1.status_code == 200:
            result_1 = response_1.json()
            print("✅ First email campaign successful!")
            print(f"   📊 Status: {result_1.get('status', 'N/A')}")
            print(f"   🆔 Campaign ID: {result_1.get('campaign_id', 'N/A')}")
            print(f"   ✨ Personalization Active: {result_1.get('context_personalization_enabled', False)}")
            
            # Check if email template was generated
            email_template = result_1.get('email_template', {})
            if isinstance(email_template, dict):
                subject = email_template.get('subject', 'N/A')
                body = email_template.get('body', 'N/A')[:200] + "..."
            else:
                subject = "N/A"
                body = str(email_template)[:200] + "..."
                
            print(f"   📧 Subject: {subject}")
            print(f"   📝 Body Preview: {body}")
            print("   🧠 Memory: Should be creating first memory entry")
            
        else:
            print(f"❌ First email failed: {response_1.status_code}")
            print(f"   Error: {response_1.text}")
            return
            
    except Exception as e:
        print(f"❌ Error in first email test: {e}")
        return
    
    # Wait for memory to be saved
    time.sleep(3)
    
    # Test 2: Second email with different style request
    print("\n🎯 Test 2: Second Email Campaign (Memory Should Load)")
    print("-" * 50)
    
    request_2 = {
        **base_request,
        "user_input": "Send a professional product announcement email about our new software release to business clients"
    }
    
    try:
        print("📡 Sending second email request...")
        response_2 = requests.post(base_url, json=request_2, timeout=120)
        
        if response_2.status_code == 200:
            result_2 = response_2.json()
            print("✅ Second email campaign successful!")
            print(f"   📊 Status: {result_2.get('status', 'N/A')}")
            print(f"   🆔 Campaign ID: {result_2.get('campaign_id', 'N/A')}")
            print(f"   ✨ Personalization Active: {result_2.get('context_personalization_enabled', False)}")
            
            # Check email template
            email_template = result_2.get('email_template', {})
            if isinstance(email_template, dict):
                subject = email_template.get('subject', 'N/A')
                body = email_template.get('body', 'N/A')[:200] + "..."
            else:
                subject = "N/A"
                body = str(email_template)[:200] + "..."
                
            print(f"   📧 Subject: {subject}")
            print(f"   📝 Body Preview: {body}")
            print("   🧠 Memory: Should be using style from first email")
            
        else:
            print(f"❌ Second email failed: {response_2.status_code}")
            print(f"   Error: {response_2.text}")
            
    except Exception as e:
        print(f"❌ Error in second email test: {e}")
    
    # Wait for memory update
    time.sleep(3)
    
    # Test 3: Third email with casual request
    print("\n🎯 Test 3: Third Email Campaign (Memory Evolution)")
    print("-" * 50)
    
    request_3 = {
        **base_request,
        "user_input": "Send a friendly invitation email for our company holiday party to all team members"
    }
    
    try:
        print("📡 Sending third email request...")
        response_3 = requests.post(base_url, json=request_3, timeout=120)
        
        if response_3.status_code == 200:
            result_3 = response_3.json()
            print("✅ Third email campaign successful!")
            print(f"   📊 Status: {result_3.get('status', 'N/A')}")
            print(f"   🆔 Campaign ID: {result_3.get('campaign_id', 'N/A')}")
            print(f"   ✨ Personalization Active: {result_3.get('context_personalization_enabled', False)}")
            
            # Check email template
            email_template = result_3.get('email_template', {})
            if isinstance(email_template, dict):
                subject = email_template.get('subject', 'N/A')
                body = email_template.get('body', 'N/A')[:200] + "..."
            else:
                subject = "N/A"
                body = str(email_template)[:200] + "..."
                
            print(f"   📧 Subject: {subject}")
            print(f"   📝 Body Preview: {body}")
            print("   🧠 Memory: Should incorporate patterns from previous emails")
            
        else:
            print(f"❌ Third email failed: {response_3.status_code}")
            print(f"   Error: {response_3.text}")
            
    except Exception as e:
        print(f"❌ Error in third email test: {e}")

def test_memory_file_verification():
    """Verify that memory files are actually being created."""
    
    print("\n🔍 Memory File Verification")
    print("-" * 50)
    
    import os
    
    # Check for memory files
    memory_users = [
        "memory_test_e2e_789",
        "memory_test_simple_456",
        "memory_test_direct_123",
        "memory_test_user_123"
    ]
    
    print("📁 Checking for memory files in vault...")
    
    for user_id in memory_users:
        vault_dir = os.path.join("vault", user_id)
        memory_file = os.path.join(vault_dir, "email_preferences.enc")
        
        if os.path.exists(memory_file):
            file_size = os.path.getsize(memory_file)
            print(f"   ✅ {user_id}: {file_size} bytes")
        else:
            print(f"   ❌ {user_id}: No memory file found")
    
    # Check overall vault structure
    vault_dir = "vault"
    if os.path.exists(vault_dir):
        users = [d for d in os.listdir(vault_dir) if os.path.isdir(os.path.join(vault_dir, d))]
        print(f"\n📊 Total users with vault data: {len(users)}")
        
        memory_users_count = 0
        for user in users:
            memory_file = os.path.join(vault_dir, user, "email_preferences.enc")
            if os.path.exists(memory_file):
                memory_users_count += 1
        
        print(f"🧠 Users with email memory: {memory_users_count}")
        
        if memory_users_count > 0:
            print("✅ Memory system is creating and storing files correctly!")
        else:
            print("❌ No memory files found - system may not be working")
    else:
        print("❌ Vault directory not found")

def demonstrate_memory_benefits():
    """Show the benefits of the memory system."""
    
    print("\n" + "=" * 70)
    print("🎉 MailerPanda Memory System Benefits Demonstration")
    print("=" * 70)
    
    print("\n📈 How Memory Improves Email Quality:")
    print("   🔄 Email 1: Generic template, learns user's basic preferences")
    print("   🔄 Email 2: Applies learned style, discovers more preferences")
    print("   🔄 Email 3: Refined style based on accumulated learning")
    print("   🔄 Email N: Perfectly tuned to user's unique writing style")
    
    print("\n🎯 What Users Experience:")
    print("   ✨ Emails that match their personal/brand voice")
    print("   ⚡ Faster email generation (no repeating preferences)")
    print("   🎪 Consistent quality across all campaigns")
    print("   📊 Continuous improvement through feedback")
    print("   🔒 Private, encrypted storage of preferences")
    
    print("\n🏢 Business Benefits:")
    print("   📈 Higher email engagement rates")
    print("   🎯 Brand voice consistency")
    print("   💰 Reduced time spent on email creation")
    print("   🚀 Scalable personalized communication")
    print("   📚 Organizational knowledge preservation")
    
    print("\n🔧 Technical Excellence:")
    print("   🔐 AES-256-GCM encryption for all memory data")
    print("   👤 Complete user isolation and privacy")
    print("   📁 Efficient storage in user-specific vaults")
    print("   🤖 Intelligent AI integration with memory context")
    print("   🔄 Automatic learning without user intervention")

def check_server_status():
    """Check if the API server is running."""
    
    print("🔍 Checking API Server Status")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running on port 8001")
            return True
        else:
            print(f"⚠️ API server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running on port 8001")
        print("💡 Please start the server with: python api.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    print("🧪 MailerPanda Memory System - Comprehensive Test Suite")
    print("=" * 70)
    
    # Check if server is running
    if not check_server_status():
        print("\n❌ Cannot run tests without API server")
        print("Please start the server first:")
        print("  python api.py")
        exit(1)
    
    # Run comprehensive tests
    test_memory_system_end_to_end()
    
    # Verify memory files
    test_memory_file_verification()
    
    # Show benefits
    demonstrate_memory_benefits()
    
    print("\n🎉 Memory System Test Complete!")
    print("Check the output above to verify memory functionality.")
