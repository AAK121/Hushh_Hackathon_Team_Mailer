#!/usr/bin/env python3
"""
Test script for MailerPanda API personalization feature
"""

import requests
import json
from datetime import datetime

# API endpoint
API_BASE = "http://localhost:8002"

def test_mailerpanda_personalization():
    """Test the MailerPanda API with personalization enabled."""
    
    # Test data
    test_request = {
        "user_id": "test_user_001",
        "consent_tokens": {
            "email.send": "test_token_123",
            "data.process": "test_token_456"
        },
        "user_input": "Send promotional emails about our new AI chatbot service to the contact list",
        "mode": "interactive",
        "enable_description_personalization": True,
        "excel_file_path": "email_list_with_descriptions.xlsx",
        "personalization_mode": "smart",
        "google_api_key": "test_key_123",
        "mailjet_api_key": "test_mailjet_key",
        "mailjet_api_secret": "test_mailjet_secret"
    }
    
    print("🧪 Testing MailerPanda API with Personalization...")
    print(f"📊 Request Data: {json.dumps(test_request, indent=2)}")
    
    try:
        # Test the API endpoint
        response = requests.post(
            f"{API_BASE}/agents/mailerpanda/execute",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ API Response:")
            print(json.dumps(response_data, indent=2))
            
            # Check for personalization fields
            if "personalized_count" in response_data:
                print(f"🎯 Personalized Emails: {response_data['personalized_count']}")
            if "standard_count" in response_data:
                print(f"📧 Standard Emails: {response_data['standard_count']}")
            if "description_column_detected" in response_data:
                print(f"🔍 Description Column Detected: {response_data['description_column_detected']}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error Details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("🔌 Connection Error: Make sure the API server is running")
        print("💡 Start the server with: python api.py")
    except Exception as e:
        print(f"❌ Test Error: {str(e)}")

def test_agent_info():
    """Test the agent info endpoint for updated MailerPanda details."""
    
    print("\n🔍 Testing Agent Info Endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/agents")
        
        if response.status_code == 200:
            agents_data = response.json()
            mailerpanda = agents_data.get("agent_mailerpanda", {})
            
            print("📋 MailerPanda Agent Info:")
            print(f"  Name: {mailerpanda.get('name')}")
            print(f"  Version: {mailerpanda.get('version')}")
            print(f"  Description: {mailerpanda.get('description')}")
            
            features = mailerpanda.get('features', [])
            if features:
                print("  Features:")
                for feature in features:
                    indicator = "✨" if "Personalization" in feature else "📌"
                    print(f"    {indicator} {feature}")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 MailerPanda Personalization API Test")
    print("=" * 50)
    
    test_agent_info()
    test_mailerpanda_personalization()
    
    print("\n✅ Test completed!")
    print("💡 If the server isn't running, start it with: python api.py")
