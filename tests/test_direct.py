import requests

# Test the direct arXiv endpoint
try:
    print("Testing direct arXiv endpoint...")
    response = requests.get("http://localhost:8001/test/arxiv", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
