"""
Comprehensive test suite for MailerPanda API endpoints
Tests all 6 endpoints with various scenarios
"""

import requests
import json
import base64
import pandas as pd
import time
import tempfile
import os
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://127.0.0.1:8001"
MAILERPANDA_BASE = f"{API_BASE_URL}/agents/mailerpanda"

# Test data
TEST_EMAILS = [
    "dragnoid121@gmail.com",
    "alokkale121@gmail.com", 
    "23b4215@iitb.ac.in"
]

def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{'='*60}")
    print(f"TESTING: {test_name}")
    print(f"{'='*60}")

def print_test_result(endpoint: str, status: int, response: Dict[Any, Any]):
    """Print test results in a formatted way"""
    print(f"\nEndpoint: {endpoint}")
    print(f"Status Code: {status}")
    print(f"Response: {json.dumps(response, indent=2)}")
    
def create_test_excel_file(with_descriptions: bool = True) -> str:
    """Create a test Excel file and return as base64"""
    data = {
        'name': ['John Gaming', 'Alice Engineer', 'Bob Student'],
        'email': TEST_EMAILS,
        'company': ['GameDev Studios', 'TechCorp Inc', 'IIT Bombay']
    }
    
    if with_descriptions:
        data['description'] = [
            'Passionate indie game developer working on mobile RPGs',
            'Senior software engineer specializing in cloud infrastructure',
            'Computer science student interested in AI and machine learning'
        ]
    
    df = pd.DataFrame(data)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        excel_path = tmp_file.name
    
    # Read and encode as base64
    with open(excel_path, 'rb') as f:
        excel_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Cleanup
    os.unlink(excel_path)
    
    return excel_data

def test_1_get_status():
    """Test 1: GET /agents/mailerpanda/status"""
    print_test_header("MailerPanda Status")
    
    response = requests.get(f"{MAILERPANDA_BASE}/status")
    print_test_result("/status", response.status_code, response.json())
    
    return response.status_code == 200

