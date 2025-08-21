#!/usr/bin/env python3
"""
Comprehensive Dynamic API Key Test for All Agents
================================================

This test verifies that ALL agents in the HushhMCP system properly accept
API keys dynamically through API parameters rather than hardcoded values.

Agents tested:
1. ChanduFinance - Financial advice with AI analysis
2. RelationshipMemory - Contact and memory management 
3. MailerPanda - Email campaign management
4. AddToCalendar - Email processing and calendar events

This ensures compliance with HushhMCP best practices:
- No hardcoded credentials in agent code
- All API keys provided dynamically via frontend/API
- Secure and flexible credential management
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# API Configuration
BASE_URL = "http://127.0.0.1:8002"
HEADERS = {"Content-Type": "application/json"}

# Test Configuration  
TEST_USER_ID = "test_user_all_agents"
TEST_TOKEN = "HCT:dGVzdF91c2VyXzEyM3xjaGFuZHVmaW5hbmNlfHZhdWx0LndyaXRlLmZpbGV8MTc1NTcwMjYyMDE4MXwxNzU1Nzg5MDIwMTgx.93d1fe656f91c9b68ffbad2cca518b1f30c90f1ed3f8c062a0e38edf5a6f8eb3"

def test_agent_dynamic_keys(agent_name: str, endpoint: str, payload: Dict[str, Any]) -> bool:
    """Test dynamic API key support for a specific agent."""
    
    print(f"\n🧪 Testing {agent_name} Agent")
    print("=" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", 
                               headers=HEADERS, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"✅ PASS: {agent_name} accepts dynamic API keys")
                return True
            else:
                print(f"❌ FAIL: {agent_name} rejected dynamic API keys")
                print(f"Error: {data.get('errors', 'Unknown error')}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception occurred - {e}")
        return False

def run_comprehensive_dynamic_api_test():
    """Run comprehensive test for all agents."""
    
    print("🚀 COMPREHENSIVE DYNAMIC API KEY TEST")
    print("=" * 60)
    print("Testing dynamic API key support across ALL HushhMCP agents")
    print("No hardcoded credentials should be required!")
    print("=" * 60)
    
    results = {}
    
    # Test 1: ChanduFinance Agent
    chandufinance_payload = {
        "user_id": TEST_USER_ID,
        "token": TEST_TOKEN,
        "command": "view_profile",
        "gemini_api_key": "test_gemini_key_chandufinance",
        "api_keys": {
            "custom_finance_key": "test_value"
        }
    }
    results["ChanduFinance"] = test_agent_dynamic_keys(
        "ChanduFinance", 
        "/agents/chandufinance/execute",
        chandufinance_payload
    )
    
    # Test 2: RelationshipMemory Agent  
    relationship_payload = {
        "user_id": TEST_USER_ID,
        "tokens": {
            "vault.read.contacts": TEST_TOKEN,
            "vault.write.contacts": TEST_TOKEN
        },
        "user_input": "Show me my recent contacts",
        "gemini_api_key": "test_gemini_key_relationship",
        "api_keys": {
            "custom_memory_key": "test_value"
        }
    }
    results["RelationshipMemory"] = test_agent_dynamic_keys(
        "RelationshipMemory",
        "/agents/relationship_memory/execute", 
        relationship_payload
    )
    
    # Test 3: MailerPanda Agent
    mailerpanda_payload = {
        "user_id": TEST_USER_ID,
        "user_input": "Create a welcome email campaign",
        "mode": "demo",
        "consent_tokens": {
            "vault.read.email": TEST_TOKEN,
            "vault.write.email": TEST_TOKEN
        },
        "google_api_key": "test_google_key_mailer",
        "mailjet_api_key": "test_mailjet_key",
        "mailjet_api_secret": "test_mailjet_secret",
        "api_keys": {
            "custom_mailer_key": "test_value"
        }
    }
    results["MailerPanda"] = test_agent_dynamic_keys(
        "MailerPanda",
        "/agents/mailerpanda/execute",
        mailerpanda_payload
    )
    
    # Test 4: AddToCalendar Agent
    addtocalendar_payload = {
        "user_id": TEST_USER_ID,
        "email_token": TEST_TOKEN,
        "calendar_token": TEST_TOKEN, 
        "google_access_token": "test_google_oauth_token",
        "action": "analyze_only",
        "google_api_key": "test_google_key_calendar",
        "api_keys": {
            "custom_calendar_key": "test_value"
        }
    }
    results["AddToCalendar"] = test_agent_dynamic_keys(
        "AddToCalendar",
        "/agents/addtocalendar/execute",
        addtocalendar_payload
    )
    
    # Summary Report
    print("\n" + "=" * 60)
    print("🎯 DYNAMIC API KEY TEST SUMMARY")
    print("=" * 60)
    
    total_agents = len(results)
    passed_agents = sum(results.values())
    
    for agent, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{agent:20} | {status}")
    
    print("-" * 60)
    print(f"Total Agents Tested: {total_agents}")
    print(f"Agents Passing: {passed_agents}")
    print(f"Success Rate: {(passed_agents/total_agents)*100:.1f}%")
    
    if passed_agents == total_agents:
        print("\n🎉 SUCCESS: ALL agents support dynamic API keys!")
        print("✅ No hardcoded credentials required")
        print("✅ Full compliance with HushhMCP best practices")
        print("✅ Secure and flexible credential management")
    else:
        print(f"\n⚠️ WARNING: {total_agents - passed_agents} agents still require hardcoded credentials")
        print("🔧 Additional refactoring needed for full compliance")
    
    print("=" * 60)

if __name__ == "__main__":
    run_comprehensive_dynamic_api_test()
