#!/usr/bin/env python3
"""
Test the serialization fix for numpy integers
"""
import requests
import json
import base64

# Create a simple CSV with 3 contacts
csv_content = """name,email,description
John Doe,john@test.com,HR manager looking for new hires
Jane Smith,jane@test.com,Marketing lead interested in newsletters
Bob Wilson,bob@test.com,Sales director focused on customer outreach"""

# Convert to base64
csv_base64 = base64.b64encode(csv_content.encode()).decode()

test_request = {
    "user_id": "test_user_serialization",
    "user_input": "Create a professional email asking about their start date",
    "consent_tokens": {
        "vault.read.email": "test_token_read_email",
        "vault.write.email": "test_token_write_email", 
        "vault.read.file": "test_token_read_file",
        "vault.write.file": "test_token_write_file",
        "custom.temporary": "test_token_temporary"
    },
    "mode": "interactive",
    "require_approval": True,  # This should return awaiting_approval status
    "use_ai_generation": True,
    "use_context_personalization": False,
    "excel_file_data": csv_base64,
    "excel_file_name": "test_contacts.csv"
}

try:
    print("🧪 Testing serialization fix...")
    
    response = requests.post(
        'http://127.0.0.1:8001/agents/mailerpanda/mass-email',
        headers={'Content-Type': 'application/json'},
        json=test_request,
        timeout=30
    )
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Response received and parsed successfully!")
        print(f"   Status: {data.get('status')}")
        print(f"   Campaign ID: {data.get('campaign_id')}")
        print(f"   Total Contacts: {data.get('excel_analysis', {}).get('total_contacts')}")
        print(f"   Contacts with Descriptions: {data.get('excel_analysis', {}).get('contacts_with_descriptions')}")
        print(f"   Requires Approval: {data.get('requires_approval')}")
        
        if data.get('status') == 'awaiting_approval':
            print("✅ Serialization fix working! No more numpy.int64 errors!")
        else:
            print(f"⚠️  Unexpected status: {data.get('status')}")
            
    else:
        print(f"❌ HTTP Error {response.status_code}: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request Exception: {e}")
except json.JSONDecodeError as e:
    print(f"❌ JSON Decode Error: {e}")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
