#!/usr/bin/env python3
"""
Comprehensive ChanduFinance API Test Suite
=========================================

This script tests all ChanduFinance API endpoints and functionality
to ensure proper integration and response handling.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# API Configuration
BASE_URL = "http://127.0.0.1:8002"
HEADERS = {"Content-Type": "application/json"}

# Test Configuration
TEST_USER_ID = "test_user_123"
TEST_TOKEN = "HCT:dGVzdF91c2VyXzEyM3xjaGFuZHVmaW5hbmNlfHZhdWx0LndyaXRlLmZpbGV8MTc1NTcwMjYyMDE4MXwxNzU1Nzg5MDIwMTgx.93d1fe656f91c9b68ffbad2cca518b1f30c90f1ed3f8c062a0e38edf5a6f8eb3"

class ChanduFinanceAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.user_id = TEST_USER_ID
        self.token = TEST_TOKEN
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, response: Dict[str, Any] = None, error: str = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response": response,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if error:
            print(f"      Error: {error}")
        if response and not success:
            print(f"      Response: {json.dumps(response, indent=2)}")
        print()

    def test_server_health(self):
        """Test basic server connectivity and health"""
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Server Health Check", True, data)
                return True
            else:
                self.log_test("Server Health Check", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Server Health Check", False, error=str(e))
            return False

    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Root Endpoint", True, data)
                return True
            else:
                self.log_test("Root Endpoint", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, error=str(e))
            return False

    def test_chandufinance_status(self):
        """Test ChanduFinance agent status endpoint"""
        try:
            response = requests.get(f"{self.base_url}/agents/chandufinance/status", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("ChanduFinance Status", True, data)
                return True
            else:
                self.log_test("ChanduFinance Status", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("ChanduFinance Status", False, error=str(e))
            return False

    def test_setup_profile(self):
        """Test profile setup functionality"""
        payload = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "setup_profile",
            "full_name": "John Smith",
            "age": 28,
            "occupation": "Software Engineer",
            "monthly_income": 6000.0,
            "monthly_expenses": 4000.0,
            "current_savings": 15000.0,
            "current_debt": 5000.0,
            "investment_budget": 1500.0,
            "risk_tolerance": "moderate",
            "investment_experience": "beginner"
        }
        
        try:
            response = requests.post(f"{self.base_url}/agents/chandufinance/execute", 
                                   headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Setup Profile", True, data)
                    return True
                else:
                    self.log_test("Setup Profile", False, data, error="API returned error status")
                    return False
            else:
                self.log_test("Setup Profile", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Setup Profile", False, error=str(e))
            return False

    def test_view_profile(self):
        """Test profile viewing functionality"""
        payload = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "view_profile"
        }
        
        try:
            response = requests.post(f"{self.base_url}/agents/chandufinance/execute", 
                                   headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("View Profile", True, data)
                    return True
                else:
                    self.log_test("View Profile", False, data, error="API returned error status")
                    return False
            else:
                self.log_test("View Profile", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("View Profile", False, error=str(e))
            return False

    def test_update_income(self):
        """Test income update functionality"""
        payload = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "update_income",
            "monthly_income": 6500.0
        }
        
        try:
            response = requests.post(f"{self.base_url}/agents/chandufinance/execute", 
                                   headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Update Income", True, data)
                    return True
                else:
                    self.log_test("Update Income", False, data, error="API returned error status")
                    return False
            else:
                self.log_test("Update Income", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Update Income", False, error=str(e))
            return False

    def test_add_goal(self):
        """Test goal addition functionality"""
        target_date = (datetime.now() + timedelta(days=365*2)).strftime("%Y-%m-%d")
        payload = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "add_goal",
            "goal_name": "Emergency Fund",
            "target_amount": 20000.0,
            "target_date": target_date,
            "priority": "high"
        }
        
        try:
            response = requests.post(f"{self.base_url}/agents/chandufinance/execute", 
                                   headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Add Goal", True, data)
                    return True
                else:
                    self.log_test("Add Goal", False, data, error="API returned error status")
                    return False
            else:
                self.log_test("Add Goal", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Add Goal", False, error=str(e))
            return False

    def test_stock_analysis(self):
        """Test personalized stock analysis"""
        payload = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "personal_stock_analysis",
            "ticker": "AAPL"
        }
        
        try:
            response = requests.post(f"{self.base_url}/agents/chandufinance/execute", 
                                   headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Stock Analysis", True, data)
                    return True
                else:
                    self.log_test("Stock Analysis", False, data, error="API returned error status")
                    return False
            else:
                self.log_test("Stock Analysis", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Stock Analysis", False, error=str(e))
            return False

    def test_investment_education(self):
        """Test investment education functionality"""
        payload = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "investment_education",
            "topic": "diversification",
            "complexity": "beginner"
        }
        
        try:
            response = requests.post(f"{self.base_url}/agents/chandufinance/execute", 
                                   headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Investment Education", True, data)
                    return True
                else:
                    self.log_test("Investment Education", False, data, error="API returned error status")
                    return False
            else:
                self.log_test("Investment Education", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Investment Education", False, error=str(e))
            return False

    def test_behavioral_coaching(self):
        """Test behavioral coaching functionality"""
        payload = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "behavioral_coaching",
            "topic": "fear_of_missing_out"
        }
        
        try:
            response = requests.post(f"{self.base_url}/agents/chandufinance/execute", 
                                   headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Behavioral Coaching", True, data)
                    return True
                else:
                    self.log_test("Behavioral Coaching", False, data, error="API returned error status")
                    return False
            else:
                self.log_test("Behavioral Coaching", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Behavioral Coaching", False, error=str(e))
            return False

    def test_explain_like_im_new(self):
        """Test beginner explanation functionality"""
        payload = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "explain_like_im_new",
            "topic": "compound_interest",
            "complexity": "beginner"
        }
        
        try:
            response = requests.post(f"{self.base_url}/agents/chandufinance/execute", 
                                   headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("Explain Like I'm New", True, data)
                    return True
                else:
                    self.log_test("Explain Like I'm New", False, data, error="API returned error status")
                    return False
            else:
                self.log_test("Explain Like I'm New", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Explain Like I'm New", False, error=str(e))
            return False

    def test_invalid_token(self):
        """Test error handling with invalid token"""
        payload = {
            "user_id": self.user_id,
            "token": "INVALID_TOKEN",
            "command": "view_profile"
        }
        
        try:
            response = requests.post(f"{self.base_url}/agents/chandufinance/execute", 
                                   headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "error":
                    self.log_test("Invalid Token Handling", True, data)
                    return True
                else:
                    self.log_test("Invalid Token Handling", False, data, error="Should have returned error")
                    return False
            else:
                self.log_test("Invalid Token Handling", False, error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Invalid Token Handling", False, error=str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive ChanduFinance API Test Suite")
        print("=" * 60)
        print()
        
        # Wait for server to be ready
        print("⏳ Waiting for server to be ready...")
        time.sleep(3)
        print()
        
        tests = [
            self.test_server_health,
            self.test_root_endpoint,
            self.test_chandufinance_status,
            self.test_setup_profile,
            self.test_view_profile,
            self.test_update_income,
            self.test_add_goal,
            self.test_stock_analysis,
            self.test_investment_education,
            self.test_behavioral_coaching,
            self.test_explain_like_im_new,
            self.test_invalid_token
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ FAIL | {test.__name__} - Exception: {str(e)}")
        
        print("=" * 60)
        print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! API is fully functional.")
        elif passed > total * 0.7:
            print("⚠️  Most tests passed, but some issues need attention.")
        else:
            print("🚨 CRITICAL: Multiple test failures. API needs fixes.")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if not result["success"] and result["error"]:
                print(f"   Error: {result['error']}")
        
        return passed, total

def main():
    """Main test execution"""
    tester = ChanduFinanceAPITester()
    passed, total = tester.run_all_tests()
    
    # Save detailed results to file
    with open("api_test_results.json", "w") as f:
        json.dump(tester.test_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: api_test_results.json")
    
    # Return appropriate exit code
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
