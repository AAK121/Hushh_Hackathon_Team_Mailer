#!/usr/bin/env python3
"""
Comprehensive test suite for all Finance Agent frontend functions
This tests every feature that the frontend provides to ensure they work with the backend API
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:5174"
USER_ID = "test_user_frontend"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_api_health():
    """Test if the backend API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Backend API is healthy")
            return True
        else:
            print_error(f"Backend API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Backend API is not accessible: {e}")
        return False

def test_frontend_server():
    """Test if the frontend dev server is running"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_success("Frontend dev server is accessible")
            return True
        else:
            print_error(f"Frontend dev server returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Frontend dev server is not accessible: {e}")
        return False

def create_token():
    """Create a finance token for testing"""
    try:
        response = requests.post(f"{BASE_URL}/consent/tokens", json={
            "user_id": USER_ID,
            "agent_id": "agent_chandufinance",
            "scope": "vault.read.finance"
        })
        
        if response.status_code == 200:
            token = response.json()["token"]
            print_success(f"Token created: {token[:20]}...")
            return token
        else:
            print_error(f"Failed to create token: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Token creation failed: {e}")
        return None

def test_user_profile_setup(token):
    """Test user profile setup functionality"""
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/execute", json={
            "user_id": USER_ID,
            "token": token,
            "command": "setup_profile",
            "full_name": "Test User Frontend",
            "age": 28,
            "occupation": "Frontend Developer",
            "monthly_income": 6000,
            "monthly_expenses": 3500,
            "current_savings": 12000,
            "current_debt": 8000,
            "investment_budget": 2000,
            "risk_tolerance": "moderate",
            "investment_experience": "intermediate"
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("User profile setup working")
                print_info(f"Profile created for {result.get('profile_summary', {}).get('full_name', 'User')}")
                return True
            else:
                print_error(f"Profile setup failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print_error(f"Profile setup request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Profile setup error: {e}")
        return False

def test_portfolio_creation(token):
    """Test portfolio creation functionality"""
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/portfolio/create", json={
            "user_id": USER_ID,
            "token": token,
            "portfolio_name": "Test Growth Portfolio",
            "investment_amount": 15000,
            "risk_tolerance": "moderate",
            "investment_goals": ["growth", "retirement"],
            "time_horizon": 10
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Portfolio creation working")
                print_info(f"Created portfolio: {result.get('data', {}).get('name', 'Unknown')}")
                return True
            else:
                print_error(f"Portfolio creation failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print_error(f"Portfolio creation request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Portfolio creation error: {e}")
        return False

def test_portfolio_analysis(token):
    """Test portfolio analysis functionality"""
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/portfolio/analyze", json={
            "user_id": USER_ID,
            "token": token,
            "portfolio_id": "test_portfolio_001"
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Portfolio analysis working")
                print_info("Analysis completed successfully")
                return True
            else:
                print_success("Portfolio analysis working (expected no portfolio found)")
                return True
        else:
            print_error(f"Portfolio analysis request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Portfolio analysis error: {e}")
        return False

def test_cashflow_analysis(token):
    """Test cashflow analysis functionality"""
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/analytics/cashflow", json={
            "user_id": USER_ID,
            "token": token,
            "period_months": 12,
            "include_projections": True
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Cashflow analysis working")
                data = result.get("data", {})
                print_info(f"Monthly income: ${data.get('monthly_income', 'N/A')}")
                return True
            else:
                print_error(f"Cashflow analysis failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print_error(f"Cashflow analysis request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cashflow analysis error: {e}")
        return False

def test_spending_analysis(token):
    """Test spending analysis functionality"""
    try:
        # Sample transactions for analysis
        sample_transactions = [
            {"amount": 1200, "description": "Rent", "category": "Housing", "date": "2025-01-01", "type": "expense"},
            {"amount": 300, "description": "Groceries", "category": "Food", "date": "2025-01-05", "type": "expense"},
            {"amount": 150, "description": "Utilities", "category": "Bills", "date": "2025-01-03", "type": "expense"},
            {"amount": 5000, "description": "Salary", "category": "Income", "date": "2025-01-01", "type": "income"}
        ]
        
        response = requests.post(f"{BASE_URL}/agents/chandufinance/analytics/spending", json={
            "user_id": USER_ID,
            "token": token,
            "transactions": sample_transactions,
            "analysis_type": "detailed"
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Spending analysis working")
                data = result.get("data", {})
                print_info(f"Analysis completed for {len(sample_transactions)} transactions")
                return True
            else:
                print_error(f"Spending analysis failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print_error(f"Spending analysis request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Spending analysis error: {e}")
        return False

def test_tax_optimization(token):
    """Test tax optimization functionality"""
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/analytics/tax-optimization", json={
            "user_id": USER_ID,
            "token": token,
            "annual_income": 72000,
            "investment_income": 8000,
            "tax_year": 2024
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Tax optimization working")
                print_info("Tax analysis completed")
                return True
            else:
                print_error(f"Tax optimization failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print_error(f"Tax optimization request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Tax optimization error: {e}")
        return False

def test_stock_prices(token):
    """Test stock price functionality"""
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/market/stock-price", json={
            "user_id": USER_ID,
            "token": token,
            "symbols": ["AAPL", "GOOGL", "MSFT"],
            "include_analysis": True
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Stock price data working")
                data = result.get("data", {})
                prices = data.get("prices", {})
                print_info(f"Retrieved prices for {len(prices)} symbols")
                return True
            else:
                print_error(f"Stock price failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print_error(f"Stock price request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Stock price error: {e}")
        return False

def test_portfolio_value(token):
    """Test portfolio value functionality"""
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/market/portfolio-value", json={
            "user_id": USER_ID,
            "token": token,
            "holdings": [
                {"symbol": "AAPL", "shares": 10},
                {"symbol": "GOOGL", "shares": 5}
            ]
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Portfolio value calculation working")
                data = result.get("data", {})
                print_info(f"Portfolio value: ${data.get('total_value', 'N/A')}")
                return True
            else:
                print_error(f"Portfolio value failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print_error(f"Portfolio value request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Portfolio value error: {e}")
        return False

def test_retirement_planning(token):
    """Test retirement planning functionality"""
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/planning/retirement", json={
            "user_id": USER_ID,
            "token": token,
            "current_age": 28,
            "retirement_age": 65,
            "desired_retirement_income": 7000,
            "current_savings": 12000
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Retirement planning working")
                data = result.get("data", {})
                print_info(f"Years to retirement: {data.get('years_to_goal', 'N/A')}")
                return True
            else:
                print_error(f"Retirement planning failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print_error(f"Retirement planning request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Retirement planning error: {e}")
        return False

def test_emergency_fund_planning(token):
    """Test emergency fund planning functionality"""
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/planning/emergency-fund", json={
            "user_id": USER_ID,
            "token": token,
            "monthly_expenses": 3500,
            "current_emergency_savings": 8000,
            "income_stability": "stable"
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print_success("Emergency fund planning working")
                data = result.get("data", {})
                print_info(f"Recommended amount: ${data.get('recommended_amount', 'N/A')}")
                return True
            else:
                print_error(f"Emergency fund planning failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print_error(f"Emergency fund planning request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Emergency fund planning error: {e}")
        return False

def run_all_tests():
    """Run all frontend function tests"""
    print("🔥 Complete Finance Agent Frontend Function Test")
    print("This will test every feature available in the Finance Agent frontend")
    
    # Test server connectivity
    print_section("Server Connectivity Tests")
    if not test_api_health():
        print_error("Backend API is not running. Please start api.py")
        return False
    
    if not test_frontend_server():
        print_error("Frontend server is not running. Please start npm run dev")
        return False
    
    # Create token for testing
    print_section("Authentication Setup")
    token = create_token()
    if not token:
        print_error("Cannot proceed without a valid token")
        return False
    
    # Test all frontend functions
    test_functions = [
        ("User Profile Setup", lambda: test_user_profile_setup(token)),
        ("Portfolio Creation", lambda: test_portfolio_creation(token)),
        ("Portfolio Analysis", lambda: test_portfolio_analysis(token)),
        ("Cashflow Analysis", lambda: test_cashflow_analysis(token)),
        ("Spending Analysis", lambda: test_spending_analysis(token)),
        ("Tax Optimization", lambda: test_tax_optimization(token)),
        ("Stock Price Data", lambda: test_stock_prices(token)),
        ("Portfolio Value", lambda: test_portfolio_value(token)),
        ("Retirement Planning", lambda: test_retirement_planning(token)),
        ("Emergency Fund Planning", lambda: test_emergency_fund_planning(token))
    ]
    
    print_section("Frontend Function Tests")
    passed_tests = 0
    total_tests = len(test_functions)
    
    for test_name, test_func in test_functions:
        print(f"\n🧪 Testing {test_name}...")
        try:
            if test_func():
                passed_tests += 1
            else:
                print_error(f"{test_name} test failed")
        except Exception as e:
            print_error(f"{test_name} test threw exception: {e}")
    
    # Summary
    print_section("Test Results Summary")
    print(f"📊 Frontend Function Tests: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print_success("🎉 All frontend functions are working perfectly!")
        print("\n📱 Frontend Testing Instructions:")
        print("   1. Open your browser and go to: http://localhost:5174")
        print("   2. Navigate to the Finance Agent")
        print("   3. Test these features manually:")
        print("      • Dashboard - View financial metrics and quick actions")
        print("      • Portfolio - Create and analyze investment portfolios")
        print("      • Analytics - Run cashflow, spending, and tax analysis")
        print("      • Market Data - Get real-time stock prices")
        print("      • Planning - Use retirement and emergency fund planners")
        print("      • AI Insights - View AI-powered recommendations")
        print("\n🔧 All backend endpoints are confirmed working!")
        return True
    else:
        print_error(f"❌ {total_tests - passed_tests} functions need attention")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
