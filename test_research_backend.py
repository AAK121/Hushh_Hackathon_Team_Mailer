# test_research_backend.py

"""
Test script for Research Agent Backend
=====================================

This script tests the basic functionality of the research agent:
1. API server startup
2. Agent discovery
3. ArXiv search functionality
4. Basic error handling
"""

import requests
import json
import sys
from pathlib import Path

# Test configuration
BASE_URL = "http://127.0.0.1:8001"
TEST_USER_ID = "test_user_123"

def test_api_health():
    """Test if the API server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            return True
        else:
            print(f"❌ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except requests.ConnectionError:
        print("❌ API Health Check: FAILED (Connection Error - Server not running?)")
        return False

def test_agent_discovery():
    """Test agent discovery endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/agents")
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", {})
            if "agent_research" in agents:
                print("✅ Agent Discovery: PASSED")
                print(f"   Found Research Agent: {agents['agent_research']['name']}")
                return True
            else:
                print("❌ Agent Discovery: FAILED (Research agent not found)")
                return False
        else:
            print(f"❌ Agent Discovery: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Agent Discovery: FAILED (Error: {e})")
        return False

def test_research_agent_status():
    """Test research agent status endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/agents/research/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Research Agent Status: PASSED")
            print(f"   Agent: {data.get('name')} v{data.get('version')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Research Agent Status: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Research Agent Status: FAILED (Error: {e})")
        return False

def generate_test_tokens():
    """Generate test consent tokens."""
    try:
        # Request consent tokens for research agent
        token_request = {
            "user_id": TEST_USER_ID,
            "scopes": ["custom.temporary", "vault.read.file", "vault.write.file"],
            "duration_hours": 1
        }
        
        # For now, we'll create mock tokens since we don't have the full consent system
        # In a real implementation, these would be cryptographically signed
        mock_tokens = {
            "custom.temporary": f"HCT:mock_temp_token_{TEST_USER_ID}",
            "vault.read.file": f"HCT:mock_read_token_{TEST_USER_ID}",
            "vault.write.file": f"HCT:mock_write_token_{TEST_USER_ID}"
        }
        
        print("✅ Test Tokens Generated: PASSED")
        return mock_tokens
        
    except Exception as e:
        print(f"❌ Test Tokens Generation: FAILED (Error: {e})")
        return None

def test_arxiv_search():
    """Test arXiv search functionality."""
    try:
        tokens = generate_test_tokens()
        if not tokens:
            return False
        
        search_request = {
            "user_id": TEST_USER_ID,
            "consent_tokens": tokens,
            "query": "machine learning applications in healthcare"
        }
        
        print("🔍 Testing arXiv search with query: 'machine learning applications in healthcare'")
        
        # Note: This test might fail due to consent validation
        # but it will help us identify what needs to be fixed
        response = requests.post(
            f"{BASE_URL}/agents/research/search/arxiv",
            json=search_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                results = data.get("results", {})
                papers = results.get("papers", [])
                print(f"✅ ArXiv Search: PASSED")
                print(f"   Found {len(papers)} papers")
                if papers:
                    print(f"   First paper: {papers[0].get('title', 'N/A')[:80]}...")
                return True
            else:
                print(f"❌ ArXiv Search: FAILED (Status: {data.get('status')})")
                print(f"   Errors: {data.get('errors', [])}")
                return False
        else:
            print(f"❌ ArXiv Search: FAILED (HTTP Status: {response.status_code})")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ArXiv Search: FAILED (Error: {e})")
        return False

def main():
    """Run all tests."""
    print("🔬 Research Agent Backend Test Suite")
    print("=" * 50)
    
    tests = [
        ("API Health Check", test_api_health),
        ("Agent Discovery", test_agent_discovery), 
        ("Research Agent Status", test_research_agent_status),
        ("ArXiv Search", test_arxiv_search)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  Test '{test_name}' failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Research Agent backend is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
