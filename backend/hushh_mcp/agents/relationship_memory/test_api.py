"""
Test script for the Proactive Relationship Manager API
Tests all endpoints with proper HushhMCP compliance
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from hushh_mcp.agents.relationship_memory.api import app

# Create test client
client = TestClient(app)

# Test authentication token
TEST_AUTH_TOKEN = "demo_user_test_token"
TEST_USER_ID = "test_user_api"

def get_auth_headers():
    """Get authentication headers for requests"""
    return {"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}


class TestAPIEndpoints:
    """Test all API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "Proactive Relationship Manager API" in data["name"]
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_create_session(self):
        """Test session creation"""
        response = client.post(f"/auth/session?user_id={TEST_USER_ID}", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == TEST_USER_ID
        assert "tokens" in data
        assert len(data["tokens"]) > 0
    
    def test_process_natural_language(self):
        """Test natural language processing"""
        request_data = {
            "user_input": "add contact John Smith with email john@example.com",
            "user_id": TEST_USER_ID,
            "is_startup": False
        }
        
        response = client.post("/agent/process", json=request_data, headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
    
    def test_add_single_contact(self):
        """Test adding a single contact"""
        request_data = {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "+1-555-0123",
            "company": "TechCorp",
            "priority": "high"
        }
        
        response = client.post("/contacts/add", json=request_data, headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
    
    def test_add_batch_contacts(self):
        """Test adding batch contacts"""
        request_data = {
            "contacts": [
                {"name": "Bob Wilson", "email": "bob@example.com", "priority": "medium"},
                {"name": "Carol Davis", "phone": "+1-555-0456", "company": "Design Studio"}
            ],
            "user_id": TEST_USER_ID
        }
        
        response = client.post("/contacts/batch", json=request_data, headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
    
    def test_get_contacts(self):
        """Test getting all contacts"""
        response = client.get(f"/contacts?user_id={TEST_USER_ID}", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
    
    def test_add_memory(self):
        """Test adding a memory"""
        request_data = {
            "contact_name": "Alice Johnson",
            "summary": "loves photography and rock climbing",
            "user_id": TEST_USER_ID,
            "location": "Coffee shop",
            "tags": ["photography", "climbing"]
        }
        
        response = client.post("/memories/add", json=request_data, headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
    
    def test_get_memories(self):
        """Test getting memories"""
        response = client.get(f"/memories?user_id={TEST_USER_ID}", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
    
    def test_add_reminder(self):
        """Test adding a reminder"""
        request_data = {
            "contact_name": "Alice Johnson",
            "title": "Follow up about project",
            "user_id": TEST_USER_ID,
            "date": "2024-03-20",
            "priority": "high"
        }
        
        response = client.post("/reminders/add", json=request_data, headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
    
    def test_get_advice(self):
        """Test getting conversational advice"""
        request_data = {
            "contact_name": "Alice Johnson",
            "question": "What should I get Alice for her birthday?",
            "user_id": TEST_USER_ID
        }
        
        response = client.post("/advice", json=request_data, headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
    
    def test_get_upcoming_dates(self):
        """Test getting upcoming dates"""
        response = client.get(f"/dates/upcoming?user_id={TEST_USER_ID}", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
    
    def test_proactive_check(self):
        """Test proactive check"""
        request_data = {"user_id": TEST_USER_ID}
        
        response = client.post("/agent/proactive-check", json=request_data, headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data


def run_manual_api_test():
    """Run manual API test with real requests"""
    print("🧪 MANUAL API TEST")
    print("=" * 50)
    
    from hushh_mcp.agents.relationship_memory.api_client_example import RelationshipManagerClient
    
    # Initialize client
    client = RelationshipManagerClient(auth_token=f"{TEST_USER_ID}_token")
    
    try:
        # Test health
        print("1. Testing health check...")
        health = client.health_check()
        print(f"   ✅ Health: {health.get('status')}")
        
        # Test natural language processing
        print("\n2. Testing natural language processing...")
        result = client.process_natural_language(
            user_input="add contact Sarah Chen with email sarah@startup.com",
            user_id=TEST_USER_ID
        )
        print(f"   ✅ NLP Result: {result.get('status')}")
        print(f"   Message: {result.get('message', '')[:100]}...")
        
        # Test batch contacts
        print("\n3. Testing batch contact addition...")
        batch_result = client.add_batch_contacts([
            {"name": "Mike Rodriguez", "email": "mike@design.com"},
            {"name": "Lisa Wang", "phone": "+1-555-0789"}
        ], TEST_USER_ID)
        print(f"   ✅ Batch Result: {batch_result.get('status')}")
        print(f"   Message: {batch_result.get('message', '')[:100]}...")
        
        # Test advice
        print("\n4. Testing advice generation...")
        advice_result = client.get_advice(
            contact_name="Sarah Chen",
            question="What should I get Sarah for her birthday?",
            user_id=TEST_USER_ID
        )
        print(f"   ✅ Advice Result: {advice_result.get('status')}")
        print(f"   Message: {advice_result.get('message', '')[:100]}...")
        
        print(f"\n✅ Manual API test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Manual test failed: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the Relationship Manager API")
    parser.add_argument("--manual", "-m", action="store_true", help="Run manual test")
    parser.add_argument("--pytest", "-p", action="store_true", help="Run pytest")
    
    args = parser.parse_args()
    
    if args.manual:
        run_manual_api_test()
    elif args.pytest:
        pytest.main([__file__, "-v"])
    else:
        print("🧪 Running both manual and pytest...")
        run_manual_api_test()
        print("\n" + "="*50)
        pytest.main([__file__, "-v"])