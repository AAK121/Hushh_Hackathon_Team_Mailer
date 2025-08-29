#!/usr/bin/env python3
"""
Comprehensive API Test Suite for ChanduFinance Agent
===================================================

Tests all endpoints and functionality of the ChanduFinance agent through the API.
Validates profile management, goal tracking, stock analysis, and educational features.
"""

import requests
import json
import time
from typing import Dict, Any
from datetime import datetime, timedelta

class ChanduFinanceAPITester:
    """Comprehensive test suite for ChanduFinance API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.user_id = "api_test_user_001"
        self.token = None
        self.test_results = []
        
    def create_test_token(self) -> str:
        """Create a demo token for testing"""
        # For testing, we'll use a demo token
        # In production, this would come from proper consent flow
        return "demo_token_chandufinance_comprehensive_test"
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        timestamp = datetime.now().isoformat()
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': timestamp
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    def make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request and handle response"""
        url = f"{self.base_url}/agents/chandufinance/{endpoint}"
        
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "error"}
    
    def test_agent_status(self):
        """Test agent status endpoint"""
        try:
            url = f"{self.base_url}/agents/chandufinance/status"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            success = (
                data.get("agent_id") == "agent_chandufinance" and
                data.get("status") == "available" and
                "setup_profile" in data.get("supported_commands", [])
            )
            
            self.log_test(
                "Agent Status", 
                success,
                f"Agent available: {data.get('status')}, Commands: {len(data.get('supported_commands', []))}"
            )
            
        except Exception as e:
            self.log_test("Agent Status", False, f"Error: {str(e)}")
    
    def test_profile_setup(self):
        """Test comprehensive profile setup"""
        data = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "setup_profile",
            "full_name": "API Test User",
            "age": 28,
            "occupation": "Software Engineer",
            "monthly_income": 6000.0,
            "monthly_expenses": 4200.0,
            "current_savings": 15000.0,
            "current_debt": 5000.0,
            "investment_budget": 1500.0,
            "risk_tolerance": "moderate",
            "investment_experience": "intermediate"
        }
        
        response = self.make_request("execute", data)
        
        success = (
            response.get("status") == "success" and
            response.get("profile_summary") is not None and
            response.get("vault_stored") == True
        )
        
        details = f"Profile created, Health Score: {response.get('profile_health_score', {}).get('percentage', 'N/A')}"
        self.log_test("Profile Setup", success, details)
        
        return response
    
    def test_profile_view(self):
        """Test profile viewing"""
        data = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "view_profile"
        }
        
        response = self.make_request("execute", data)
        
        success = (
            response.get("status") == "success" and
            response.get("personal_info") is not None and
            response.get("financial_info") is not None
        )
        
        health_score = response.get('profile_health_score', {})
        details = f"Profile loaded, Score: {health_score.get('percentage', 'N/A')}, Rating: {health_score.get('health_rating', 'N/A')}"
        self.log_test("Profile View", success, details)
        
        return response
    
    def test_income_update(self):
        """Test income update"""
        data = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "update_income",
            "monthly_income": 7000.0
        }
        
        response = self.make_request("execute", data)
        
        success = response.get("status") == "success"
        details = f"Income updated: {response.get('message', 'No message')}"
        self.log_test("Income Update", success, details)
        
        return response
    
    def test_goal_management(self):
        """Test goal addition and tracking"""
        # Add a goal
        data = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "add_goal",
            "goal_name": "Emergency Fund",
            "target_amount": 25000.0,
            "target_date": "2026-12-31",
            "priority": "high"
        }
        
        response = self.make_request("execute", data)
        
        success = (
            response.get("status") == "success" and
            response.get("goal_details") is not None
        )
        
        goal_details = response.get('goal_details', {})
        details = f"Goal added: {goal_details.get('name', 'N/A')}, Target: ${goal_details.get('target_amount', 0):,.2f}"
        self.log_test("Goal Addition", success, details)
        
        # Check goal progress
        progress_data = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "goal_progress_check"
        }
        
        progress_response = self.make_request("execute", progress_data)
        progress_success = progress_response.get("status") == "success"
        
        self.log_test("Goal Progress Check", progress_success, "Goal progress retrieved")
        
        return response
    
    def test_stock_analysis(self):
        """Test stock analysis functionality"""
        data = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "personal_stock_analysis",
            "ticker": "AAPL"
        }
        
        response = self.make_request("execute", data)
        
        success = (
            response.get("status") == "success" and
            response.get("ticker") == "AAPL"
        )
        
        analysis = response.get('personalized_analysis', '')
        details = f"Stock analysis for {response.get('ticker', 'N/A')}, Analysis length: {len(analysis)} chars"
        self.log_test("Stock Analysis", success, details)
        
        return response
    
    def test_educational_content(self):
        """Test educational content generation"""
        data = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "explain_like_im_new",
            "topic": "dividend investing",
            "complexity": "beginner"
        }
        
        response = self.make_request("execute", data)
        
        success = (
            response.get("status") == "success" and
            response.get("explanation") is not None
        )
        
        explanation = response.get('explanation', '')
        details = f"Educational content generated, Length: {len(explanation)} chars"
        self.log_test("Educational Content", success, details)
        
        return response
    
    def test_behavioral_coaching(self):
        """Test behavioral coaching functionality"""
        data = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "behavioral_coaching",
            "topic": "emotional investing"
        }
        
        response = self.make_request("execute", data)
        
        success = (
            response.get("status") == "success" and
            response.get("coaching_advice") is not None
        )
        
        coaching = response.get('coaching_advice', '')
        details = f"Coaching advice generated, Length: {len(coaching)} chars"
        self.log_test("Behavioral Coaching", success, details)
        
        return response
    
    def test_portfolio_review(self):
        """Test portfolio review functionality"""
        data = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "portfolio_review"
        }
        
        response = self.make_request("execute", data)
        
        success = response.get("status") == "success"
        details = f"Portfolio review completed: {response.get('message', 'No message')}"
        self.log_test("Portfolio Review", success, details)
        
        return response
    
    def test_error_handling(self):
        """Test error handling with invalid requests"""
        # Test missing required fields
        data = {
            "user_id": self.user_id,
            "token": self.token,
            "command": "invalid_command"
        }
        
        response = self.make_request("execute", data)
        
        success = response.get("status") == "error"
        details = f"Error handling works: {response.get('errors', ['No error message'])[0]}"
        self.log_test("Error Handling", success, details)
        
        return response
    
    def run_comprehensive_test(self):
        """Run the complete test suite"""
        print("🚀 Starting ChanduFinance API Comprehensive Test Suite")
        print("=" * 70)
        
        # Setup
        self.token = self.create_test_token()
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_agent_status,
            self.test_profile_setup,
            self.test_profile_view,
            self.test_income_update,
            self.test_goal_management,
            self.test_stock_analysis,
            self.test_educational_content,
            self.test_behavioral_coaching,
            self.test_portfolio_review,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                test_name = test.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        # Summary
        total_time = time.time() - start_time
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print("\\n" + "=" * 70)
        print(f"🎯 TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"⏱️ Total Time: {total_time:.2f} seconds")
        print(f"🎉 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\\n🏆 ALL TESTS PASSED! ChanduFinance API is fully functional!")
        else:
            print("\\n⚠️ Some tests failed. Check the details above.")
        
        return self.test_results

def main():
    """Main function to run the test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test ChanduFinance API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()
    
    tester = ChanduFinanceAPITester(args.url)
    results = tester.run_comprehensive_test()
    
    # Save results to file
    with open('chandufinance_api_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\\n📄 Test results saved to: chandufinance_api_test_results.json")

if __name__ == "__main__":
    main()
