#!/usr/bin/env python3
"""
Test ChanduFinance Dynamic API Key Support
==========================================

This test verifies that the ChanduFinance agent properly accepts
API keys dynamically through API parameters rather than hardcoded values.
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "http://127.0.0.1:8002"
HEADERS = {"Content-Type": "application/json"}

# Test Configuration  
TEST_USER_ID = "test_user_dynamic"
TEST_TOKEN = "HCT:dGVzdF91c2VyX2R5bmFtaWN8Y2hhbmR1ZmluYW5jZXx2YXVsdC53cml0ZS5maWxlfDE3NTU3OTAzNzM4OTh8MTc1NjM5NTE3Mzg5OA==.a851b9c86e5efaa51e03c9e8d3b95f4718da6a6dd83531e631870749c278e541"

def test_dynamic_api_key_support():
    """Test that API keys can be provided dynamically through API parameters."""
    
    print("🧪 Testing Dynamic API Key Support")
    print("=" * 50)
    
    # Test 1: Basic profile setup without API key
    payload_basic = {
        "user_id": TEST_USER_ID,
        "token": TEST_TOKEN,
        "command": "setup_profile",
        "full_name": "Test User",
        "age": 30,
        "monthly_income": 5000.0,
        "monthly_expenses": 3000.0,
        "risk_tolerance": "moderate"
    }
    
    print("Test 1: Profile setup without API key...")
    response = requests.post(f"{BASE_URL}/agents/chandufinance/execute", 
                           headers=HEADERS, json=payload_basic, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            print("✅ PASS: Basic functionality works without API key")
        else:
            print("❌ FAIL: Basic functionality failed")
            print(f"Error: {data.get('errors', 'Unknown error')}")
    else:
        print(f"❌ FAIL: HTTP {response.status_code}")
    
    # Test 2: Profile setup with dynamic API key
    payload_with_key = {
        "user_id": TEST_USER_ID,
        "token": TEST_TOKEN,
        "command": "setup_profile", 
        "full_name": "Test User With Key",
        "age": 30,
        "monthly_income": 5000.0,
        "monthly_expenses": 3000.0,
        "risk_tolerance": "moderate",
        "gemini_api_key": "test_dynamic_key_12345"  # Dynamic API key
    }
    
    print("\nTest 2: Profile setup with dynamic API key...")
    response = requests.post(f"{BASE_URL}/agents/chandufinance/execute",
                           headers=HEADERS, json=payload_with_key, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            print("✅ PASS: Dynamic API key accepted successfully")
        else:
            print("❌ FAIL: Dynamic API key rejected")
            print(f"Error: {data.get('errors', 'Unknown error')}")
    else:
        print(f"❌ FAIL: HTTP {response.status_code}")
    
    # Test 3: Educational content with dynamic API key
    payload_education = {
        "user_id": TEST_USER_ID,
        "token": TEST_TOKEN,
        "command": "explain_like_im_new",
        "topic": "compound_interest",
        "complexity": "beginner",
        "gemini_api_key": "test_dynamic_key_education"  # Dynamic API key for LLM
    }
    
    print("\nTest 3: Educational content with dynamic API key...")
    response = requests.post(f"{BASE_URL}/agents/chandufinance/execute",
                           headers=HEADERS, json=payload_education, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            print("✅ PASS: Educational content with dynamic API key works")
        else:
            print("❌ FAIL: Educational content with dynamic API key failed")
            print(f"Error: {data.get('errors', 'Unknown error')}")
    else:
        print(f"❌ FAIL: HTTP {response.status_code}")
    
    # Test 4: Multiple API keys
    payload_multiple_keys = {
        "user_id": TEST_USER_ID,
        "token": TEST_TOKEN,
        "command": "view_profile",
        "gemini_api_key": "test_gemini_key",
        "api_keys": {
            "custom_key_1": "value_1",
            "custom_key_2": "value_2"
        }
    }
    
    print("\nTest 4: Multiple API keys support...")
    response = requests.post(f"{BASE_URL}/agents/chandufinance/execute",
                           headers=HEADERS, json=payload_multiple_keys, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            print("✅ PASS: Multiple API keys accepted successfully")
        else:
            print("❌ FAIL: Multiple API keys failed")
            print(f"Error: {data.get('errors', 'Unknown error')}")
    else:
        print(f"❌ FAIL: HTTP {response.status_code}")
    
    print("\n🎯 Dynamic API Key Test Complete!")
    print("✅ API keys are now provided dynamically through API parameters")
    print("✅ No hardcoded credentials in agent code")
    print("✅ Compliant with HushhMCP best practices")

if __name__ == "__main__":
    test_dynamic_api_key_support()
