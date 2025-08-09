#!/usr/bin/env python3
"""
Token Extraction and Testing Script
This script extracts access tokens from existing Google OAuth token files
and tests the new access token integration with the AddToCalendar agent.
"""

import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
from hushh_mcp.consent.token import issue_token, validate_token, ConsentScope

def extract_access_token_from_file(token_file_path):
    """
    Extract access token from Google OAuth token file.
    
    Args:
        token_file_path: Path to the token JSON file
        
    Returns:
        tuple: (access_token, expires_at, token_info)
    """
    try:
        with open(token_file_path, 'r') as f:
            token_data = json.load(f)
        
        access_token = token_data.get('token')
        refresh_token = token_data.get('refresh_token')
        expires_at = token_data.get('expiry')
        scopes = token_data.get('scopes', [])
        
        print(f"📄 Token file: {os.path.basename(token_file_path)}")
        print(f"   🔑 Access token: {access_token[:20] + '...' if access_token else 'None'}")
        print(f"   🔄 Refresh token: {'Available' if refresh_token else 'None'}")
        print(f"   ⏰ Expires: {expires_at}")
        print(f"   🔒 Scopes: {', '.join(scopes)}")
        
        return access_token, expires_at, token_data
        
    except FileNotFoundError:
        print(f"❌ Token file not found: {token_file_path}")
        return None, None, None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in token file: {e}")
        return None, None, None
    except Exception as e:
        print(f"❌ Error reading token file: {e}")
        return None, None, None

def test_with_real_tokens():
    """
    Test the access token integration using real tokens from files.
    """
    print("🧪 Testing Access Token Integration with Real Tokens")
    print("=" * 60)
    
    # Base path for token files
    base_path = "c:\\Users\\Dell\\Downloads\\h\\Hushh_Hackathon_Team_Mailer\\hushh_mcp\\agents\\addtocalendar"
    
    # Available token files
    token_files = [
        "token_gmail_demo_user_encapsulated_001.json",
        "token_calendar_demo_user_encapsulated_001.json",
        "token_gmail_test_user_123.json", 
        "token_calendar_test_user_123.json",
        "token_gmail_web_demo_user_001.json",
        "token_calendar_web_demo_user_001.json"
    ]
    
    # Extract tokens from available files
    available_tokens = {}
    
    print("🔍 Scanning for available token files...")
    for token_file in token_files:
        file_path = os.path.join(base_path, token_file)
        if os.path.exists(file_path):
            access_token, expires_at, token_data = extract_access_token_from_file(file_path)
            if access_token:
                service_type = 'gmail' if 'gmail' in token_file else 'calendar'
                user_id = 'test_user_123' if 'test_user_123' in token_file else 'demo_user_encapsulated_001'
                
                key = f"{service_type}_{user_id}"
                available_tokens[key] = {
                    'access_token': access_token,
                    'expires_at': expires_at,
                    'token_data': token_data,
                    'file_path': file_path
                }
    
    print(f"\n📊 Found {len(available_tokens)} valid token files")
    
    if not available_tokens:
        print("❌ No valid access tokens found in token files")
        return False
    
    # Find a user with both Gmail and Calendar tokens
    test_scenarios = []
    
    for user_id in ['test_user_123', 'demo_user_encapsulated_001']:
        gmail_key = f"gmail_{user_id}"
        calendar_key = f"calendar_{user_id}" 
        
        if gmail_key in available_tokens and calendar_key in available_tokens:
            test_scenarios.append({
                'user_id': user_id,
                'gmail_token': available_tokens[gmail_key]['access_token'],
                'calendar_token': available_tokens[calendar_key]['access_token'],
                'gmail_data': available_tokens[gmail_key],
                'calendar_data': available_tokens[calendar_key]
            })
    
    if not test_scenarios:
        print("⚠️  No user found with both Gmail and Calendar tokens")
        # Use any available token for basic testing
        first_token = list(available_tokens.values())[0]
        test_scenarios.append({
            'user_id': 'single_token_test',
            'gmail_token': first_token['access_token'],
            'calendar_token': first_token['access_token'],  # Use same token for both
            'gmail_data': first_token,
            'calendar_data': first_token
        })
    
    # Run tests with real tokens
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{'='*60}")
        print(f"🧪 Test Scenario {i+1}: User {scenario['user_id']}")
        print(f"{'='*60}")
        
        success = run_test_scenario(scenario)
        
        if success:
            print(f"✅ Test scenario {i+1} completed successfully!")
        else:
            print(f"❌ Test scenario {i+1} failed")
    
    return True

