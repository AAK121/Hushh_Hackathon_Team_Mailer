#!/usr/bin/env python3
"""
Research Agent Testing Script
============================

This script demonstrates how to interact with the Research Agent API
and provides examples of all available functionality.
"""

import json
import time
from pathlib import Path

# Note: Requires requests library
# Install with: C:\Python310\python.exe -m pip install requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  requests library not found. Install with: pip install requests")

API_BASE = "http://127.0.0.1:8001"
TEST_USER_ID = "demo_user_123"

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"🔬 {title}")
    print('='*60)

def print_result(success, message, data=None):
    """Print formatted test results."""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    if data and isinstance(data, dict):
        print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
    elif data:
        print(f"   Response: {str(data)[:200]}...")

def test_health():
    """Test API health endpoint."""
    print_section("Health Check")
    
    if not HAS_REQUESTS:
        print("❌ Cannot test - requests library missing")
        return False
        
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, "API is healthy and responding", data)
            return True
        else:
            print_result(False, f"Health check failed: HTTP {response.status_code}")
            return False
    except requests.ConnectionError:
        print_result(False, "Cannot connect to API server. Is it running?")
        return False
    except Exception as e:
        print_result(False, f"Health check error: {e}")
        return False

def test_agent_discovery():
    """Test agent discovery endpoint."""
    print_section("Agent Discovery")
    
    if not HAS_REQUESTS:
        print("❌ Cannot test - requests library missing")
        return False
        
    try:
        response = requests.get(f"{API_BASE}/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data.get("agents", {})
            
            if "agent_research" in agents:
                research_agent = agents["agent_research"]
                print_result(True, f"Research Agent found: {research_agent['name']} v{research_agent['version']}")
                print(f"   📝 Description: {research_agent['description']}")
                print(f"   🔗 Endpoints: {list(research_agent['endpoints'].keys())}")
                return True
            else:
                print_result(False, "Research Agent not found in agent list")
                return False
        else:
            print_result(False, f"Agent discovery failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Agent discovery error: {e}")
        return False

def test_research_status():
    """Test research agent status."""
    print_section("Research Agent Status")
    
    if not HAS_REQUESTS:
        print("❌ Cannot test - requests library missing")
        return False
        
    try:
        response = requests.get(f"{API_BASE}/agents/research/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Research Agent Status: {data['status']}")
            print(f"   🎯 Required Scopes: {', '.join(data['required_scopes'])}")
            print(f"   📊 Required Inputs: {', '.join(data['required_inputs'].keys())}")
            return True
        else:
            print_result(False, f"Status check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Status check error: {e}")
        return False

def demo_arxiv_search():
    """Demonstrate ArXiv search with mock tokens."""
    print_section("ArXiv Search Demo (Expected to Fail)")
    
    if not HAS_REQUESTS:
        print("❌ Cannot test - requests library missing")
        return False
    
    print("🔍 This test demonstrates the API structure but will fail due to mock tokens")
    print("   In a real frontend, you would get proper consent tokens first.")
    
    # Mock consent tokens (will fail validation)
    mock_tokens = {
        "custom.temporary": f"HCT:mock_temp_{TEST_USER_ID}_{int(time.time())}",
        "vault.read.file": f"HCT:mock_read_{TEST_USER_ID}_{int(time.time())}",
        "vault.write.file": f"HCT:mock_write_{TEST_USER_ID}_{int(time.time())}"
    }
    
    payload = {
        "user_id": TEST_USER_ID,
        "consent_tokens": mock_tokens,
        "query": "artificial intelligence applications in medical diagnosis"
    }
    
    try:
        print(f"   📤 Sending query: '{payload['query']}'")
        response = requests.post(
            f"{API_BASE}/agents/research/search/arxiv",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get("status") == "success":
            print_result(True, "ArXiv search succeeded!", data)
        else:
            # Expected failure due to consent validation
            errors = data.get("errors", []) if isinstance(data, dict) else ["Unknown error"]
            print_result(False, f"ArXiv search failed (expected): {', '.join(errors)}")
            print("   💡 This failure is expected when using mock consent tokens")
            
    except Exception as e:
        print_result(False, f"ArXiv search error: {e}")
        
    return False  # Expected to fail with mock tokens

def show_integration_example():
    """Show how to integrate with a real frontend."""
    print_section("Frontend Integration Example")
    
    print("""
🌐 Frontend Integration Steps:

1. **Get Consent Tokens** (implement proper consent flow):
   ```javascript
   const tokens = await getConsentTokens(userId, [
     'custom.temporary', 
     'vault.read.file', 
     'vault.write.file'
   ]);
   ```

2. **Search ArXiv**:
   ```javascript
   const searchResult = await fetch('/agents/research/search/arxiv', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({
       user_id: currentUser.id,
       consent_tokens: tokens,
       query: userQuery
     })
   });
   ```

3. **Upload PDF**:
   ```javascript
   const formData = new FormData();
   formData.append('file', pdfFile);
   formData.append('user_id', currentUser.id);
   formData.append('consent_tokens', JSON.stringify(tokens));
   
   const uploadResult = await fetch('/agents/research/upload', {
     method: 'POST',
     body: formData
   });
   ```

4. **Get Summary**:
   ```javascript
   const summary = await fetch(`/agents/research/paper/${paperId}/summary?user_id=${userId}&consent_tokens=${encodeURIComponent(JSON.stringify(tokens))}`);
   ```

5. **Process Snippets**:
   ```javascript
   const processed = await fetch(`/agents/research/paper/${paperId}/process/snippet`, {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({
       user_id: currentUser.id,
       consent_tokens: tokens,
       text: selectedText,
       instruction: "Explain this for a beginner"
     })
   });
   ```
""")

def main():
    """Run all tests and demos."""
    print("🔬 Research Agent Testing & Demo Script")
    print("This script tests the Research Agent backend and shows integration examples.")
    
    if not HAS_REQUESTS:
        print("\n⚠️  To run HTTP tests, install requests:")
        print("   C:\\Python310\\python.exe -m pip install requests")
        print("\nShowing integration examples only...\n")
        show_integration_example()
        return
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Agent Discovery", test_agent_discovery),
        ("Research Agent Status", test_research_status),
        ("ArXiv Search Demo", demo_arxiv_search)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    # Show integration examples
    show_integration_example()
    
    # Summary
    print_section("Test Summary")
    print(f"📊 Passed: {passed}/{len(tests)} tests")
    
    if passed >= 3:  # Health, discovery, status should pass
        print("🎉 Backend is working correctly!")
        print("   Ready for frontend integration.")
    else:
        print("⚠️  Some basic tests failed.")
        print("   Check if the API server is running: C:\\Python310\\python.exe api.py")

if __name__ == "__main__":
    main()