def test_2_analyze_excel():
    """Test 2: POST /agents/mailerpanda/analyze-excel"""
    print_test_header("Excel Analysis (With Descriptions)")
    
    excel_data = create_test_excel_file(with_descriptions=True)
    
    payload = {
        "excel_file_data": excel_data
    }
    
    response = requests.post(
        f"{MAILERPANDA_BASE}/analyze-excel",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print_test_result("/analyze-excel (with descriptions)", response.status_code, response.json())
    
    # Test without descriptions
    print_test_header("Excel Analysis (Without Descriptions)")
    
    excel_data_no_desc = create_test_excel_file(with_descriptions=False)
    
    payload_no_desc = {
        "excel_file_data": excel_data_no_desc
    }
    
    response_no_desc = requests.post(
        f"{MAILERPANDA_BASE}/analyze-excel",
        json=payload_no_desc,
        headers={"Content-Type": "application/json"}
    )
    
    print_test_result("/analyze-excel (without descriptions)", response_no_desc.status_code, response_no_desc.json())
    
    return response.status_code == 200 and response_no_desc.status_code == 200

def test_3_mass_email():
    """Test 3: POST /agents/mailerpanda/mass-email"""
    print_test_header("Mass Email (With Context Personalization)")
    
    excel_data = create_test_excel_file(with_descriptions=True)
    
    payload = {
        "user_id": "test_user_comprehensive",
        "excel_file_data": excel_data,
        "email_subject": "Comprehensive API Test - Context Personalized",
        "email_body": "This is a test email with context personalization enabled.",
        "use_context_personalization": True
    }
    
    response = requests.post(
        f"{MAILERPANDA_BASE}/mass-email",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print_test_result("/mass-email (with context)", response.status_code, response.json())
    
    # Test without context personalization
    print_test_header("Mass Email (Without Context Personalization)")
    
    payload_no_context = {
        "user_id": "test_user_comprehensive_no_context",
        "excel_file_data": excel_data,
        "email_subject": "Comprehensive API Test - Standard",
        "email_body": "This is a test email with standard personalization only.",
        "use_context_personalization": False
    }
    
    response_no_context = requests.post(
        f"{MAILERPANDA_BASE}/mass-email",
        json=payload_no_context,
        headers={"Content-Type": "application/json"}
    )
    
    print_test_result("/mass-email (without context)", response_no_context.status_code, response_no_context.json())
    
    return response.status_code == 200 and response_no_context.status_code == 200

def test_4_single_email_execute():
    """Test 4: POST /agents/mailerpanda/execute (Single Email)"""
    print_test_header("Single Email Execution")
    
    payload = {
        "user_id": "test_user_single",
        "recipient_email": "dragnoid121@gmail.com",
        "recipient_name": "John Gaming",
        "email_subject": "Single Email Test",
        "email_body": "This is a single email test from the comprehensive test suite.",
        "description": "Game developer working on indie mobile games"
    }
    
    response = requests.post(
        f"{MAILERPANDA_BASE}/execute",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print_test_result("/execute", response.status_code, response.json())
    
    return response.status_code == 200

def test_5_approval_workflow():
    """Test 5: POST /agents/mailerpanda/approve (Approval Workflow)"""
    print_test_header("Approval Workflow Test")
    
    # First create a session that requires approval
    payload = {
        "user_id": "test_user_approval",
        "recipient_email": "alokkale121@gmail.com",
        "recipient_name": "Alice Engineer",
        "email_subject": "Approval Test Email",
        "email_body": "This email tests the approval workflow.",
        "description": "Senior engineer specializing in cloud infrastructure"
    }
    
    # Execute to create session
    execute_response = requests.post(
        f"{MAILERPANDA_BASE}/execute",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Execute response: {execute_response.status_code}")
    
    if execute_response.status_code == 200:
        result = execute_response.json()
        
        if result.get("status") == "pending_approval":
            campaign_id = result.get("campaign_id")
            print(f"Campaign ID for approval: {campaign_id}")
            
            # Now test approval
            approval_payload = {
                "campaign_id": campaign_id,
                "approved": True
            }
            
            approval_response = requests.post(
                f"{MAILERPANDA_BASE}/approve",
                json=approval_payload,
                headers={"Content-Type": "application/json"}
            )
            
            print_test_result("/approve", approval_response.status_code, approval_response.json())
            return approval_response.status_code == 200
        else:
            print("Email was auto-approved, approval workflow not triggered")
            return True
    
    return False

def test_6_session_status():
    """Test 6: GET /agents/mailerpanda/session/{campaign_id}"""
    print_test_header("Session Status Check")
    
    # First create a session
    payload = {
        "user_id": "test_user_session",
        "recipient_email": "23b4215@iitb.ac.in",
        "recipient_name": "Bob Student", 
        "email_subject": "Session Status Test",
        "email_body": "This email tests session status retrieval.",
        "description": "CS student interested in AI and ML"
    }
    
    execute_response = requests.post(
        f"{MAILERPANDA_BASE}/execute",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if execute_response.status_code == 200:
        result = execute_response.json()
        campaign_id = result.get("campaign_id")
        
        if campaign_id:
            # Check session status
            session_response = requests.get(f"{MAILERPANDA_BASE}/session/{campaign_id}")
            print_test_result(f"/session/{campaign_id}", session_response.status_code, session_response.json())
            return session_response.status_code == 200
    
    return False

def run_comprehensive_tests():
    """Run all MailerPanda API tests"""
    print("🐼 MAILERPANDA API COMPREHENSIVE TEST SUITE 🐼")
    print("Testing all 6 endpoints with various scenarios")
    
    # Check if server is running
    try:
        health_check = requests.get(f"{API_BASE_URL}/agents")
        print(f"✅ API Server is running (Status: {health_check.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ API Server is not running. Please start it first.")
        return
    
    # Test results
    results = []
    
    # Run all tests
    tests = [
        ("Status Check", test_1_get_status),
        ("Excel Analysis", test_2_analyze_excel),
        ("Mass Email", test_3_mass_email), 
        ("Single Email Execute", test_4_single_email_execute),
        ("Approval Workflow", test_5_approval_workflow),
        ("Session Status", test_6_session_status)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            success = test_func()
            results.append((test_name, "✅ PASSED" if success else "❌ FAILED"))
            time.sleep(2)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Test {test_name} failed with error: {str(e)}")
            results.append((test_name, f"❌ ERROR: {str(e)}"))
    
    # Print final results
    print(f"\n{'='*60}")
    print("FINAL TEST RESULTS")
    print(f"{'='*60}")
    
    for test_name, result in results:
        print(f"{test_name}: {result}")
    
    passed_tests = sum(1 for _, result in results if "✅ PASSED" in result)
    total_tests = len(results)
    
    print(f"\n📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! MailerPanda API is fully functional!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    run_comprehensive_tests()
