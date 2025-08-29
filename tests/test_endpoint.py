import requests
import json

# Test the research search endpoint
url = "http://localhost:8001/research/search"
data = {
    "query": "machine learning",
    "user_id": "test_user"
}

try:
    print("Testing /research/search endpoint...")
    response = requests.post(url, json=data, timeout=20)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except requests.exceptions.Timeout:
    print("Request timed out!")
except Exception as e:
    print(f"Error: {e}")

# Also test the health endpoint
try:
    print("\nTesting /health endpoint...")
    health_response = requests.get("http://localhost:8001/health", timeout=5)
    print(f"Health Status: {health_response.status_code}")
    print(f"Health Response: {health_response.text}")
except Exception as e:
    print(f"Health Error: {e}")
