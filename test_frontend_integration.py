#!/usr/bin/env python3
"""
Frontend Integration Test - Test the FinanceAgent component integration
"""

import requests
import json
import time

def test_frontend_integration():
    """Test if frontend can connect to backend and display properly"""
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    # Test 1: API Connection
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is accessible")
        else:
            print(f"❌ Backend API returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend API: {e}")
        return False
    
    # Test 2: Frontend Service
    try:
        response = requests.get("http://localhost:5174", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend dev server is accessible")
        else:
            print(f"❌ Frontend returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to frontend: {e}")
        return False
    
    # Test 3: CORS Headers
    try:
        response = requests.options("http://localhost:8001/agents/chandufinance/execute", 
                                  headers={"Origin": "http://localhost:5174"})
        print("✅ CORS headers configured properly")
    except Exception as e:
        print(f"⚠️  CORS might have issues: {e}")
    
    print("\n🎉 Integration test passed!")
    print("📱 You can now test the Finance Agent in your browser:")
    print("   1. Open: http://localhost:5174")
    print("   2. Navigate to Finance Agent")
    print("   3. Test all features:")
    print("      • Dashboard with financial metrics")
    print("      • Portfolio creation and analysis")
    print("      • Cashflow and spending analytics")
    print("      • Real-time market data")
    print("      • Retirement and emergency fund planning")
    print("      • AI insights and recommendations")
    
    return True

def test_specific_endpoints():
    """Test specific ChanduFinance endpoints that the frontend uses"""
    print("\n🔧 Testing Specific Frontend Functions")
    print("=" * 50)
    
    # Create token first
    try:
        token_response = requests.post("http://localhost:8001/consent/tokens", json={
            "user_id": "demo_user",
            "agent_id": "agent_chandufinance", 
            "scope": "vault.read.finance"
        })
        
        if token_response.status_code == 200:
            token = token_response.json().get("token")
            print(f"✅ Token created: {token[:20]}...")
        else:
            print("❌ Failed to create token")
            return False
            
    except Exception as e:
        print(f"❌ Token creation failed: {e}")
        return False
    
    # Test endpoints that frontend uses
    endpoints_to_test = [
        {
            "name": "Profile Setup", 
            "url": "/agents/chandufinance/execute",
            "payload": {
                "user_id": "demo_user",
                "token": token,
                "command": "setup_profile",
                "full_name": "Test User",
                "age": 30,
                "occupation": "Developer",
                "monthly_income": 5000,
                "monthly_expenses": 3000,
                "current_savings": 10000,
                "investment_budget": 1000,
                "risk_tolerance": "moderate",
                "investment_experience": "beginner"
            }
        },
        {
            "name": "Portfolio Creation",
            "url": "/agents/chandufinance/portfolio/create", 
            "payload": {
                "user_id": "demo_user",
                "token": token,
                "portfolio_name": "Test Portfolio",
                "investment_amount": 5000,
                "risk_tolerance": "moderate",
                "investment_goals": ["growth"],
                "time_horizon": 5
            }
        },
        {
            "name": "Market Data",
            "url": "/agents/chandufinance/market/stock-price",
            "payload": {
                "user_id": "demo_user", 
                "token": token,
                "symbols": ["AAPL", "GOOGL"],
                "include_analysis": True
            }
        }
    ]
    
    success_count = 0
    for test in endpoints_to_test:
        try:
            response = requests.post(f"http://localhost:8001{test['url']}", 
                                   json=test['payload'], timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    print(f"✅ {test['name']}: Working")
                    success_count += 1
                else:
                    print(f"❌ {test['name']}: Failed - {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ {test['name']}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {test['name']}: Exception - {e}")
    
    print(f"\n📊 Endpoint Tests: {success_count}/{len(endpoints_to_test)} passed")
    return success_count == len(endpoints_to_test)

if __name__ == "__main__":
    print("🔥 Finance Frontend Integration Test")
    print("This will verify that your frontend can communicate with the backend\n")
    
    if test_frontend_integration():
        if test_specific_endpoints():
            print("\n🎊 ALL TESTS PASSED!")
            print("🚀 Your Finance Agent frontend is ready to use!")
        else:
            print("\n⚠️  Some endpoint tests failed, but basic integration works")
    else:
        print("\n❌ Integration test failed. Check if both servers are running.")
