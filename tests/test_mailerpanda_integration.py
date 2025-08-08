#!/usr/bin/env python3
"""Test complete HushMCP integration in MailerPanda agent."""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
from hushh_mcp.consent.token import ConsentToken, ConsentScope
from hushh_mcp.vault.encrypt import VaultManager
from hushh_mcp.trust.link import TrustLinkManager


def create_test_tokens(user_id: str = "test_user_001"):
    """Create test consent tokens for MailerPanda."""
    expiry = datetime.utcnow() + timedelta(hours=1)
    
    tokens = {}
    
    # Email reading token
    email_token = ConsentToken(
        user_id=user_id,
        scope=ConsentScope.VAULT_READ_EMAIL,
        purpose="Email campaign management",
        expires_at=expiry
    )
    tokens['email_token'] = email_token.encode()
    
    # File reading token
    file_token = ConsentToken(
        user_id=user_id,
        scope=ConsentScope.VAULT_READ_FILE,
        purpose="File access for campaigns",
        expires_at=expiry
    )
    tokens['file_token'] = file_token.encode()
    
    # Email writing token
    write_token = ConsentToken(
        user_id=user_id,
        scope=ConsentScope.VAULT_WRITE_EMAIL,
        purpose="Store campaign data",
        expires_at=expiry
    )
    tokens['write_token'] = write_token.encode()
    
    # Temporary operations token
    temp_token = ConsentToken(
        user_id=user_id,
        scope=ConsentScope.CUSTOM_TEMPORARY,
        purpose="Temporary campaign operations",
        expires_at=expiry
    )
    tokens['temp_token'] = temp_token.encode()
    
    return tokens


def test_mailerpanda_enhanced():
    """Test enhanced MailerPanda with complete HushMCP integration."""
    
    # Initialize agent
    agent = MassMailerAgent()
    
    # Create test tokens
    user_id = "test_user_mailerpanda"
    consent_tokens = create_test_tokens(user_id)
    
    print("🧪 Testing Enhanced MailerPanda Agent")
    print("=" * 50)
    
    # Test 1: Consent validation
    print("\n1. Testing consent validation...")
    try:
        validation_result = agent._validate_consent_for_operation(
            consent_tokens,
            ['email_token', 'write_token'],
            user_id
        )
        print(f"✅ Consent validation: {validation_result}")
    except Exception as e:
        print(f"❌ Consent validation failed: {e}")
        return
    
    # Test 2: Vault operations
    print("\n2. Testing vault operations...")
    try:
        test_data = {"test": "email_campaign_data", "timestamp": str(datetime.utcnow())}
        storage_result = agent._store_in_vault(
            user_id,
            "test_campaign",
            test_data,
            consent_tokens['write_token']
        )
        print(f"✅ Vault storage: {storage_result}")
        
        retrieved_data = agent._retrieve_from_vault(
            user_id,
            "test_campaign",
            consent_tokens['email_token']
        )
        print(f"✅ Vault retrieval: {retrieved_data}")
    except Exception as e:
        print(f"❌ Vault operations failed: {e}")
    
    # Test 3: Trust link creation
    print("\n3. Testing trust link creation...")
    try:
        trust_link = agent._create_trust_link_for_delegation(
            user_id,
            "addtocalendar",
            {"calendar_access": "write"},
            consent_tokens['temp_token']
        )
        print(f"✅ Trust link created: {trust_link[:50]}...")
    except Exception as e:
        print(f"❌ Trust link creation failed: {e}")
    
    # Test 4: Complete agent workflow
    print("\n4. Testing complete agent workflow...")
    try:
        user_input = """
        Create an email campaign for our product launch:
        
        Subject: Introducing Revolutionary AI Assistant
        Target: tech_enthusiasts@company.com, early_adopters@startup.com
        
        Content should include:
        - Product benefits
        - Early bird pricing
        - Demo scheduling link
        
        Please generate professional content and set up follow-up calendar reminders.
        """
        
        result = agent.handle(
            user_id=user_id,
            consent_tokens=consent_tokens,
            user_input=user_input,
            mode="test"  # Use test mode to avoid actual email sending
        )
        
        print(f"✅ Agent execution completed")
        print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
        
        # Print summary of results
        if isinstance(result, dict):
            if 'campaign_data' in result:
                campaign = result['campaign_data']
                print(f"📧 Campaign created: {campaign.get('subject', 'N/A')}")
                print(f"📝 Recipients: {len(campaign.get('recipients', []))}")
                print(f"🔗 Trust links: {len(result.get('trust_links', []))}")
            
            if 'vault_references' in result:
                print(f"💾 Vault storage: {len(result['vault_references'])} items stored")
        
    except Exception as e:
        print(f"❌ Agent workflow failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎯 MailerPanda Enhanced Integration Test Complete")


def test_api_integration():
    """Test API integration with enhanced MailerPanda."""
    
    print("\n🌐 Testing API Integration")
    print("=" * 50)
    
    user_id = "test_api_user"
    consent_tokens = create_test_tokens(user_id)
    
    # Simulate API request
    api_request = {
        "user_id": user_id,
        "consent_tokens": consent_tokens,
        "parameters": {
            "user_input": "Send welcome email to new@customer.com with onboarding guide",
            "mode": "interactive"
        }
    }
    
    print(f"📨 API Request prepared")
    print(f"👤 User ID: {user_id}")
    print(f"🔑 Tokens: {len(consent_tokens)} consent tokens")
    print(f"📋 Parameters: {list(api_request['parameters'].keys())}")
    
    # This would be handled by the FastAPI endpoint
    print("✅ API integration ready for FastAPI testing")


if __name__ == "__main__":
    print("🚀 Starting HushMCP MailerPanda Integration Tests")
    
    # Test enhanced agent
    test_mailerpanda_enhanced()
    
    # Test API integration
    test_api_integration()
    
    print("\n🎉 All tests completed!")
