#!/usr/bin/env python3
"""
Simple test to debug email sending issues.
"""

import requests
import json

def simple_debug_test():
    """Simple debug test."""
    
    print("🔍 Debug Test - No Excel File")
    print("=" * 40)
    
    # Simple test without Excel file
    test_request = {
        "user_id": "debug_user",
        "consent_tokens": {
            "vault.read.email": "test_token_1",
            "vault.write.email": "test_token_2", 
            "vault.read.file": "test_token_3",
            "vault.write.file": "test_token_4",
            "custom.temporary": "test_token_5"
        },
        "user_input": "Send a simple debug email",
        "mode": "interactive",
        "use_context_personalization": False,
        "personalization_mode": "conservative"
    }
    
    try:
        print("📤 Sending debug request...")
        response = requests.post(
            "http://localhost:8001/agents/mailerpanda/mass-email",
            json=test_request,
            timeout=60
        )
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response received:")
            print(f"  Status: {result.get('status')}")
            print(f"  Campaign ID: {result.get('campaign_id')}")
            print(f"  Emails Sent: {result.get('emails_sent', 0)}")
            print(f"  Context Enabled: {result.get('context_personalization_enabled', False)}")
            
            # Show Excel analysis
            excel_analysis = result.get('excel_analysis', {})
            print(f"  Excel Analysis:")
            print(f"    File Uploaded: {excel_analysis.get('file_uploaded', False)}")
            print(f"    Total Contacts: {excel_analysis.get('total_contacts', 0)}")
            print(f"    Context Toggle: {excel_analysis.get('context_toggle_status', 'N/A')}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error Details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    simple_debug_test()
