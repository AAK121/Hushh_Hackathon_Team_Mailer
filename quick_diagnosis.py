#!/usr/bin/env python3
"""
Quick Research Agent Diagnosis
=============================
"""

print("🔍 Diagnosing Research Agent Issue...")
print("=" * 50)

# Test 1: Check if modules import correctly
print("\n1️⃣ Testing Module Imports...")
try:
    from hushh_mcp.agents.research_agent.index import research_agent
    print("✅ Research agent imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: Check consent token creation
print("\n2️⃣ Testing Consent Token Creation...")
try:
    from hushh_mcp.consent.token import issue_token, validate_token
    from hushh_mcp.constants import ConsentScope
    
    # Create a proper token
    token_obj = issue_token(
        user_id="test_user",
        agent_id="research_agent", 
        scope=ConsentScope.CUSTOM_TEMPORARY,
        expires_in_ms=3600000
    )
    
    print(f"✅ Token created: {token_obj.token[:30]}...")
    
    # Test validation
    is_valid, error_msg, parsed_token = validate_token(
        token_obj.token, 
        ConsentScope.CUSTOM_TEMPORARY
    )
    
    print(f"✅ Token validation: {is_valid}")
    if not is_valid:
        print(f"❌ Validation error: {error_msg}")
    
except Exception as e:
    print(f"❌ Token test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test ArXiv search directly
print("\n3️⃣ Testing ArXiv Search Function Directly...")
try:
    # Create test state
    test_state = {
        "user_id": "test_user",
        "consent_tokens": {"custom.temporary": "mock"},
        "query": "machine learning",
        "status": "arxiv_search",
        "mode": "api",
        "session_id": "test123",
        "paper_id": None,
        "paper_content": None,
        "arxiv_results": None,
        "summary": None,
        "snippet": None,
        "instruction": None,
        "processed_snippet": None,
        "notes": None,
        "error": None
    }
    
    print("🔍 Calling ArXiv search function...")
    result = research_agent._search_arxiv(test_state)
    
    if result.get("error"):
        print(f"❌ ArXiv search error: {result['error']}")
    else:
        papers = result.get("arxiv_results", [])
        print(f"✅ ArXiv search successful! Found {len(papers)} papers")
        
        if papers:
            first_paper = papers[0]
            print(f"📄 First paper: {first_paper.get('title', 'N/A')[:60]}...")
    
except Exception as e:
    print(f"❌ ArXiv test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test the full API call with proper token
print("\n4️⃣ Testing Full API Call...")
try:
    import requests
    
    # Create valid token
    valid_token = issue_token(
        user_id="test_user_api",
        agent_id="research_agent",
        scope=ConsentScope.CUSTOM_TEMPORARY,
        expires_in_ms=3600000
    ).token
    
    url = "http://localhost:8001/agents/research/search/arxiv"
    data = {
        "user_id": "test_user_api",
        "consent_tokens": {
            "custom.temporary": valid_token
        },
        "query": "artificial intelligence"
    }
    
    print("📤 Making API request with valid token...")
    response = requests.post(url, json=data, timeout=30)
    
    print(f"📊 Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ API call successful!")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success'):
            papers = result.get('results', [])
            print(f"📄 Papers found: {len(papers)}")
        else:
            print(f"❌ API error: {result.get('error', 'Unknown')}")
    else:
        print(f"❌ HTTP error: {response.text}")

except ImportError:
    print("⚠️ requests not available, skipping API test")
    print("Run: pip install requests")
except Exception as e:
    print(f"❌ API test failed: {e}")

print("\n" + "=" * 50)
print("🎯 Diagnosis Complete!")
print("Check the results above to see what's working and what's not.")
