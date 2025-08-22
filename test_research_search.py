import json
import urllib.request
import urllib.parse

# Test the research agent search endpoint
def test_research_search():
    url = "http://localhost:8001/agents/research/search/arxiv"
    
    data = {
        "user_id": "test_user_123",
        "consent_tokens": {
            "custom.temporary": "test_token_12345",
            "vault.read.file": "test_read_token",
            "vault.write.file": "test_write_token"
        },
        "query": "machine learning healthcare applications"
    }
    
    try:
        req_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
        
        print("🔍 Testing Research Agent ArXiv Search...")
        print(f"Query: {data['query']}")
        print("Making request...")
        
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode())
        
        print(f"✅ Response received!")
        print(f"Success: {result.get('success', False)}")
        print(f"Session ID: {result.get('session_id', 'N/A')}")
        
        if result.get('success'):
            papers = result.get('results', [])
            print(f"📄 Papers found: {len(papers)}")
            
            for i, paper in enumerate(papers[:3], 1):
                print(f"\n📄 Paper {i}:")
                print(f"   Title: {paper.get('title', 'N/A')[:100]}...")
                print(f"   Authors: {', '.join(paper.get('authors', [])[:2])}")
                print(f"   arXiv ID: {paper.get('id', 'N/A')}")
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ Search failed: {error}")
            
            # Show full response for debugging
            print(f"🔍 Full response: {json.dumps(result, indent=2)}")
            
            if 'consent' in error.lower():
                print("💡 This is expected - consent validation is working!")
            elif 'token' in error.lower():
                print("💡 This is a token validation issue - security working!")
            else:
                print("⚠️ This might be a different issue - investigating...")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_research_search()
