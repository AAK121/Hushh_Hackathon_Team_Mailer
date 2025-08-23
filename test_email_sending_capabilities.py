#!/usr/bin/env python3
"""
Comprehensive MailerPanda Email Sending Test
============================================

This script tests the actual email sending capabilities of the MailerPanda agent
including the description-based personalization feature.
"""

import requests
import json
from datetime import datetime
import os
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8002"
EXCEL_FILE_PATH = "hushh_mcp/agents/mailerpanda/email_list_with_descriptions.xlsx"

def get_real_credentials():
    """Get real email credentials from environment variables."""
    return {
        "google_api_key": os.getenv("GOOGLE_API_KEY", "your_google_api_key_here"),
        "mailjet_api_key": os.getenv("MAILJET_API_KEY", "your_mailjet_api_key_here"),
        "mailjet_api_secret": os.getenv("MAILJET_API_SECRET", "your_mailjet_secret_here"),
        "sender_email": os.getenv("SENDER_EMAIL", "test@yourdomain.com")
    }

def test_basic_email_sending():
    """Test basic email sending functionality without personalization."""
    
    print("🧪 Testing Basic Email Sending...")
    print("=" * 50)
    
    credentials = get_real_credentials()
    
    # Basic email test request
    test_request = {
        "user_id": "test_user_email_001",
        "consent_tokens": {
            "vault.read.email": "test_email_token_123",
            "vault.write.email": "test_email_token_456",
            "vault.read.file": "test_file_token_789",
            "vault.write.file": "test_file_token_101",
            "custom.temporary": "test_temp_token_202"
        },
        "user_input": "Send a welcome email to our new customers introducing our AI automation services",
        "mode": "headless",  # Skip human approval for testing
        "sender_email": credentials["sender_email"],
        "recipient_emails": ["alokkale121@gmail.com"],  # Single test email
        "enable_description_personalization": False,
        "google_api_key": credentials["google_api_key"],
        "mailjet_api_key": credentials["mailjet_api_key"],
        "mailjet_api_secret": credentials["mailjet_api_secret"]
    }
    
    print(f"📧 Sending basic email to: {test_request['recipient_emails']}")
    print(f"📝 Campaign: {test_request['user_input']}")
    
    try:
        response = requests.post(
            f"{API_BASE}/agents/mailerpanda/execute",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for email sending
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ Basic Email Test Results:")
            print(json.dumps(response_data, indent=2))
            
            if response_data.get("emails_sent", 0) > 0:
                print(f"🎉 SUCCESS: {response_data['emails_sent']} emails sent!")
                return True
            else:
                print("⚠️ No emails were sent")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error Details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        return False

def test_personalized_email_sending():
    """Test email sending with description-based personalization."""
    
    print("\n🎯 Testing Personalized Email Sending...")
    print("=" * 50)
    
    credentials = get_real_credentials()
    
    # Check if Excel file exists
    excel_path = Path(EXCEL_FILE_PATH)
    if not excel_path.exists():
        print(f"❌ Excel file not found: {EXCEL_FILE_PATH}")
        return False
    
    # Personalized email test request
    test_request = {
        "user_id": "test_user_personalized_001",
        "consent_tokens": {
            "vault.read.email": "test_email_token_123",
            "vault.write.email": "test_email_token_456",
            "vault.read.file": "test_file_token_789",
            "vault.write.file": "test_file_token_101",
            "custom.temporary": "test_temp_token_202"
        },
        "user_input": "Send personalized marketing emails about our new AI chatbot service to all contacts in the Excel file",
        "mode": "headless",  # Skip human approval for testing
        "sender_email": credentials["sender_email"],
        "enable_description_personalization": True,
        "excel_file_path": EXCEL_FILE_PATH,
        "personalization_mode": "smart",
        "google_api_key": credentials["google_api_key"],
        "mailjet_api_key": credentials["mailjet_api_key"],
        "mailjet_api_secret": credentials["mailjet_api_secret"]
    }
    
    print(f"📊 Using Excel file: {EXCEL_FILE_PATH}")
    print(f"🎯 Personalization mode: {test_request['personalization_mode']}")
    print(f"📝 Campaign: {test_request['user_input']}")
    
    try:
        response = requests.post(
            f"{API_BASE}/agents/mailerpanda/execute",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=120  # Longer timeout for personalized emails
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ Personalized Email Test Results:")
            print(json.dumps(response_data, indent=2))
            
            # Check personalization statistics
            personalized_count = response_data.get("personalized_count", 0)
            standard_count = response_data.get("standard_count", 0)
            description_detected = response_data.get("description_column_detected", False)
            
            print(f"\n📊 Personalization Statistics:")
            print(f"   🎯 Personalized emails: {personalized_count}")
            print(f"   📧 Standard emails: {standard_count}")
            print(f"   🔍 Description column detected: {description_detected}")
            
            if response_data.get("emails_sent", 0) > 0:
                print(f"🎉 SUCCESS: {response_data['emails_sent']} emails sent!")
                if personalized_count > 0:
                    print(f"✨ BONUS: {personalized_count} emails were personalized!")
                return True
            else:
                print("⚠️ No emails were sent")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error Details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        return False

def test_approval_workflow():
    """Test the human-in-the-loop approval workflow."""
    
    print("\n👥 Testing Approval Workflow...")
    print("=" * 50)
    
    credentials = get_real_credentials()
    
    # Interactive mode test request
    test_request = {
        "user_id": "test_user_approval_001",
        "consent_tokens": {
            "vault.read.email": "test_email_token_123",
            "vault.write.email": "test_email_token_456",
            "vault.read.file": "test_file_token_789",
            "vault.write.file": "test_file_token_101",
            "custom.temporary": "test_temp_token_202"
        },
        "user_input": "Send a newsletter about our latest AI features to the team",
        "mode": "interactive",  # Require human approval
        "sender_email": credentials["sender_email"],
        "recipient_emails": ["alokkale121@gmail.com"],
        "enable_description_personalization": False,
        "google_api_key": credentials["google_api_key"],
        "mailjet_api_key": credentials["mailjet_api_key"],
        "mailjet_api_secret": credentials["mailjet_api_secret"]
    }
    
    print(f"👥 Testing interactive mode with approval workflow")
    
    try:
        response = requests.post(
            f"{API_BASE}/agents/mailerpanda/execute",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ Approval Workflow Test Results:")
            print(json.dumps(response_data, indent=2))
            
            if response_data.get("requires_approval", False):
                campaign_id = response_data.get("campaign_id")
                print(f"🔄 Campaign {campaign_id} requires approval (as expected)")
                
                # Test approval
                approval_request = {
                    "user_id": test_request["user_id"],
                    "campaign_id": campaign_id,
                    "action": "approve"
                }
                
                print("✅ Approving campaign...")
                approval_response = requests.post(
                    f"{API_BASE}/agents/mailerpanda/approve",
                    json=approval_request,
                    headers={"Content-Type": "application/json"}
                )
                
                if approval_response.status_code == 200:
                    approval_data = approval_response.json()
                    print("✅ Approval successful:")
                    print(json.dumps(approval_data, indent=2))
                    return True
                else:
                    print(f"❌ Approval failed: {approval_response.status_code}")
                    return False
            else:
                print("⚠️ Campaign did not require approval (unexpected)")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error Details: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")
        return False

def main():
    """Run comprehensive email sending tests."""
    
    print("🚀 MailerPanda Email Sending Capability Test")
    print("=" * 60)
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base URL: {API_BASE}")
    
    # Check if server is running
    try:
        health_response = requests.get(f"{API_BASE}/health", timeout=5)
        if health_response.status_code != 200:
            print(f"❌ Server health check failed: {health_response.status_code}")
            return
        print("✅ Server is running and healthy")
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("💡 Make sure the API server is running on port 8002")
        return
    
    # Get credentials info
    credentials = get_real_credentials()
    print(f"\n🔐 Credentials Check:")
    print(f"   Google API Key: {'✅ Set' if credentials['google_api_key'] != 'your_google_api_key_here' else '❌ Not set'}")
    print(f"   Mailjet API Key: {'✅ Set' if credentials['mailjet_api_key'] != 'your_mailjet_api_key_here' else '❌ Not set'}")
    print(f"   Mailjet Secret: {'✅ Set' if credentials['mailjet_api_secret'] != 'your_mailjet_secret_here' else '❌ Not set'}")
    print(f"   Sender Email: {credentials['sender_email']}")
    
    # Run tests
    results = []
    
    # Test 1: Basic Email Sending
    results.append(("Basic Email Sending", test_basic_email_sending()))
    
    # Test 2: Personalized Email Sending
    results.append(("Personalized Email Sending", test_personalized_email_sending()))
    
    # Test 3: Approval Workflow
    results.append(("Approval Workflow", test_approval_workflow()))
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 40)
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All email sending tests PASSED! MailerPanda is working perfectly!")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    print(f"\n💡 Note: Make sure you have set real email credentials in environment variables:")
    print("   - GOOGLE_API_KEY")
    print("   - MAILJET_API_KEY") 
    print("   - MAILJET_API_SECRET")
    print("   - SENDER_EMAIL")

if __name__ == "__main__":
    main()
