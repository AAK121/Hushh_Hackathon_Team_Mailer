#!/usr/bin/env python3
"""
Working test suite for the new finance endpoints with proper token handling.
"""

import json
import requests
from datetime import datetime

BASE_URL = "http://localhost:8001"

def create_test_token():
    """Create a proper consent token for testing."""
    try:
        payload = {
            "user_id": "test_user_finance",
            "agent_id": "agent_chandufinance", 
            "scope": "vault.read.finance"
        }
        
        response = requests.post(f"{BASE_URL}/consent/tokens", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        else:
            print(f"Token creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            # Return a mock token for testing
            return "test_token_123"
    except Exception as e:
        print(f"Token creation error: {e}")
        return "test_token_123"

def test_portfolio_creation():
    """Test the portfolio creation endpoint."""
    print("🧪 Testing Portfolio Creation")
    
    token = create_test_token()
    
    payload = {
        "user_id": "test_user_finance",
        "token": token,
        "portfolio_name": "Test Growth Portfolio",
        "investment_amount": 15000.0,
        "risk_tolerance": "moderate",
        "investment_goals": ["growth", "retirement"],
        "time_horizon": 15,
        "gemini_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/portfolio/create", 
                               json=payload, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('status') == 'success':
                print("✅ Portfolio creation successful!")
                return data.get('data', {}).get('portfolio_id')
            else:
                print("❌ Portfolio creation failed")
                print(f"Errors: {data.get('errors')}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_cashflow_analysis():
    """Test the cashflow analysis endpoint."""
    print("\n🧪 Testing Cashflow Analysis") 
    
    token = create_test_token()
    
    payload = {
        "user_id": "test_user_finance",
        "token": token,
        "period_months": 12,
        "include_projections": True,
        "gemini_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/analytics/cashflow",
                               json=payload, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('status') == 'success'}")
            
            if data.get('status') == 'success':
                print("✅ Cashflow analysis successful!")
                monthly_analysis = data.get('data', {}).get('monthly_analysis', {})
                print(f"Monthly net cashflow: ${monthly_analysis.get('net_cashflow', 0):,.2f}")
                return True
            else:
                print("❌ Cashflow analysis failed")
                print(f"Errors: {data.get('errors')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_stock_prices():
    """Test the stock prices endpoint."""
    print("\n🧪 Testing Stock Prices")
    
    token = create_test_token()
    
    payload = {
        "user_id": "test_user_finance", 
        "token": token,
        "symbols": ["AAPL", "GOOGL", "MSFT"],
        "include_analysis": True,
        "gemini_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/market/stock-price",
                               json=payload, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                print("✅ Stock prices retrieved successfully!")
                prices = data.get('data', {}).get('prices', {})
                for symbol, price_data in prices.items():
                    print(f"{symbol}: ${price_data.get('price', 0):.2f}")
                return True
            else:
                print("❌ Stock prices failed")
                print(f"Errors: {data.get('errors')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_retirement_planning():
    """Test the retirement planning endpoint."""
    print("\n🧪 Testing Retirement Planning")
    
    token = create_test_token()
    
    payload = {
        "user_id": "test_user_finance",
        "token": token,
        "current_age": 35,
        "retirement_age": 65,
        "desired_retirement_income": 6000.0,
        "current_savings": 50000.0,
        "gemini_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/agents/chandufinance/planning/retirement",
                               json=payload, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                print("✅ Retirement planning successful!")
                result_data = data.get('data', {})
                print(f"Required savings: ${result_data.get('required_savings', 0):,.2f}")
                print(f"Monthly contribution needed: ${result_data.get('monthly_contribution_needed', 0):,.2f}")
                return True
            else:
                print("❌ Retirement planning failed")
                print(f"Errors: {data.get('errors')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Run all endpoint tests."""
    print("🚀 Testing New Finance Agent Endpoints")
    print("=" * 60)
    
    tests = [
        ("Portfolio Creation", test_portfolio_creation),
        ("Cashflow Analysis", test_cashflow_analysis), 
        ("Stock Prices", test_stock_prices),
        ("Retirement Planning", test_retirement_planning)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")

if __name__ == "__main__":
    main()

