#!/usr/bin/env python3
"""
COMPREHENSIVE API INTEGRATION TEST - 100% SUCCESS TARGET
========================================================

This test validates ALL HushhMCP agents using the API server with:
✅ Real API keys from .env passed as dynamic parameters
✅ Fresh tokens with extended expiry
✅ Full integration testing through API endpoints only
✅ No hardcoded credentials in agent code
✅ Complete functionality verification

Agents Tested:
1. ChanduFinance - Financial advice with AI analysis
2. RelationshipMemory - Contact and memory management  
3. MailerPanda - Email campaign management
4. AddToCalendar - Email processing and calendar events

Target: 100% SUCCESS RATE with real API functionality
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
BASE_URL = "http://127.0.0.1:8002"
HEADERS = {"Content-Type": "application/json"}

# Extract real API keys from environment
REAL_API_KEYS = {
    "gemini_api_key": os.getenv("GEMINI_API_KEY"),
    "google_api_key": os.getenv("GOOGLE_API_KEY"), 
    "mailjet_api_key": os.getenv("MAILJET_API_KEY"),
    "mailjet_api_secret": os.getenv("MAILJET_API_SECRET"),
}

# Fresh tokens with correct user ID and scopes
INTEGRATION_TOKENS = {
    "vault.write.file": "HCT:aW50ZWdyYXRpb25fdGVzdF91c2VyfGNoYW5kdWZpbmFuY2V8dmF1bHQud3JpdGUuZmlsZXwxNzU1NzkxMzg2OTEwfDE3NTU4Nzc3ODY5MTA=.9ada0a7672ff8d1226c2f8894f36cc4aac962fb0931b1a915a11726d4bafec07",
    "vault.read.contacts": "HCT:aW50ZWdyYXRpb25fdGVzdF91c2VyfGNoYW5kdWZpbmFuY2V8dmF1bHQucmVhZC5jb250YWN0c3wxNzU1NzkxMzg2OTExfDE3NTU4Nzc3ODY5MTE=.48278c0fe004b2a3b0ce6ecdf9bebca889d0cef6b2d5deb93c484ca75a2fa08e",
    "vault.write.contacts": "HCT:aW50ZWdyYXRpb25fdGVzdF91c2VyfGNoYW5kdWZpbmFuY2V8dmF1bHQud3JpdGUuY29udGFjdHN8MTc1NTc5MTM4NjkxMXwxNzU1ODc3Nzg2OTEx.a16e79b59796df2eb4bc897206d17767ca3d85f5a1196cead6d735eba4764830",
    "vault.read.email": "HCT:aW50ZWdyYXRpb25fdGVzdF91c2VyfGNoYW5kdWZpbmFuY2V8dmF1bHQucmVhZC5lbWFpbHwxNzU1NzkxMzg2OTExfDE3NTU4Nzc3ODY5MTE=.7646066aea61cb0f994ee3d8b8f99c4151f4dd7bfd17d1fad8236a7e2dfe6f76",
    "vault.write.email": "HCT:aW50ZWdyYXRpb25fdGVzdF91c2VyfGNoYW5kdWZpbmFuY2V8dmF1bHQud3JpdGUuZW1haWx8MTc1NTc5MTM4NjkxMXwxNzU1ODc3Nzg2OTEx.2176e35b4454545d27e9e4a70172e9a779fdaf797ccc65a27b58e91b32d04b75"
}

# Test configuration
TEST_USER_ID = "integration_test_user"

class APIIntegrationTester:
    """Comprehensive API integration tester for all HushhMCP agents."""
    
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def test_api_endpoint(self, agent_name: str, endpoint: str, payload: Dict[str, Any], 
                         test_description: str) -> Dict[str, Any]:
        """Test a specific API endpoint with comprehensive logging."""
        
        print(f"\n🧪 Testing: {test_description}")
        print(f"📡 Endpoint: {endpoint}")
        print(f"🔑 API Keys: {list(payload.get('api_keys', {}).keys()) if payload.get('api_keys') else 'Direct keys'}")
        
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", 
                                   headers=HEADERS, json=payload, timeout=45)
            
            result = {
                "status_code": response.status_code,
                "success": False,
                "response_data": None,
                "error": None,
                "test_description": test_description
            }
            
            if response.status_code == 200:
                data = response.json()
                result["response_data"] = data
                
                # Check for multiple success statuses
                if data.get("status") in ["success", "completed"]:
                    result["success"] = True
                    print(f"✅ SUCCESS: {test_description}")
                    print(f"📊 Response: {data.get('message', 'Operation completed successfully')}")
                    self.passed_tests += 1
                else:
                    result["error"] = data.get("errors", ["Unknown error"])
                    print(f"❌ FAILED: {test_description}")
                    print(f"🚨 Error: {result['error']}")
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ FAILED: {test_description}")
                print(f"🚨 HTTP Error: {result['error']}")
                
            self.total_tests += 1
            return result
            
        except Exception as e:
            result = {
                "status_code": None,
                "success": False,
                "response_data": None,
                "error": str(e),
                "test_description": test_description
            }
            print(f"❌ EXCEPTION: {test_description}")
            print(f"🚨 Exception: {e}")
            self.total_tests += 1
            return result

    def test_chandufinance_agent(self) -> List[Dict[str, Any]]:
        """Test ChanduFinance agent with comprehensive functionality."""
        
        print("\n" + "="*60)
        print("🏦 TESTING CHANDUFINANCE AGENT")
        print("="*60)
        
        tests = []
        
        # Test 1: Profile Setup with Dynamic API Key
        payload = {
            "user_id": TEST_USER_ID,
            "token": INTEGRATION_TOKENS["vault.write.file"],
            "command": "setup_profile",
            "full_name": "Integration Test User",
            "age": 30,
            "monthly_income": 5000.0,
            "monthly_expenses": 3000.0,
            "risk_tolerance": "moderate",
            "gemini_api_key": REAL_API_KEYS["gemini_api_key"],
            "api_keys": {
                "custom_finance_key": "test_integration_value"
            }
        }
        
        result = self.test_api_endpoint(
            "ChanduFinance",
            "/agents/chandufinance/execute",
            payload,
            "Profile Setup with Dynamic API Keys"
        )
        tests.append(result)
        
        # Test 2: View Profile
        payload = {
            "user_id": TEST_USER_ID,
            "token": INTEGRATION_TOKENS["vault.write.file"],
            "command": "view_profile",
            "gemini_api_key": REAL_API_KEYS["gemini_api_key"]
        }
        
        result = self.test_api_endpoint(
            "ChanduFinance",
            "/agents/chandufinance/execute", 
            payload,
            "View Profile with Dynamic Gemini API Key"
        )
        tests.append(result)
        
        # Test 3: Educational Content with AI 
        payload = {
            "user_id": TEST_USER_ID,
            "token": INTEGRATION_TOKENS["vault.write.file"],
            "command": "explain_like_im_new",
            "topic": "compound_interest",
            "complexity": "beginner",
            "gemini_api_key": REAL_API_KEYS["gemini_api_key"]
        }
        
        result = self.test_api_endpoint(
            "ChanduFinance",
            "/agents/chandufinance/execute",
            payload,
            "Educational Content with Dynamic AI Analysis"
        )
        tests.append(result)
        
        return tests

    def test_relationship_memory_agent(self) -> List[Dict[str, Any]]:
        """Test RelationshipMemory agent with comprehensive functionality."""
        
        print("\n" + "="*60)
        print("👥 TESTING RELATIONSHIP MEMORY AGENT")
        print("="*60)
        
        tests = []
        
        # Test 1: Add Contact with Dynamic API Key
        payload = {
            "user_id": TEST_USER_ID,
            "tokens": {
                "vault.read.contacts": INTEGRATION_TOKENS["vault.read.contacts"],
                "vault.write.contacts": INTEGRATION_TOKENS["vault.write.contacts"],
                "vault.read.email": INTEGRATION_TOKENS["vault.read.email"]
            },
            "user_input": "Add a new contact: John Doe, email john@example.com, works at TechCorp",
            "gemini_api_key": REAL_API_KEYS["gemini_api_key"],
            "api_keys": {
                "custom_memory_key": "test_integration_value"
            }
        }
        
        result = self.test_api_endpoint(
            "RelationshipMemory",
            "/agents/relationship_memory/execute",
            payload,
            "Add Contact with Dynamic API Keys"
        )
        tests.append(result)
        
        # Test 2: Query Contacts
        payload = {
            "user_id": TEST_USER_ID,
            "tokens": {
                "vault.read.contacts": INTEGRATION_TOKENS["vault.read.contacts"],
                "vault.write.contacts": INTEGRATION_TOKENS["vault.write.contacts"]
            },
            "user_input": "Show me all my contacts",
            "gemini_api_key": REAL_API_KEYS["gemini_api_key"]
        }
        
        result = self.test_api_endpoint(
            "RelationshipMemory", 
            "/agents/relationship_memory/execute",
            payload,
            "Query Contacts with Dynamic Gemini API Key"
        )
        tests.append(result)
        
        return tests

    def test_mailerpanda_agent(self) -> List[Dict[str, Any]]:
        """Test MailerPanda agent with comprehensive functionality."""
        
        print("\n" + "="*60)
        print("📧 TESTING MAILERPANDA AGENT")
        print("="*60)
        
        tests = []
        
        # Test 1: Create Email Campaign with Dynamic API Keys
        payload = {
            "user_id": TEST_USER_ID,
            "user_input": "Create a welcome email campaign for new customers",
            "mode": "interactive",
            "consent_tokens": {
                "vault.read.email": INTEGRATION_TOKENS["vault.read.email"],
                "vault.write.email": INTEGRATION_TOKENS["vault.write.email"],
                "vault.read.contacts": INTEGRATION_TOKENS["vault.read.contacts"]
            },
            "google_api_key": REAL_API_KEYS["google_api_key"],
            "mailjet_api_key": REAL_API_KEYS["mailjet_api_key"],
            "mailjet_api_secret": REAL_API_KEYS["mailjet_api_secret"],
            "api_keys": {
                "custom_mailer_key": "test_integration_value"
            }
        }
        
        result = self.test_api_endpoint(
            "MailerPanda",
            "/agents/mailerpanda/execute",
            payload,
            "Create Email Campaign with Dynamic API Keys"
        )
        tests.append(result)
        
        # Test 2: Interactive Mode
        payload = {
            "user_id": TEST_USER_ID,
            "user_input": "Generate a promotional email for summer sale",
            "mode": "interactive",
            "consent_tokens": {
                "vault.read.email": INTEGRATION_TOKENS["vault.read.email"],
                "vault.write.email": INTEGRATION_TOKENS["vault.write.email"]
            },
            "google_api_key": REAL_API_KEYS["google_api_key"],
            "require_approval": True
        }
        
        result = self.test_api_endpoint(
            "MailerPanda",
            "/agents/mailerpanda/execute",
            payload,
            "Interactive Email Generation with Dynamic Google API Key"
        )
        tests.append(result)
        
        return tests

    def test_addtocalendar_agent(self) -> List[Dict[str, Any]]:
        """Test AddToCalendar agent with comprehensive functionality."""
        
        print("\n" + "="*60)
        print("📅 TESTING ADDTOCALENDAR AGENT")
        print("="*60)
        
        tests = []
        
        # Test 1: Analyze Only Mode with Dynamic API Key
        payload = {
            "user_id": TEST_USER_ID,
            "email_token": INTEGRATION_TOKENS["vault.read.email"],
            "calendar_token": INTEGRATION_TOKENS["vault.write.file"],
            "google_access_token": "demo_oauth_token_12345",
            "action": "analyze_only",
            "confidence_threshold": 0.6,
            "max_emails": 10,
            "google_api_key": REAL_API_KEYS["google_api_key"],
            "api_keys": {
                "custom_calendar_key": "test_integration_value"
            }
        }
        
        result = self.test_api_endpoint(
            "AddToCalendar",
            "/agents/addtocalendar/execute",
            payload,
            "Email Analysis with Dynamic API Keys"
        )
        tests.append(result)
        
        # Test 2: Manual Event Creation
        payload = {
            "user_id": TEST_USER_ID,
            "email_token": INTEGRATION_TOKENS["vault.read.email"],
            "calendar_token": INTEGRATION_TOKENS["vault.write.file"],
            "google_access_token": "demo_oauth_token_12345",
            "action": "manual_event",
            "manual_event": {
                "title": "Integration Test Meeting",
                "description": "Testing manual event creation",
                "start_time": "2025-08-22T10:00:00",
                "end_time": "2025-08-22T11:00:00",
                "location": "Virtual"
            },
            "google_api_key": REAL_API_KEYS["google_api_key"]
        }
        
        result = self.test_api_endpoint(
            "AddToCalendar",
            "/agents/addtocalendar/execute",
            payload,
            "Manual Event Creation with Dynamic Google API Key"
        )
        tests.append(result)
        
        return tests

    def run_comprehensive_test(self):
        """Run comprehensive integration test for all agents."""
        
        print("🚀 COMPREHENSIVE API INTEGRATION TEST")
        print("=" * 80)
        print("🎯 Target: 100% SUCCESS with real API functionality")
        print("🔑 Using real API keys from .env passed dynamically")
        print("🎫 Using fresh tokens with extended expiry")
        print("📡 Testing through API server endpoints only")
        print("=" * 80)
        
        # Verify API keys are loaded
        print(f"\n🔍 API Keys Status:")
        for key_name, key_value in REAL_API_KEYS.items():
            status = "✅ LOADED" if key_value else "❌ MISSING"
            masked_key = f"{key_value[:10]}..." if key_value else "None"
            print(f"  {key_name}: {status} ({masked_key})")
        
        # Run all agent tests
        all_results = {}
        
        all_results["ChanduFinance"] = self.test_chandufinance_agent()
        all_results["RelationshipMemory"] = self.test_relationship_memory_agent()
        all_results["MailerPanda"] = self.test_mailerpanda_agent()
        all_results["AddToCalendar"] = self.test_addtocalendar_agent()
        
        # Generate comprehensive report
        self.generate_final_report(all_results)

    def generate_final_report(self, all_results: Dict[str, List[Dict[str, Any]]]):
        """Generate comprehensive final report."""
        
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        total_success = 0
        total_tests = 0
        
        for agent_name, tests in all_results.items():
            agent_success = sum(1 for test in tests if test["success"])
            agent_total = len(tests)
            total_success += agent_success
            total_tests += agent_total
            
            success_rate = (agent_success / agent_total * 100) if agent_total > 0 else 0
            status_icon = "✅" if success_rate == 100 else "⚠️" if success_rate >= 50 else "❌"
            
            print(f"\n{status_icon} {agent_name:20} | {agent_success}/{agent_total} | {success_rate:.1f}%")
            
            for test in tests:
                test_status = "✅" if test["success"] else "❌"
                print(f"    {test_status} {test['test_description']}")
                if not test["success"] and test["error"]:
                    print(f"       🚨 {test['error']}")
        
        overall_success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "-" * 80)
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {total_success}")
        print(f"   Failed: {total_tests - total_success}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        
        if overall_success_rate == 100:
            print("\n🎉 PERFECT SCORE: 100% SUCCESS ACHIEVED!")
            print("✅ All agents working with dynamic API keys")
            print("✅ Full API integration functional")
            print("✅ No hardcoded credentials required")
            print("✅ HushhMCP compliance achieved")
        elif overall_success_rate >= 75:
            print(f"\n🎊 EXCELLENT: {overall_success_rate:.1f}% success rate!")
            print("🔧 Minor issues to address for perfect score")
        elif overall_success_rate >= 50:
            print(f"\n👍 GOOD: {overall_success_rate:.1f}% success rate")
            print("🔧 Some improvements needed")
        else:
            print(f"\n⚠️ NEEDS WORK: {overall_success_rate:.1f}% success rate")
            print("🔧 Significant improvements needed")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = APIIntegrationTester()
    tester.run_comprehensive_test()
