#!/usr/bin/env python3
"""Test the FastAPI server with enhanced MailerPanda agent."""

import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope


def create_test_tokens(user_id: str = "test_api_user"):
    """Create test consent tokens for API testing."""
    expiry = int((datetime.utcnow() + timedelta(hours=1)).timestamp() * 1000)
    
    tokens = {}
    
    # Email reading token
    email_token = issue_token(
        user_id=user_id,
        agent_id="mailerpanda",
        scope=ConsentScope.VAULT_READ_EMAIL,
        expires_in_ms=3600000
    )
    tokens['email_token'] = email_token.token
    
    # Email writing token
    write_token = issue_token(
        user_id=user_id,
        agent_id="mailerpanda", 
        scope=ConsentScope.VAULT_WRITE_EMAIL,
        expires_in_ms=3600000
    )
    tokens['write_token'] = write_token.token
    
    # File reading token
    file_token = issue_token(
        user_id=user_id,
        agent_id="mailerpanda",
        scope=ConsentScope.VAULT_READ_FILE,
        expires_in_ms=3600000
    )
    tokens['file_token'] = file_token.token
    
    # Temporary operations token
    temp_token = issue_token(
        user_id=user_id,
        agent_id="mailerpanda",
        scope=ConsentScope.CUSTOM_TEMPORARY,
        expires_in_ms=3600000
    )
    tokens['temp_token'] = temp_token.token
    
    return tokens


def test_api_server():
    """Test the FastAPI server with MailerPanda agent."""
    
    base_url = "http://127.0.0.1:8001"
    
    print("🌐 Testing FastAPI Server with Enhanced MailerPanda")
    print("=" * 60)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"⚠️ Server responded with status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        print("Please start the server with: python api.py")
        return
    
    # Test 2: Create consent tokens
    print("\n2. Creating consent tokens...")
    user_id = "test_api_user_001"
    consent_tokens = create_test_tokens(user_id)
    print(f"✅ Created {len(consent_tokens)} consent tokens")
    for token_name, token in consent_tokens.items():
        print(f"   📋 {token_name}: {token[:30]}...")
    
    # Test 3: Test basic email campaign
    print("\n3. Testing basic email campaign...")
    campaign_request = {
        "user_id": user_id,
        "consent_tokens": consent_tokens,
        "parameters": {
            "user_input": "Send a welcome email to new@customer.com introducing our company and services",
            "mode": "test"
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/agents/mailerpanda",
            json=campaign_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Campaign request successful")
            print(f"📊 Response keys: {list(result.keys())}")
            
            if 'campaign_data' in result:
                campaign = result['campaign_data']
                print(f"📧 Subject: {campaign.get('subject', 'N/A')}")
                print(f"👥 Recipients: {len(campaign.get('recipients', []))}")
            
            if 'vault_references' in result:
                print(f"💾 Vault items: {len(result['vault_references'])}")
                
        else:
            print(f"❌ Campaign failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Test 4: Test advanced campaign with cross-agent delegation
    print("\n4. Testing advanced campaign with delegation...")
    advanced_request = {
        "user_id": user_id,
        "consent_tokens": consent_tokens,
        "parameters": {
            "user_input": """
            Create a product launch email campaign:
            
            Subject: Revolutionary AI Assistant Launch
            Recipients: tech@startup.com, investors@venture.com
            
            Content:
            - Announce our new AI assistant
            - Highlight key features and benefits
            - Include early bird pricing offer
            - Add call-to-action for demo scheduling
            
            Please also create calendar reminders for follow-up.
            """,
            "mode": "test",
            "delegate_to_calendar": True
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/agents/mailerpanda",
            json=advanced_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Advanced campaign successful")
            
            if 'trust_links' in result:
                print(f"🔗 Trust links created: {len(result['trust_links'])}")
                
            if 'delegation_results' in result:
                print("📅 Calendar delegation successful")
                
        else:
            print(f"❌ Advanced campaign failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Advanced request failed: {e}")
    
    # Test 5: Test error handling
    print("\n5. Testing error handling...")
    
    # Test with missing consent tokens
    invalid_request = {
        "user_id": user_id,
        "consent_tokens": {},  # No tokens
        "parameters": {
            "user_input": "Send test email",
            "mode": "test"
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/agents/mailerpanda",
            json=invalid_request,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Error handling works - missing tokens detected")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error test failed: {e}")
    
    # Test 6: Test agent listing
    print("\n6. Testing agent listing...")
    try:
        response = requests.get(f"{base_url}/agents", timeout=5)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Available agents: {agents}")
        else:
            print(f"⚠️ Agent listing failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Agent listing error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 API Testing Complete")
    print("\nNext Steps:")
    print("1. Test with real Mailjet credentials for actual email sending")
    print("2. Test cross-agent delegation with AddToCalendar")
    print("3. Load test with multiple concurrent requests")
    print("4. Test with various consent token configurations")


if __name__ == "__main__":
    test_api_server()
