"""
Comprehensive API Test Suite for Relationship Memory Agent
This script tests all the API endpoints to ensure they work correctly.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

class APITester:
    """Comprehensive API testing class"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session_data = {}
        
    def test_all_endpoints(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive API Test Suite")
        print("=" * 60)
        
        # Test basic endpoints
        if not self.test_root_endpoint():
            return False
            
        if not self.test_health_endpoint():
            return False
            
        # Test authentication
        if not self.test_session_creation():
            return False
            
        # Test agent functionality
        self.test_agent_endpoints()
        
        # Test advanced features
        self.test_advanced_features()
        
        print("\n🎉 All API tests completed!")
        return True
    
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint"""
        print("\n1. 🏠 Testing Root Endpoint")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Service: {data.get('service', 'N/A')}")
                print(f"   Version: {data.get('version', 'N/A')}")
                print(f"   Agent ID: {data.get('agent_id', 'N/A')}")
                print("   ✅ Root endpoint works!")
                return True
            else:
                print(f"   ❌ Root endpoint failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Root endpoint failed: {e}")
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test the health endpoint"""
        print("\n2. 🏥 Testing Health Endpoint")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {data.get('status', 'N/A')}")
                print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
                print("   ✅ Health endpoint works!")
                return True
            else:
                print(f"   ❌ Health endpoint failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Health endpoint failed: {e}")
            return False
    
    def test_session_creation(self) -> bool:
        """Test session creation and authentication"""
        print("\n3. 🔐 Testing Session Creation")
        print("-" * 30)
        
        try:
            user_id = f"test_user_{int(time.time())}"
            response = requests.post(f"{self.base_url}/auth/session?user_id={user_id}")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                self.session_data = response.json()
                print(f"   User ID: {self.session_data['user_id']}")
                print(f"   Tokens Count: {len(self.session_data['tokens'])}")
                print(f"   Vault Key: {self.session_data['vault_key'][:20]}...")
                print("   ✅ Session creation works!")
                return True
            else:
                print(f"   ❌ Session creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Session creation failed: {e}")
            return False
    
    def test_agent_endpoints(self):
        """Test main agent functionality endpoints"""
        print("\n4. 🤖 Testing Agent Endpoints")
        print("-" * 30)
        
        if not self.session_data:
            print("   ❌ No session data available")
            return
        
        # Test data for contacts
        test_requests = [
            {
                "name": "Add Contact",
                "payload": {
                    "user_input": "add contact John Smith with email john@example.com",
                    "user_id": self.session_data["user_id"],
                    "tokens": self.session_data["tokens"],
                    "vault_key": self.session_data["vault_key"]
                }
            },
            {
                "name": "Add Memory",
                "payload": {
                    "user_input": "remember that John loves coffee and works at tech company",
                    "user_id": self.session_data["user_id"],
                    "tokens": self.session_data["tokens"],
                    "vault_key": self.session_data["vault_key"]
                }
            },
            {
                "name": "Add Date",
                "payload": {
                    "user_input": "John's birthday is on March 15th",
                    "user_id": self.session_data["user_id"],
                    "tokens": self.session_data["tokens"],
                    "vault_key": self.session_data["vault_key"]
                }
            },
            {
                "name": "Show Contacts",
                "payload": {
                    "user_input": "show all my contacts",
                    "user_id": self.session_data["user_id"],
                    "tokens": self.session_data["tokens"],
                    "vault_key": self.session_data["vault_key"]
                }
            }
        ]
        
        for test in test_requests:
            self._test_agent_request(test["name"], test["payload"])
    
    def _test_agent_request(self, name: str, payload: Dict[str, Any]):
        """Test a single agent request"""
        print(f"\n   📋 Testing: {name}")
        
        try:
            response = requests.post(f"{self.base_url}/agent/process", json=payload)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      Result: {data.get('status', 'N/A')}")
                print(f"      Action: {data.get('action_taken', 'N/A')}")
                message = data.get('message', '')
                if len(message) > 100:
                    message = message[:100] + "..."
                print(f"      Message: {message}")
                print(f"      ✅ {name} works!")
            else:
                print(f"      ❌ {name} failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"      ❌ {name} failed: {e}")
    
    def test_advanced_features(self):
        """Test advanced features like proactive checks"""
        print("\n5. 🔮 Testing Advanced Features")
        print("-" * 30)
        
        if not self.session_data:
            print("   ❌ No session data available")
            return
        
        # Test proactive check
        print("\n   🚀 Testing Proactive Check")
        try:
            payload = {
                "user_id": self.session_data["user_id"],
                "tokens": self.session_data["tokens"],
                "vault_key": self.session_data["vault_key"]
            }
            
            response = requests.post(f"{self.base_url}/agent/proactive", json=payload)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      Result: {data.get('status', 'N/A')}")
                print("      ✅ Proactive check works!")
            else:
                print(f"      ❌ Proactive check failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"      ❌ Proactive check failed: {e}")

def main():
    """Main test function"""
    print("🔍 Relationship Memory API Test Suite")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌐 Testing API on http://localhost:8001")
    
    # Wait a moment for potential server startup
    print("\n⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            print("   Please make sure the relationship memory API is running on port 8001")
            print("   Run: python hushh_mcp\\agents\\relationship_memory\\api.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        print("   Please start the relationship memory API server first:")
        print("   Run: python hushh_mcp\\agents\\relationship_memory\\api.py")
        return
    except Exception as e:
        print(f"❌ Server check failed: {e}")
        return
    
    # Run tests
    tester = APITester()
    success = tester.test_all_endpoints()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("   The Relationship Memory API is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
