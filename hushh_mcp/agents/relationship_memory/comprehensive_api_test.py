"""
Comprehensive API Test Runner for the Proactive Relationship Manager
This script provides a complete test suite for the relationship memory API
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class APITestRunner:
    """Comprehensive test runner for the relationship memory API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.user_id = "comprehensive_test_user"
        self.test_results = {}
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results[test_name] = success
        
    def run_comprehensive_tests(self):
        """Run comprehensive API tests"""
        print("🚀 Comprehensive Relationship Manager API Testing")
        print("=" * 60)
        
        # Basic connectivity tests
        self._test_server_connectivity()
        
        # Authentication tests
        self._test_authentication()
        
        # Contact management tests
        self._test_contact_operations()
        
        # Memory management tests
        self._test_memory_operations()
        
        # Date management tests
        self._test_date_operations()
        
        # Reminder management tests
        self._test_reminder_operations()
        
        # Advanced features tests
        self._test_advanced_features()
        
        # Natural language processing tests
        self._test_natural_language()
        
        # Generate summary
        self._generate_test_summary()
    
    def _test_server_connectivity(self):
        """Test basic server connectivity"""
        print("\n🔌 Testing Server Connectivity...")
        
        try:
            # Test root endpoint
            response = self.session.get(f"{self.base_url}/")
            self.log_test("Root endpoint", response.status_code == 200, 
                         f"Status: {response.status_code}")
            
            # Test health check
            response = self.session.get(f"{self.base_url}/health")
            self.log_test("Health check", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Server connectivity", False, f"Error: {str(e)}")
    
    def _test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        
        try:
            # Test session creation
            response = self.session.post(f"{self.base_url}/auth/session?user_id={self.user_id}")
            self.log_test("Session creation", response.status_code == 200,
                         f"Status: {response.status_code}")
            
            if response.status_code == 200:
                session_data = response.json()
                self.log_test("Session data validity", 
                            'user_id' in session_data and 'tokens' in session_data,
                            "Contains required fields")
        except Exception as e:
            self.log_test("Authentication", False, f"Error: {str(e)}")
    
    def _test_contact_operations(self):
        """Test contact management operations"""
        print("\n👥 Testing Contact Management...")
        
        headers = {"Authorization": f"Bearer test_token_{self.user_id}"}
        
        # Test adding single contact
        try:
            contact_data = {
                "name": "Test Contact Alpha",
                "email": "alpha@test.com",
                "phone": "555-0001",
                "company": "Test Corp",
                "priority": "high"
            }
            
            response = self.session.post(f"{self.base_url}/contacts/add", 
                                       json=contact_data, headers=headers)
            self.log_test("Add single contact", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Add single contact", False, f"Error: {str(e)}")
        
        # Test batch contact addition
        try:
            batch_data = {
                "contacts": [
                    {"name": "Test Contact Beta", "email": "beta@test.com"},
                    {"name": "Test Contact Gamma", "email": "gamma@test.com", "phone": "555-0003"}
                ],
                "user_id": self.user_id
            }
            
            response = self.session.post(f"{self.base_url}/contacts/batch",
                                       json=batch_data, headers=headers)
            self.log_test("Batch contact addition", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Batch contact addition", False, f"Error: {str(e)}")
        
        # Test getting contacts
        try:
            response = self.session.get(f"{self.base_url}/contacts?user_id={self.user_id}",
                                      headers=headers)
            self.log_test("Get contacts", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Get contacts", False, f"Error: {str(e)}")
        
        # Test contact details
        try:
            response = self.session.get(f"{self.base_url}/contacts/Test Contact Alpha/details?user_id={self.user_id}",
                                      headers=headers)
            self.log_test("Get contact details", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Get contact details", False, f"Error: {str(e)}")
        
        # Test contact search
        try:
            response = self.session.get(f"{self.base_url}/search/contacts?query=Alpha&user_id={self.user_id}",
                                      headers=headers)
            self.log_test("Search contacts", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Search contacts", False, f"Error: {str(e)}")
    
    def _test_memory_operations(self):
        """Test memory management operations"""
        print("\n🧠 Testing Memory Management...")
        
        headers = {"Authorization": f"Bearer test_token_{self.user_id}"}
        
        # Test adding memory
        try:
            memory_data = {
                "contact_name": "Test Contact Alpha",
                "summary": "loves machine learning and coffee",
                "location": "Tech conference",
                "tags": ["ai", "coffee"],
                "user_id": self.user_id
            }
            
            response = self.session.post(f"{self.base_url}/memories/add",
                                       json=memory_data, headers=headers)
            self.log_test("Add memory", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Add memory", False, f"Error: {str(e)}")
        
        # Test getting memories
        try:
            response = self.session.get(f"{self.base_url}/memories?user_id={self.user_id}",
                                      headers=headers)
            self.log_test("Get all memories", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Get all memories", False, f"Error: {str(e)}")
        
        # Test getting memories for specific contact
        try:
            response = self.session.get(f"{self.base_url}/memories?user_id={self.user_id}&contact_name=Test Contact Alpha",
                                      headers=headers)
            self.log_test("Get contact memories", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Get contact memories", False, f"Error: {str(e)}")
    
    def _test_date_operations(self):
        """Test date management operations"""
        print("\n📅 Testing Date Management...")
        
        headers = {"Authorization": f"Bearer test_token_{self.user_id}"}
        
        # Test adding important date
        try:
            response = self.session.post(
                f"{self.base_url}/dates/add?contact_name=Test Contact Alpha&date_type=birthday&date_value=25-12&user_id={self.user_id}",
                headers=headers
            )
            self.log_test("Add important date", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Add important date", False, f"Error: {str(e)}")
        
        # Test getting upcoming dates
        try:
            response = self.session.get(f"{self.base_url}/dates/upcoming?user_id={self.user_id}",
                                      headers=headers)
            self.log_test("Get upcoming dates", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Get upcoming dates", False, f"Error: {str(e)}")
    
    def _test_reminder_operations(self):
        """Test reminder management operations"""
        print("\n⏰ Testing Reminder Management...")
        
        headers = {"Authorization": f"Bearer test_token_{self.user_id}"}
        
        # Test adding reminder
        try:
            reminder_data = {
                "contact_name": "Test Contact Alpha",
                "title": "follow up on ML discussion",
                "priority": "high",
                "description": "Discuss the new AI project proposal",
                "user_id": self.user_id
            }
            
            response = self.session.post(f"{self.base_url}/reminders/add",
                                       json=reminder_data, headers=headers)
            self.log_test("Add reminder", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Add reminder", False, f"Error: {str(e)}")
        
        # Test getting reminders
        try:
            response = self.session.get(f"{self.base_url}/reminders?user_id={self.user_id}",
                                      headers=headers)
            self.log_test("Get reminders", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Get reminders", False, f"Error: {str(e)}")
    
    def _test_advanced_features(self):
        """Test advanced features"""
        print("\n🚀 Testing Advanced Features...")
        
        headers = {"Authorization": f"Bearer test_token_{self.user_id}"}
        
        # Test proactive check
        try:
            proactive_data = {
                "user_id": self.user_id
            }
            
            response = self.session.post(f"{self.base_url}/agent/proactive-check",
                                       json=proactive_data, headers=headers)
            self.log_test("Proactive check", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Proactive check", False, f"Error: {str(e)}")
        
        # Test advice generation
        try:
            advice_data = {
                "contact_name": "Test Contact Alpha",
                "question": "what should I get them for their birthday?",
                "user_id": self.user_id
            }
            
            response = self.session.post(f"{self.base_url}/advice",
                                       json=advice_data, headers=headers)
            self.log_test("Get advice", response.status_code == 200,
                         f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Get advice", False, f"Error: {str(e)}")
    
    def _test_natural_language(self):
        """Test natural language processing"""
        print("\n🗣️ Testing Natural Language Processing...")
        
        headers = {"Authorization": f"Bearer test_token_{self.user_id}"}
        
        test_inputs = [
            "add Sarah Connor with email sarah@terminator.com",
            "remember that Sarah loves technology and motorcycles",
            "remind me to wish Sarah happy birthday",
            "show me all my contacts",
            "what should I talk to Sarah about?"
        ]
        
        for i, user_input in enumerate(test_inputs):
            try:
                data = {
                    "user_input": user_input,
                    "user_id": self.user_id
                }
                
                response = self.session.post(f"{self.base_url}/agent/process",
                                           json=data, headers=headers)
                self.log_test(f"NLP test {i+1}", response.status_code == 200,
                             f"'{user_input[:30]}...' -> Status: {response.status_code}")
                
            except Exception as e:
                self.log_test(f"NLP test {i+1}", False, f"Error: {str(e)}")
    
    def _generate_test_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(self.test_results.values())
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
        
        if success_rate >= 90:
            print("\n🎉 EXCELLENT! The API is working very well.")
        elif success_rate >= 70:
            print("\n✅ GOOD! Most features are working correctly.")
        elif success_rate >= 50:
            print("\n⚠️ MODERATE! Some issues need attention.")
        else:
            print("\n❌ POOR! Significant issues detected.")

def main():
    """Main function to run comprehensive API tests"""
    print("🎯 COMPREHENSIVE RELATIONSHIP MANAGER API TEST SUITE")
    print("=" * 70)
    print("📝 Prerequisites:")
    print("   1. API server running on http://localhost:8000")
    print("   2. All environment variables configured (.env file)")
    print("   3. Gemini API key available")
    print("\n💡 To start the API server:")
    print("   python hushh_mcp/agents/relationship_memory/api.py")
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ API server is running and healthy!")
            print("🚀 Starting comprehensive tests...\n")
            
            # Run the comprehensive test suite
            runner = APITestRunner()
            runner.run_comprehensive_tests()
            
        else:
            print(f"⚠️ API server responded with status {response.status_code}")
            print("Please check the server configuration.")
    except requests.exceptions.ConnectinError:
        print("❌ Cannot connect to API server at http://localhost:8000")
        print("Please start the server first.")
    except Exception as e:
        print(f"❌ Error checking server status: {str(e)}")
        print("Please ensure the API server is running properly.")

if __name__ == "__main__":
    main()