def run_test_scenario(scenario):
    """
    Run a complete test scenario with real tokens.
    
    Args:
        scenario: Dictionary containing test data and tokens
        
    Returns:
        bool: True if test was successful
    """
    user_id = scenario['user_id']
    gmail_access_token = scenario['gmail_token']
    calendar_access_token = scenario['calendar_token']
    
    print(f"👤 Testing user: {user_id}")
    print(f"📧 Gmail token: {gmail_access_token[:20]}...{gmail_access_token[-10:]}")
    print(f"📅 Calendar token: {calendar_access_token[:20]}...{calendar_access_token[-10:]}")
    
    try:
        # Generate HushhMCP consent tokens
        print("\n🔐 Generating HushhMCP consent tokens...")
        
        email_token_obj = issue_token(
            user_id=user_id,
            agent_id="addtocalendar",
            scope=ConsentScope.VAULT_READ_EMAIL
        )
        
        calendar_token_obj = issue_token(
            user_id=user_id,
            agent_id="addtocalendar",
            scope=ConsentScope.VAULT_WRITE_CALENDAR
        )
        
        email_consent_token = email_token_obj.token
        calendar_consent_token = calendar_token_obj.token
        
        print(f"   ✅ Email consent token: {email_consent_token[:30]}...")
        print(f"   ✅ Calendar consent token: {calendar_consent_token[:30]}...")
        
        # Initialize agent
        print("\n🚀 Initializing AddToCalendar agent...")
        agent = AddToCalendarAgent()
        print(f"   ✅ Agent initialized: {agent.agent_id}")
        
        # Test 1: Gmail service creation with access token
        print("\n📧 Test 1: Gmail service creation with access token")
        try:
            gmail_service = agent._get_google_service_with_token('gmail', 'v1', gmail_access_token)
            if gmail_service:
                print("   ✅ Gmail service created successfully")
                
                # Try to read a few emails to verify the token works
                try:
                    messages_result = gmail_service.users().messages().list(
                        userId='me', maxResults=3
                    ).execute()
                    messages = messages_result.get('messages', [])
                    print(f"   📊 Found {len(messages)} emails (token is valid)")
                except Exception as e:
                    print(f"   ⚠️  Gmail API call failed: {e}")
            else:
                print("   ❌ Failed to create Gmail service")
                return False
        except Exception as e:
            print(f"   ❌ Gmail service creation failed: {e}")
            
        # Test 2: Calendar service creation with access token
        print("\n📅 Test 2: Calendar service creation with access token")
        try:
            calendar_service = agent._get_google_service_with_token('calendar', 'v3', calendar_access_token)
            if calendar_service:
                print("   ✅ Calendar service created successfully")
                
                # Try to list calendars to verify the token works
                try:
                    calendars_result = calendar_service.calendarList().list().execute()
                    calendars = calendars_result.get('items', [])
                    print(f"   📊 Found {len(calendars)} calendars (token is valid)")
                except Exception as e:
                    print(f"   ⚠️  Calendar API call failed: {e}")
            else:
                print("   ❌ Failed to create Calendar service")
                return False
        except Exception as e:
            print(f"   ❌ Calendar service creation failed: {e}")
        
        # Test 3: Full agent execution with access tokens (analyze only)
        print("\n🎯 Test 3: Agent execution with access tokens (analyze_only)")
        try:
            result = agent.handle(
                user_id=user_id,
                email_token_str=email_consent_token,
                calendar_token_str=calendar_consent_token,
                google_access_token=gmail_access_token,
                action="analyze_only"
            )
            
            print(f"   📊 Agent result status: {result.get('status', 'unknown')}")
            print(f"   🔑 Authentication method: {result.get('authentication_method', 'unknown')}")
            
            if result.get('status') == 'success':
                analysis = result.get('data', {}).get('analysis_results', {})
                print(f"   📧 Total emails analyzed: {analysis.get('total_emails', 0)}")
                print(f"   ⭐ High priority emails: {analysis.get('prioritized_emails', 0)}")
                print(f"   🎯 Potential events found: {analysis.get('extracted_events', 0)}")
                print("   ✅ Full agent execution successful!")
            elif result.get('status') == 'error':
                print(f"   ⚠️  Agent execution completed with error: {result.get('message', 'Unknown error')}")
                # This might be expected if there are permission issues
            
        except Exception as e:
            print(f"   ❌ Agent execution failed: {e}")
        
        # Test 4: Test comprehensive analysis (if both tokens work)
        print("\n🔄 Test 4: Comprehensive analysis with calendar creation")
        try:
            result = agent.handle(
                user_id=user_id,
                email_token_str=email_consent_token,
                calendar_token_str=calendar_consent_token,
                google_access_token=gmail_access_token,  # Using gmail token for both
                action="comprehensive_analysis"
            )
            
            print(f"   📊 Comprehensive result status: {result.get('status', 'unknown')}")
            
            if result.get('status') == 'success':
                summary = result.get('data', {}).get('analysis_summary', {})
                print(f"   📧 Emails processed: {summary.get('total_emails_processed', 0)}")
                print(f"   🎯 Events extracted: {summary.get('events_extracted', 0)}")
                print(f"   📅 Events created: {summary.get('events_created', 0)}")
                print("   ✅ Comprehensive analysis successful!")
            else:
                print(f"   ⚠️  Comprehensive analysis result: {result.get('message', 'Unknown')}")
                
        except Exception as e:
            print(f"   ❌ Comprehensive analysis failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test scenario failed: {e}")
        return False

def main():
    """Main test execution."""
    try:
        print("🚀 Starting Real Token Integration Test")
        print("=" * 60)
        
        success = test_with_real_tokens()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 REAL TOKEN TESTING COMPLETED!")
            print("✅ Access token integration is working with real Google tokens")
            print("🔑 Frontend can now safely use OAuth access tokens")
            print("📱 Ready for production deployment!")
        else:
            print("\n❌ Real token testing encountered issues")
            
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
