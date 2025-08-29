#!/usr/bin/env python3
"""
Quick Test - Check if research agent imports work now
"""

print("🔍 Testing Research Agent Import...")

try:
    from hushh_mcp.agents.research_agent.index import research_agent
    print("✅ Research agent imported successfully!")
    
    # Test if the agent has the required methods
    if hasattr(research_agent, '_search_arxiv'):
        print("✅ ArXiv search method found")
    else:
        print("❌ ArXiv search method missing")
        
    if hasattr(research_agent, 'search_arxiv'):
        print("✅ Public search method found")
    else:
        print("❌ Public search method missing")
        
    print("\n🔬 Testing Direct ArXiv Search...")
    
    # Test state for ArXiv search
    test_state = {
        "user_id": "test_user",
        "consent_tokens": {"custom.temporary": "mock"},
        "query": "test query",
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
    
    # Call the ArXiv search function directly
    result = research_agent._search_arxiv(test_state)
    
    if result.get("error"):
        print(f"❌ ArXiv search failed: {result['error']}")
    else:
        papers = result.get("arxiv_results", [])
        print(f"✅ ArXiv search successful! Found {len(papers)} papers")
        
        if papers:
            print(f"📄 First paper: {papers[0].get('title', 'N/A')[:60]}...")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Import test complete!")
