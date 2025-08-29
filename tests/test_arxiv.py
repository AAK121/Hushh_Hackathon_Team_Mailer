import requests
import feedparser

def test_arxiv_search():
    try:
        query = "machine learning"
        base_url = "http://export.arxiv.org/api/query?"
        search_query = f"search_query=all:{query}"
        params = f"{search_query}&start=0&max_results=5&sortBy=relevance&sortOrder=descending"
        
        print(f"Making request to: {base_url}{params}")
        response = requests.get(f"{base_url}{params}", timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response length: {len(response.content)}")
        
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            print(f"Found {len(feed.entries)} entries")
            
            for i, entry in enumerate(feed.entries):
                print(f"Paper {i+1}: {entry.title[:50]}...")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_arxiv_search()
