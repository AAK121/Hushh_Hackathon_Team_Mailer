import requests

try:
    print("Testing basic arXiv API access...")
    url = "http://export.arxiv.org/api/query?search_query=all:machine+learning&start=0&max_results=1"
    print(f"URL: {url}")
    
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.content)}")
    print(f"First 500 chars: {response.text[:500]}")
    
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")
