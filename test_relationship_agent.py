import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Example consent tokens (you would get these from your HushMCP system)
CONSENT_TOKENS = {
    "VAULT_WRITE_MEMORY": "your_consent_token",
    "VAULT_READ_CONTACT": "your_consent_token"
}

def test_add_memory():
    """Test adding a new memory"""
    url = f"{BASE_URL}/relationship/add-memory"
    
    data = {
        "contact_id": 1,
        "summary": "Initial meeting",
        "detailed_notes": "Had a productive first meeting discussing project requirements",
        "tags": ["meeting", "project", "initial"]
    }
    
    headers = {
        "Content-Type": "application/json",
        "user_id": "test_user_1",
        "consent_tokens": json.dumps(CONSENT_TOKENS)
    }
    
    response = requests.post(url, json=data, headers=headers)
    print("Add Memory Response:", response.json())

def test_get_contact_history():
    """Test retrieving contact history"""
    url = f"{BASE_URL}/relationship/contact-history/1"
    
    headers = {
        "user_id": "test_user_1",
        "consent_tokens": json.dumps(CONSENT_TOKENS)
    }
    
    response = requests.get(url, headers=headers)
    print("Contact History Response:", response.json())

if __name__ == "__main__":
    print("Testing Relationship Memory Agent API...")
    test_add_memory()
    test_get_contact_history()
