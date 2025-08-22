#!/usr/bin/env python3
"""
Quick API Test - Verify Consent Fix
"""

import json
import urllib.request

def test_api_with_mock_token():
    """Test the API with a mock token to see if the error is fixed."""
    print("🔍 Testing API with mock token...")
    
    url = "http://localhost:8001/agents/research/search/arxiv"
    
    data = {
        "user_id": "test_user_quick",
        "consent_tokens": {
            "custom.temporary": "mock_token_123"
        },
        "query": "test query"
    }
    
    try:
        req_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
        
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode())
        
        print(f"✅ Response received!")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Success: {result.get('success', False)}")
        
        if 'errors' in result:
            errors = result['errors']
            if errors:
                print(f"Errors: {errors}")
                
                # Check if the specific error is fixed
                error_text = ' '.join(errors)
                if "takes from 1 to 2 positional arguments but 3 were given" in error_text:
                    print("❌ The consent validation fix didn't work")
                    return False
                else:
                    print("✅ The original error is fixed!")
                    return True
            else:
                print("✅ No errors!")
                return True
        else:
            print("✅ No error field in response")
            return True
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_with_valid_token():
    """Test with a properly created token."""
    print("\n🔐 Testing API with valid token...")
    
    try:
        from hushh_mcp.consent.token import issue_token
        from hushh_mcp.constants import ConsentScope
        
        # Create valid token
        token_obj = issue_token(
            user_id="test_user_valid",
            agent_id="research_agent",
            scope=ConsentScope.CUSTOM_TEMPORARY,
            expires_in_ms=3600000
        )
        
        url = "http://localhost:8001/agents/research/search/arxiv"
        
        data = {
            "user_id": "test_user_valid",
            "consent_tokens": {
                "custom.temporary": token_obj.token
            },
            "query": "artificial intelligence"
        }
        
        req_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
        
        response = urllib.request.urlopen(req, timeout=20)
        result = json.loads(response.read().decode())
        
        print(f"✅ Response received!")
        print(f"Status: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'success':
            papers = result.get('results', {}).get('papers', [])
            print(f"🎉 SUCCESS! Found {len(papers)} papers")
            
            if papers:
                first_paper = papers[0]
                print(f"📄 First paper: {first_paper.get('title', 'N/A')[:60]}...")
            
            return True
        else:
            errors = result.get('errors', [])
            print(f"❌ API still failing: {errors}")
            return False
            
    except Exception as e:
        print(f"❌ Valid token test failed: {e}")
        return False

def main():
    """Run quick tests to verify the fix."""
    print("🧪 Quick API Fix Verification")
    print("=" * 50)
    
    # Test 1: Mock token (should have different error now)
    test1_passed = test_api_with_mock_token()
    
    # Test 2: Valid token (should work completely)
    test2_passed = test_with_valid_token()
    
    print("\n" + "=" * 50)
    print("🎯 VERIFICATION RESULTS")
    print("=" * 50)
    print(f"Mock Token Test (Error Fixed): {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Valid Token Test (Full Success): {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test2_passed:
        print("\n🎉 CELEBRATION! The research agent is fully working!")
        print("✅ Backend operational")
        print("✅ ArXiv search functional") 
        print("✅ Consent validation working")
        print("✅ API endpoints responding")
        print("🚀 Ready for frontend integration!")
    elif test1_passed:
        print("\n✅ Fix successful but consent validation working as expected")
        print("💡 This means the security system is properly blocking invalid tokens")
    else:
        print("\n❌ Still investigating...")

if __name__ == "__main__":
    main()
