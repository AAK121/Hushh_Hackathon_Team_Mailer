#!/usr/bin/env python3
"""
Demo script for the Enhanced AddToCalendar Agent
Shows advanced email analysis, AI prioritization, and manual event creation.
"""

import json
import requests
import time
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://127.0.0.1:8001"
USER_ID = "demo_user_enhanced"

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print(f"{'─'*40}")

def demo_comprehensive_analysis():
    """Demo: Comprehensive email analysis with AI prioritization and calendar integration."""
    print_header("Enhanced AddToCalendar Agent Demo")
    
    # Step 1: Generate consent tokens
    print_section("Step 1: Generating Consent Tokens")
    
    # Email consent token
    email_consent_data = {
        "user_id": USER_ID,
        "scope": "VAULT_READ_EMAIL",
        "purpose": "Enhanced email analysis and event extraction",
        "duration_hours": 1
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/consent/token", json=email_consent_data)
        email_token = response.json()["token"]
        print(f"✅ Email consent token generated: {email_token[:20]}...")
    except Exception as e:
        print(f"❌ Failed to generate email token: {e}")
        return
    
    # Calendar consent token
    calendar_consent_data = {
        "user_id": USER_ID,
        "scope": "VAULT_WRITE_CALENDAR",
        "purpose": "AI-powered calendar event creation",
        "duration_hours": 1
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/consent/token", json=calendar_consent_data)
        calendar_token = response.json()["token"]
        print(f"✅ Calendar consent token generated: {calendar_token[:20]}...")
    except Exception as e:
        print(f"❌ Failed to generate calendar token: {e}")
        return
    
    # Step 2: Execute comprehensive analysis
    print_section("Step 2: Running Comprehensive Email Analysis")
    
    agent_request = {
        "agent_id": "addtocalendar",
        "user_id": USER_ID,
        "parameters": {
            "action": "comprehensive_analysis"
        },
        "consent_tokens": {
            "email_token": email_token,
            "calendar_token": calendar_token
        }
    }
    
    try:
        print("🔄 Starting comprehensive email analysis...")
        response = requests.post(f"{API_BASE_URL}/agents/addtocalendar/execute", json=agent_request)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis completed successfully!")
            
            # Display results
            analysis_data = result.get('data', {})
            
            if 'analysis_summary' in analysis_data:
                summary = analysis_data['analysis_summary']
                print(f"\n📊 Analysis Summary:")
                print(f"   • Total emails processed: {summary.get('total_emails_processed', 0)}")
                print(f"   • High priority emails: {summary.get('high_priority_emails', 0)}")
                print(f"   • Events extracted: {summary.get('events_extracted', 0)}")
                print(f"   • Events created: {summary.get('events_created', 0)}")
                print(f"   • Processing time: {analysis_data.get('processing_time', 0)}s")
            
            # Show email categories
            if 'analysis_summary' in analysis_data and 'email_categories' in analysis_data['analysis_summary']:
                categories = analysis_data['analysis_summary']['email_categories']
                print(f"\n🏷️  Email Categories:")
                for category, count in categories.items():
                    print(f"   • {category.title()}: {count} emails")
            
            # Show top extracted events
            if 'data' in analysis_data and 'extracted_events' in analysis_data['data']:
                events = analysis_data['data']['extracted_events']
                if events:
                    print(f"\n🎯 Top Extracted Events:")
                    for i, event in enumerate(events[:3], 1):
                        confidence = event.get('confidence_score', 0)
                        print(f"   {i}. {event.get('summary', 'Unknown Event')}")
                        print(f"      📅 {event.get('start_time')} - {event.get('end_time')}")
                        print(f"      🎯 Confidence: {confidence:.2f}")
                        if event.get('location'):
                            print(f"      📍 Location: {event.get('location')}")
            
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def demo_manual_event():
    """Demo: Manual event creation with AI assistance."""
    print_section("Step 3: Creating Manual Event with AI Assistance")
    
    # Generate calendar consent token
    calendar_consent_data = {
        "user_id": USER_ID,
        "scope": "VAULT_WRITE_CALENDAR", 
        "purpose": "Manual AI-assisted event creation",
        "duration_hours": 1
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/consent/token", json=calendar_consent_data)
        calendar_token = response.json()["token"]
        print(f"✅ Calendar token for manual event: {calendar_token[:20]}...")
    except Exception as e:
        print(f"❌ Failed to generate calendar token: {e}")
        return
    
    # Create manual event
    event_descriptions = [
        "Team retrospective meeting next Friday at 3 PM for 2 hours",
        "Doctor appointment tomorrow at 10 AM",
        "Lunch with John next Tuesday at noon"
    ]
    
    for i, description in enumerate(event_descriptions, 1):
        print(f"\n🎨 Creating manual event {i}: {description}")
        
        agent_request = {
            "agent_id": "addtocalendar",
            "user_id": USER_ID,
            "parameters": {
                "action": "manual_event",
                "event_description": description,
                "add_to_calendar": True  # Actually create in calendar
            },
            "consent_tokens": {
                "calendar_token": calendar_token
            }
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/agents/addtocalendar/execute", json=agent_request)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'success':
                    manual_event = result['data'].get('manual_event', {})
                    event_data = manual_event.get('event', {})
                    ai_suggestions = manual_event.get('ai_suggestions', {})
                    
                    print(f"   ✅ Event created: {event_data.get('summary', 'Unknown')}")
                    print(f"   📅 Time: {event_data.get('start_time')} - {event_data.get('end_time')}")
                    print(f"   🤖 AI Confidence: {ai_suggestions.get('confidence', 0):.2f}")
                    
                    if ai_suggestions.get('suggestions'):
                        print(f"   💡 AI Suggestions: {', '.join(ai_suggestions['suggestions'])}")
                else:
                    print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between requests
        time.sleep(1)

def demo_analyze_only():
    """Demo: Email analysis without calendar creation."""
    print_section("Step 4: Analysis-Only Mode (No Calendar Creation)")
    
    # Generate email consent token
    email_consent_data = {
        "user_id": USER_ID,
        "scope": "VAULT_READ_EMAIL",
        "purpose": "Email analysis only without calendar creation",
        "duration_hours": 1
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/consent/token", json=email_consent_data)
        email_token = response.json()["token"]
        print(f"✅ Email token for analysis: {email_token[:20]}...")
    except Exception as e:
        print(f"❌ Failed to generate email token: {e}")
        return
    
    # Execute analysis-only
    agent_request = {
        "agent_id": "addtocalendar",
        "user_id": USER_ID,
        "parameters": {
            "action": "analyze_only"
        },
        "consent_tokens": {
            "email_token": email_token
        }
    }
    
    try:
        print("🔍 Running analysis-only mode...")
        response = requests.post(f"{API_BASE_URL}/agents/addtocalendar/execute", json=agent_request)
        
        if response.status_code == 200:
            result = response.json()
            analysis_results = result['data'].get('analysis_results', {})
            
            print("✅ Analysis completed!")
            print(f"   📧 Total emails: {analysis_results.get('total_emails', 0)}")
            print(f"   ⭐ High priority: {analysis_results.get('prioritized_emails', 0)}")  
            print(f"   🎯 Potential events: {analysis_results.get('extracted_events', 0)}")
            
            # Show potential events
            potential_events = result['data'].get('data', {}).get('potential_events', [])
            if potential_events:
                print(f"\n🎯 Potential Events Found:")
                for i, event in enumerate(potential_events[:3], 1):
                    print(f"   {i}. {event.get('summary', 'Unknown Event')}")
                    print(f"      🎯 Confidence: {event.get('confidence_score', 0):.2f}")
                    
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main demo execution."""
    print_header("Enhanced AddToCalendar Agent Demonstration")
    print("🎯 Showcasing AI-powered email analysis and calendar integration")
    
    # Check if API server is running
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Server Status: {health_data.get('status', 'unknown')}")
            print(f"🤖 Available Agents: {health_data.get('agents_available', 0)}")
        else:
            print("❌ API server not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API server at {API_BASE_URL}")
        print(f"   Error: {e}")
        print("   Please start the API server first: python api.py")
        return
    
    # Run demos
    demo_comprehensive_analysis()
    demo_manual_event()
    demo_analyze_only()
    
    print_header("Demo Complete!")
    print("🎉 Enhanced AddToCalendar Agent demonstration finished successfully!")
    print("\n📋 Features demonstrated:")
    print("   • AI-powered email prioritization (1-10 scale)")
    print("   • Smart email categorization (work, personal, events, etc.)")
    print("   • Enhanced event extraction with confidence scoring")
    print("   • Manual event creation with AI assistance")
    print("   • HushMCP consent token validation")
    print("   • Secure vault storage for event data")
    print("   • Multiple execution modes (comprehensive, manual, analyze-only)")

if __name__ == "__main__":
    main()
