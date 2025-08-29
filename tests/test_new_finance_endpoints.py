#!/usr/bin/env python3
"""
Comprehensive Test Suite for New ChanduFinance Agent API Endpoints
================================================================

This test suite validates all the new finance agent endpoints including:
- Portfolio Management (create, analyze, rebalance)
- Financial Analytics (cashflow, spending, tax optimization)
- Market Data (stock prices, portfolio valuation)
- Advanced Planning (retirement, emergency fund)
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8001"
TEST_USER_ID = "test_user_finance_enhanced"
GEMINI_API_KEY = "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI"  # Demo key

class FinanceEndpointTester:
    """Comprehensive tester for the new finance endpoints."""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.user_id = TEST_USER_ID
        self.test_results = []
        self.consent_token = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Dict = None):
        """Log test results."""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if not success and response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()
    
    def create_consent_token(self) -> str:
        """Create a consent token for testing."""
        try:
            response = requests.post(f"{self.base_url}/consent/tokens", json={
                "user_id": self.user_id,
                "agent_id": "agent_chandufinance",
                "scope": "vault.read.finance"
            })
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                self.log_test("Create Consent Token", True, f"Token created: {token[:20]}...")
                return token
            else:
                self.log_test("Create Consent Token", False, f"Failed: {response.status_code}", response.json())
                return "test_token_" + str(int(time.time()))
                
        except Exception as e:
            self.log_test("Create Consent Token", False, f"Exception: {str(e)}")
            return "test_token_" + str(int(time.time()))

    # ====================================================================
    # PORTFOLIO MANAGEMENT TESTS
    # ====================================================================
    
    def test_portfolio_creation(self):
        """Test portfolio creation endpoint."""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.consent_token,
                "portfolio_name": "Test Growth Portfolio",
                "investment_amount": 10000.0,
                "risk_tolerance": "moderate",
                "investment_goals": ["growth", "retirement"],
                "time_horizon": 10,
                "gemini_api_key": GEMINI_API_KEY
            }
            
            response = requests.post(f"{self.base_url}/agents/chandufinance/portfolio/create", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    portfolio_id = data.get('data', {}).get('portfolio_id')
                    self.log_test("Portfolio Creation", True, f"Portfolio created: {portfolio_id}", data)
                    return portfolio_id
                else:
                    self.log_test("Portfolio Creation", False, "Success status not returned", data)
                    return None
            else:
                self.log_test("Portfolio Creation", False, f"HTTP {response.status_code}", response.json())
                return None
                
        except Exception as e:
            self.log_test("Portfolio Creation", False, f"Exception: {str(e)}")
            return None
    
    def test_portfolio_analysis(self, portfolio_id: str = None):
        """Test portfolio analysis endpoint."""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.consent_token,
                "portfolio_id": portfolio_id or "test_portfolio_123",
                "holdings": [
                    {"symbol": "AAPL", "shares": 10, "price": 150.0},
                    {"symbol": "GOOGL", "shares": 5, "price": 2500.0}
                ],
                "gemini_api_key": GEMINI_API_KEY
            }
            
            response = requests.post(f"{self.base_url}/agents/chandufinance/portfolio/analyze", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    metrics = data.get('data', {}).get('performance_metrics', {})
                    self.log_test("Portfolio Analysis", True, f"Analysis completed with metrics: {len(metrics)} items", data)
                else:
                    self.log_test("Portfolio Analysis", False, "Success status not returned", data)
            else:
                self.log_test("Portfolio Analysis", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Portfolio Analysis", False, f"Exception: {str(e)}")
    
    def test_portfolio_rebalance(self, portfolio_id: str = None):
        """Test portfolio rebalancing endpoint."""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.consent_token,
                "portfolio_id": portfolio_id or "test_portfolio_123",
                "gemini_api_key": GEMINI_API_KEY
            }
            
            response = requests.post(f"{self.base_url}/agents/chandufinance/portfolio/rebalance", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    trades = data.get('data', {}).get('rebalance_trades', [])
                    self.log_test("Portfolio Rebalance", True, f"Rebalance suggestions: {len(trades)} trades", data)
                else:
                    self.log_test("Portfolio Rebalance", False, "Success status not returned", data)
            else:
                self.log_test("Portfolio Rebalance", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Portfolio Rebalance", False, f"Exception: {str(e)}")

    # ====================================================================
    # ANALYTICS TESTS
    # ====================================================================
    
    def test_cashflow_analysis(self):
        """Test cash flow analysis endpoint."""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.consent_token,
                "period_months": 12,
                "include_projections": True,
                "gemini_api_key": GEMINI_API_KEY
            }
            
            response = requests.post(f"{self.base_url}/agents/chandufinance/analytics/cashflow", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    analysis = data.get('data', {}).get('monthly_analysis', {})
                    self.log_test("Cashflow Analysis", True, f"Analysis completed for {len(analysis)} periods", data)
                else:
                    self.log_test("Cashflow Analysis", False, "Success status not returned", data)
            else:
                self.log_test("Cashflow Analysis", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Cashflow Analysis", False, f"Exception: {str(e)}")
    
    def test_spending_analysis(self):
        """Test spending pattern analysis endpoint."""
        try:
            sample_transactions = [
                {"amount": 50.0, "category": "groceries", "date": "2024-01-15", "description": "Supermarket"},
                {"amount": 1200.0, "category": "rent", "date": "2024-01-01", "description": "Monthly rent"},
                {"amount": 75.0, "category": "dining", "date": "2024-01-10", "description": "Restaurant"}
            ]
            
            payload = {
                "user_id": self.user_id,
                "token": self.consent_token,
                "transactions": sample_transactions,
                "analysis_type": "detailed",
                "gemini_api_key": GEMINI_API_KEY
            }
            
            response = requests.post(f"{self.base_url}/agents/chandufinance/analytics/spending", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    categories = data.get('data', {}).get('category_breakdown', {})
                    self.log_test("Spending Analysis", True, f"Analysis completed for {len(categories)} categories", data)
                else:
                    self.log_test("Spending Analysis", False, "Success status not returned", data)
            else:
                self.log_test("Spending Analysis", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Spending Analysis", False, f"Exception: {str(e)}")
    
    def test_tax_optimization(self):
        """Test tax optimization analysis endpoint."""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.consent_token,
                "annual_income": 75000.0,
                "investment_income": 5000.0,
                "tax_year": 2024,
                "gemini_api_key": GEMINI_API_KEY
            }
            
            response = requests.post(f"{self.base_url}/agents/chandufinance/analytics/tax-optimization", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    strategies = data.get('data', {}).get('optimization_strategies', [])
                    self.log_test("Tax Optimization", True, f"Analysis completed with {len(strategies)} strategies", data)
                else:
                    self.log_test("Tax Optimization", False, "Success status not returned", data)
            else:
                self.log_test("Tax Optimization", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Tax Optimization", False, f"Exception: {str(e)}")

    # ====================================================================
    # MARKET DATA TESTS
    # ====================================================================
    
    def test_stock_prices(self):
        """Test stock price lookup endpoint."""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.consent_token,
                "symbols": ["AAPL", "GOOGL", "MSFT"],
                "include_analysis": True,
                "gemini_api_key": GEMINI_API_KEY
            }
            
            response = requests.post(f"{self.base_url}/agents/chandufinance/market/stock-price", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    prices = data.get('data', {}).get('prices', {})
                    self.log_test("Stock Prices", True, f"Prices retrieved for {len(prices)} symbols", data)
                else:
                    self.log_test("Stock Prices", False, "Success status not returned", data)
            else:
                self.log_test("Stock Prices", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Stock Prices", False, f"Exception: {str(e)}")
    
    def test_portfolio_value(self, portfolio_id: str = None):
        """Test portfolio valuation endpoint."""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.consent_token,
                "portfolio_id": portfolio_id or "test_portfolio_123",
                "include_performance": True
            }
            
            response = requests.post(f"{self.base_url}/agents/chandufinance/market/portfolio-value", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    value = data.get('data', {}).get('current_value', 0)
                    self.log_test("Portfolio Value", True, f"Portfolio value: ${value:,.2f}", data)
                else:
                    self.log_test("Portfolio Value", False, "Success status not returned", data)
            else:
                self.log_test("Portfolio Value", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Portfolio Value", False, f"Exception: {str(e)}")

    # ====================================================================
    # PLANNING TESTS
    # ====================================================================
    
    def test_retirement_planning(self):
        """Test retirement planning endpoint."""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.consent_token,
                "current_age": 30,
                "retirement_age": 65,
                "desired_retirement_income": 5000.0,
                "current_savings": 25000.0,
                "gemini_api_key": GEMINI_API_KEY
            }
            
            response = requests.post(f"{self.base_url}/agents/chandufinance/planning/retirement", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    required = data.get('data', {}).get('required_savings', 0)
                    monthly = data.get('data', {}).get('monthly_contribution_needed', 0)
                    self.log_test("Retirement Planning", True, f"Required savings: ${required:,.2f}, Monthly: ${monthly:,.2f}", data)
                else:
                    self.log_test("Retirement Planning", False, "Success status not returned", data)
            else:
                self.log_test("Retirement Planning", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Retirement Planning", False, f"Exception: {str(e)}")
    
    def test_emergency_fund(self):
        """Test emergency fund analysis endpoint."""
        try:
            payload = {
                "user_id": self.user_id,
                "token": self.consent_token,
                "monthly_expenses": 3000.0,
                "current_emergency_fund": 5000.0,
                "risk_profile": "moderate",
                "gemini_api_key": GEMINI_API_KEY
            }
            
            response = requests.post(f"{self.base_url}/agents/chandufinance/planning/emergency-fund", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    recommended = data.get('data', {}).get('recommended_amount', 0)
                    gap = data.get('data', {}).get('funding_gap', 0)
                    self.log_test("Emergency Fund", True, f"Recommended: ${recommended:,.2f}, Gap: ${gap:,.2f}", data)
                else:
                    self.log_test("Emergency Fund", False, "Success status not returned", data)
            else:
                self.log_test("Emergency Fund", False, f"HTTP {response.status_code}", response.json())
                
        except Exception as e:
            self.log_test("Emergency Fund", False, f"Exception: {str(e)}")

    # ====================================================================
    # TEST ORCHESTRATION
    # ====================================================================
    
    def run_all_tests(self):
        """Run comprehensive test suite for all new finance endpoints."""
        print("🚀 Starting Comprehensive Finance Endpoint Tests")
        print("=" * 60)
        
        # Setup
        self.consent_token = self.create_consent_token()
        portfolio_id = None
        
        # Portfolio Management Tests
        print("\n📊 PORTFOLIO MANAGEMENT TESTS")
        print("-" * 40)
        portfolio_id = self.test_portfolio_creation()
        self.test_portfolio_analysis(portfolio_id)
        self.test_portfolio_rebalance(portfolio_id)
        
        # Analytics Tests
        print("\n📈 FINANCIAL ANALYTICS TESTS")
        print("-" * 40)
        self.test_cashflow_analysis()
        self.test_spending_analysis()
        self.test_tax_optimization()
        
        # Market Data Tests
        print("\n💹 MARKET DATA TESTS")
        print("-" * 40)
        self.test_stock_prices()
        self.test_portfolio_value(portfolio_id)
        
        # Planning Tests
        print("\n🎯 ADVANCED PLANNING TESTS")
        print("-" * 40)
        self.test_retirement_planning()
        self.test_emergency_fund()
        
        # Summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test_name']}: {result['details']}")
        
        print("\n💾 Saving detailed results to test_results.json")
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)

def main():
    """Main test execution function."""
    tester = FinanceEndpointTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

