#!/usr/bin/env python3
"""
Standalone Approval Workflow Test
"""

import requests
import json

API_BASE_URL = "http://127.0.0.1:8001"

def test_simple_approval():
    """Test the approval workflow with a simple request"""
    print("🚀 Testing Approval Workflow")
    print("=" * 40)
    
    # Test backend status
    print("🔍 Testing backend status...")
    try:
        response = requests.get(f"{API_BASE_URL}/agents/mailerpanda/status")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend status check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return
    
    # Test mass email creation
    print("\n📧 Testing mass email creation...")
    mass_email_data = {
        "user_description": "Create a test email campaign",
        "excel_file": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,UEsDBBQACAgIALiIRVMAAAAAAAAAAAAAAAALAAAAX3JlbHMvLnJlbHONzjEOwjAMhd9/LYg",
        "enable_context_personalization": True,
        "demo_mode": False
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/agents/mailerpanda/mass-email",
            json=mass_email_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Mass email created successfully!")
            campaign_id = result.get('campaign_id', 'test_campaign_123')
            print(f"📊 Campaign ID: {campaign_id}")
        else:
            print(f"❌ Mass email creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            campaign_id = "test_campaign_123"  # Use dummy ID for testing
    except Exception as e:
        print(f"❌ Mass email test failed: {e}")
        campaign_id = "test_campaign_123"
    
    # Test approval workflow
    print(f"\n🔄 Testing approval actions for campaign: {campaign_id}")
    
    approval_actions = ["modify", "regenerate", "approve", "reject"]
    
    for action in approval_actions:
        print(f"\n🎯 Testing {action.upper()} action...")
        
        approval_data = {
            "campaign_id": campaign_id,
            "action": action,
            "feedback": f"Test feedback for {action} action"
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/agents/mailerpanda/approve",
                json=approval_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {action.title()} action successful!")
                print(f"📊 Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ {action.title()} action failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ {action.title()} test failed: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Approval workflow testing completed!")

if __name__ == "__main__":
    test_simple_approval()
