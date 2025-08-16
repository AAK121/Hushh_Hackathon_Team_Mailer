#!/usr/bin/env python3
"""
Comprehensive HushhMCP Agents Function Testing
Tests all available functions for each of the 4 agents
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta

def test_comprehensive_agents():
    """Test all functions of all agents comprehensively"""
    
    print("🚀 HushhMCP Agents Comprehensive Function Testing")
    print("=" * 70)
    
    # Server connectivity check
    try:
        response = requests.get('http://127.0.0.1:8002/health', timeout=10)
        if response.status_code == 200:
            print("✅ API Server is running")
        else:
            print("❌ API Server not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        return False
    
    # Get all agents
    try:
        agents_response = requests.get('http://127.0.0.1:8002/agents', timeout=10)
        agents_data = agents_response.json()
        print(f"✅ Found {agents_data['total_agents']} agents available")
        print()
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return False
    
    # Test counters
    total_tests = 0
    passed_tests = 0
    
    # 1. COMPREHENSIVE CHANDUFINANCE TESTING
    print("📊 TESTING CHANDUFINANCE AGENT - Financial Analysis Functions")
    print("-" * 60)
    
    finance_tests = [
        {
            "name": "Stock Financial Data Retrieval",
            "payload": {
                "user_id": "test_user_123",
                "token": "test_token_123",
                "ticker": "AAPL",
                "command": "get_financials"
            }
        },
        {
            "name": "Market Analysis",
            "payload": {
                "user_id": "test_user_123", 
                "token": "test_token_123",
                "ticker": "GOOGL",
                "command": "market_analysis"
            }
        },
        {
            "name": "DCF Valuation Analysis",
            "payload": {
                "user_id": "test_user_123",
                "token": "test_token_123", 
                "ticker": "MSFT",
                "command": "run_valuation"
            }
        },
        {
            "name": "Sensitivity Analysis",
            "payload": {
                "user_id": "test_user_123",
                "token": "test_token_123", 
                "ticker": "TSLA",
                "command": "run_sensitivity"
            }
        }
    ]
    
    for test in finance_tests:
        total_tests += 1
        try:
            response = requests.post('http://127.0.0.1:8002/agents/chandufinance/execute', 
                                   json=test["payload"], timeout=15)
            result = response.json()
            if result.get('status') == 'success':
                print(f"✅ {test['name']}: SUCCESS")
                passed_tests += 1
            else:
                print(f"❌ {test['name']}: {result.get('status', 'FAILED')}")
        except Exception as e:
            print(f"❌ {test['name']}: ERROR - {e}")
    
    print()
    
    # 2. COMPREHENSIVE RELATIONSHIP MEMORY TESTING
    print("🧠 TESTING RELATIONSHIP MEMORY AGENT - All Memory Functions")
    print("-" * 60)
    
    memory_tests = [
        {
            "name": "Add Contact Function",
            "payload": {
                'user_id': 'test_user_123',
                'tokens': {'vault.read.contacts': 'test_token_123', 'vault.write.contacts': 'test_token_456'},
                'user_input': 'Add contact John Doe with email john@example.com and phone 555-1234'
            }
        },
        {
            "name": "Add Memory Function", 
            "payload": {
                'user_id': 'test_user_123',
                'tokens': {'vault.read.contacts': 'test_token_123', 'vault.write.contacts': 'test_token_456'},
                'user_input': 'Remember that Sarah loves hiking and prefers weekend activities'
            }
        },
        {
            "name": "Add Reminder Function",
            "payload": {
                'user_id': 'test_user_123', 
                'tokens': {'vault.read.contacts': 'test_token_123', 'vault.write.contacts': 'test_token_456'},
                'user_input': 'Remind me to call Mom on her birthday next month'
            }
        },
        {
            "name": "Show Contacts Function",
            "payload": {
                'user_id': 'test_user_123',
                'tokens': {'vault.read.contacts': 'test_token_123', 'vault.write.contacts': 'test_token_456'},
                'user_input': 'Show me all my contacts'
            }
        },
        {
            "name": "Search Contacts Function",
            "payload": {
                'user_id': 'test_user_123',
                'tokens': {'vault.read.contacts': 'test_token_123', 'vault.write.contacts': 'test_token_456'},
                'user_input': 'Find contact John'
            }
        },
        {
            "name": "Show Memories Function",
            "payload": {
                'user_id': 'test_user_123',
                'tokens': {'vault.read.contacts': 'test_token_123', 'vault.write.contacts': 'test_token_456'},
                'user_input': 'Show my memories about Sarah'
            }
        },
        {
            "name": "Show Reminders Function",
            "payload": {
                'user_id': 'test_user_123',
                'tokens': {'vault.read.contacts': 'test_token_123', 'vault.write.contacts': 'test_token_456'},
                'user_input': 'Show my upcoming reminders'
            }
        },
        {
            "name": "Get Relationship Advice",
            "payload": {
                'user_id': 'test_user_123',
                'tokens': {'vault.read.contacts': 'test_token_123', 'vault.write.contacts': 'test_token_456'},
                'user_input': 'What should I get Jane for her birthday?'
            }
        }
    ]
    
    for test in memory_tests:
        total_tests += 1
        try:
            response = requests.post('http://127.0.0.1:8002/agents/relationship_memory/execute',
                                   json=test["payload"], timeout=20)
            result = response.json()
            if result.get('status') == 'success':
                print(f"✅ {test['name']}: SUCCESS")
                passed_tests += 1
            else:
                print(f"❌ {test['name']}: {result.get('status', 'FAILED')}")
        except Exception as e:
            print(f"❌ {test['name']}: ERROR - {e}")
    
    print()
    
    # 3. COMPREHENSIVE ADDTOCALENDAR TESTING  
    print("📅 TESTING ADDTOCALENDAR AGENT - Email & Calendar Functions")
    print("-" * 60)
    
    calendar_tests = [
        {
            "name": "Email Analysis Only",
            "payload": {
                "user_id": "test_user_123",
                "email_token": "test_email_token_123",
                "calendar_token": "test_calendar_token_456", 
                "google_access_token": "test_google_token_789",
                "action": "analyze_only",
                "max_emails": 10,
                "confidence_threshold": 0.7
            }
        },
        {
            "name": "Comprehensive Email Analysis",
            "payload": {
                "user_id": "test_user_123",
                "email_token": "test_email_token_123",
                "calendar_token": "test_calendar_token_456",
                "google_access_token": "test_google_token_789", 
                "action": "comprehensive_analysis",
                "max_emails": 15,
                "confidence_threshold": 0.6
            }
        },
        {
            "name": "Manual Event Addition",
            "payload": {
                "user_id": "test_user_123",
                "email_token": "test_email_token_123", 
                "calendar_token": "test_calendar_token_456",
                "google_access_token": "test_google_token_789",
                "action": "manual_event",
                "manual_event": {
                    "title": "Team Meeting",
                    "description": "Weekly team sync",
                    "start_time": "2025-08-20T10:00:00",
                    "end_time": "2025-08-20T11:00:00",
                    "location": "Conference Room A"
                }
            }
        }
    ]
    
    for test in calendar_tests:
        total_tests += 1
        try:
            response = requests.post('http://127.0.0.1:8002/agents/addtocalendar/execute',
                                   json=test["payload"], timeout=25)
            result = response.json()
            if result.get('status') == 'success':
                print(f"✅ {test['name']}: SUCCESS")
                passed_tests += 1
            else:
                print(f"❌ {test['name']}: {result.get('status', 'FAILED')}")
        except Exception as e:
            print(f"❌ {test['name']}: ERROR - {e}")
    
    print()
    
    # 4. COMPREHENSIVE MAILERPANDA TESTING
    print("📧 TESTING MAILERPANDA AGENT - Email Campaign Functions")
    print("-" * 60)
    
    mailer_tests = [
        {
            "name": "Create Demo Campaign",
            "payload": {
                "user_id": "test_user_123",
                "consent_tokens": {
                    "vault.read.email": "test_token_123",
                    "vault.write.email": "test_token_456"
                },
                "user_input": "Create a demo email campaign for product launch",
                "mode": "demo",
                "sender_email": "demo@example.com"
            }
        },
        {
            "name": "Interactive Newsletter Campaign",
            "payload": {
                "user_id": "test_user_123",
                "consent_tokens": {
                    "vault.read.email": "test_token_123", 
                    "vault.write.email": "test_token_456"
                },
                "user_input": "Create a monthly newsletter campaign",
                "mode": "interactive",
                "sender_email": "newsletter@company.com"
            }
        },
        {
            "name": "Headless Campaign Generation",
            "payload": {
                "user_id": "test_user_123",
                "consent_tokens": {
                    "vault.read.email": "test_token_123",
                    "vault.write.email": "test_token_456"
                },
                "user_input": "Generate automated promotional email",
                "mode": "headless",
                "sender_email": "auto@company.com"
            }
        },
        {
            "name": "Event Invitation Campaign",
            "payload": {
                "user_id": "test_user_123",
                "consent_tokens": {
                    "vault.read.email": "test_token_123",
                    "vault.write.email": "test_token_456"
                },
                "user_input": "Create invitation email for company annual meeting",
                "mode": "demo",
                "sender_email": "events@company.com"
            }
        },
        {
            "name": "Welcome Series Campaign",
            "payload": {
                "user_id": "test_user_123",
                "consent_tokens": {
                    "vault.read.email": "test_token_123",
                    "vault.write.email": "test_token_456"
                },
                "user_input": "Create welcome email series for new customers",
                "mode": "demo",
                "sender_email": "welcome@company.com"
            }
        }
    ]
    
    for test in mailer_tests:
        total_tests += 1
        try:
            response = requests.post('http://127.0.0.1:8002/agents/mailerpanda/execute',
                                   json=test["payload"], timeout=20)
            result = response.json()
            if result.get('status') in ['success', 'completed']:
                print(f"✅ {test['name']}: SUCCESS")
                passed_tests += 1
            else:
                print(f"❌ {test['name']}: {result.get('status', 'FAILED')}")
        except Exception as e:
            print(f"❌ {test['name']}: ERROR - {e}")
    
    print()
    print("🎯 COMPREHENSIVE TESTING SUMMARY")
    print("=" * 70)
    print(f"📊 Total Function Tests: {total_tests}")
    print(f"✅ Passed Tests: {passed_tests}")
    print(f"❌ Failed Tests: {total_tests - passed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 PERFECT! All agent functions working at 100%!")
    elif passed_tests >= total_tests * 0.9:
        print("🎊 EXCELLENT! Outstanding success rate achieved!")
    elif passed_tests >= total_tests * 0.8:
        print("🎊 EXCELLENT! High success rate achieved!")
    elif passed_tests >= total_tests * 0.6:
        print("👍 GOOD! Majority of functions working!")
    else:
        print("⚠️ NEEDS WORK! Several functions need debugging!")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Set UTF-8 encoding for Windows
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    
    test_comprehensive_agents()
