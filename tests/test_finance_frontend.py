#!/usr/bin/env python3
"""
Comprehensive test script for the Finance Frontend functionality
Tests all ChanduFinance API endpoints before frontend integration
"""

import requests
import json
import time
from typing import Dict, Any

class FinanceFrontendTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.user_id = "demo_user"
        self.token = None
        self.session = requests.Session()
        
    def log(self, message: str, status: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        
    def test_api_health(self) -> bool:
        """Test if the API server is running"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log("✅ API server is running", "SUCCESS")
                return True
            else:
                self.log(f"❌ API health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Cannot connect to API server: {e}", "ERROR")
            return False
            
    def create_token(self) -> bool:
        """Create a ChanduFinance token"""
        try:
            payload = {
                "user_id": self.user_id,
                "agent_id": "agent_chandufinance",
                "scope": "vault.read.finance"
            }
            response = self.session.post(f"{self.base_url}/consent/tokens", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                if self.token:
                    self.log("✅ Token created successfully", "SUCCESS")
                    return True
                else:
                    self.log("❌ Token not found in response", "ERROR")
                    return False
            else:
                self.log(f"❌ Token creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Token creation error: {e}", "ERROR")
            return False
            
    def test_profile_setup(self) -> bool:
        """Test user profile setup"""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.token,
                "command": "setup_profile",
                "full_name": "Demo User",
                "age": 30,
                "occupation": "Software Developer",
                "monthly_income": 5000,
                "monthly_expenses": 3200,
                "current_savings": 15000,
                "current_debt": 5000,
                "investment_budget": 1500,
                "risk_tolerance": "moderate",
                "investment_experience": "beginner"
            }
            
            response = self.session.post(f"{self.base_url}/agents/chandufinance/execute", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("✅ Profile setup successful", "SUCCESS")
                    if data.get("ai_insights"):
                        self.log(f"💡 AI Insights: {data['ai_insights'][:100]}...", "INFO")
                    return True
                else:
                    self.log(f"❌ Profile setup failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Profile setup request failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Profile setup error: {e}", "ERROR")
            return False
            
    def test_portfolio_creation(self) -> bool:
        """Test portfolio creation"""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.token,
                "portfolio_name": "Test Portfolio",
                "investment_amount": 10000,
                "risk_tolerance": "moderate",
                "investment_goals": ["retirement", "growth"],
                "time_horizon": 10
            }
            
            response = self.session.post(f"{self.base_url}/agents/chandufinance/portfolio/create", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("✅ Portfolio creation successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Portfolio creation failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Portfolio creation request failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Portfolio creation error: {e}", "ERROR")
            return False
            
    def test_cashflow_analysis(self) -> bool:
        """Test cashflow analysis"""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.token,
                "period_months": 12,
                "include_projections": True
            }
            
            response = self.session.post(f"{self.base_url}/agents/chandufinance/analytics/cashflow", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("✅ Cashflow analysis successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Cashflow analysis failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Cashflow analysis request failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Cashflow analysis error: {e}", "ERROR")
            return False
            
    def test_spending_analysis(self) -> bool:
        """Test spending analysis"""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.token,
                "transactions": [
                    {"amount": 1200, "description": "Rent", "category": "Housing", "date": "2025-01-01", "type": "expense"},
                    {"amount": 300, "description": "Groceries", "category": "Food", "date": "2025-01-05", "type": "expense"},
                    {"amount": 5000, "description": "Salary", "category": "Income", "date": "2025-01-01", "type": "income"}
                ],
                "analysis_type": "detailed"
            }
            
            response = self.session.post(f"{self.base_url}/agents/chandufinance/analytics/spending", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("✅ Spending analysis successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Spending analysis failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Spending analysis request failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Spending analysis error: {e}", "ERROR")
            return False
            
    def test_stock_prices(self) -> bool:
        """Test stock price fetching"""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.token,
                "symbols": ["AAPL", "GOOGL"],
                "include_analysis": True
            }
            
            response = self.session.post(f"{self.base_url}/agents/chandufinance/market/stock-price", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("✅ Stock prices fetching successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Stock prices failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Stock prices request failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Stock prices error: {e}", "ERROR")
            return False
            
    def test_retirement_planning(self) -> bool:
        """Test retirement planning"""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.token,
                "current_age": 30,
                "retirement_age": 65,
                "desired_retirement_income": 6000,
                "current_savings": 15000
            }
            
            response = self.session.post(f"{self.base_url}/agents/chandufinance/planning/retirement", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("✅ Retirement planning successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Retirement planning failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Retirement planning request failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Retirement planning error: {e}", "ERROR")
            return False
            
    def test_emergency_fund_planning(self) -> bool:
        """Test emergency fund planning"""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.token,
                "monthly_expenses": 3200,
                "current_emergency_savings": 5000,
                "income_stability": "stable"
            }
            
            response = self.session.post(f"{self.base_url}/agents/chandufinance/planning/emergency-fund", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("✅ Emergency fund planning successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Emergency fund planning failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Emergency fund planning request failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Emergency fund planning error: {e}", "ERROR")
            return False
            
    def test_tax_optimization(self) -> bool:
        """Test tax optimization"""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.token,
                "annual_income": 60000,
                "investment_income": 5000,
                "tax_year": 2024
            }
            
            response = self.session.post(f"{self.base_url}/agents/chandufinance/analytics/tax-optimization", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log("✅ Tax optimization successful", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Tax optimization failed: {data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Tax optimization request failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Tax optimization error: {e}", "ERROR")
            return False
            
    def run_all_tests(self):
        """Run all frontend functionality tests"""
        self.log("🚀 Starting Finance Frontend Functionality Tests", "START")
        self.log("=" * 60, "INFO")
        
        tests = [
            ("API Health Check", self.test_api_health),
            ("Token Creation", self.create_token),
            ("Profile Setup", self.test_profile_setup),
            ("Portfolio Creation", self.test_portfolio_creation),
            ("Cashflow Analysis", self.test_cashflow_analysis),
            ("Spending Analysis", self.test_spending_analysis),
            ("Stock Prices", self.test_stock_prices),
            ("Retirement Planning", self.test_retirement_planning),
            ("Emergency Fund Planning", self.test_emergency_fund_planning),
            ("Tax Optimization", self.test_tax_optimization)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n🧪 Testing: {test_name}", "TEST")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"❌ Test '{test_name}' crashed: {e}", "ERROR")
                failed += 1
                
        self.log("\n" + "=" * 60, "INFO")
        self.log(f"🎯 Test Results: {passed} passed, {failed} failed", "RESULT")
        
        if failed == 0:
            self.log("🎉 All tests passed! Frontend is ready to use.", "SUCCESS")
            return True
        else:
            self.log(f"⚠️  {failed} tests failed. Check the issues above.", "WARNING")
            return False

def main():
    tester = FinanceFrontendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎊 Finance Frontend is fully functional!")
        print("💡 You can now test the frontend interface:")
        print("   1. Open browser to http://localhost:3000")
        print("   2. Navigate to Finance Agent")
        print("   3. Try all the features (Portfolio, Analytics, Market Data, Planning)")
    else:
        print("\n⚠️  Some issues detected. Please check the API server and try again.")

if __name__ == "__main__":
    main()
