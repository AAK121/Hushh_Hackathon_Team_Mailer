#!/usr/bin/env python3
"""
Create test Excel file with descriptions and test frontend integration.
"""

import pandas as pd
import base64
import requests
import json

def create_test_excel():
    """Create test Excel file with descriptions."""
    
    contacts_data = {
        'name': ['Alok Kumar', 'Ashok Patel', 'Chandresh Singh'],
        'email': ['alok@example.com', 'ashok@example.com', 'chandresh@example.com'],
        'description': [
            'Tech enthusiast who loves detailed documentation and technical deep-dives. Prefers comprehensive analysis.',
            'Business-focused professional who values concise, actionable insights and quick summaries.',
            'Creative strategist who appreciates innovative approaches and enjoys collaborative discussions.'
        ]
    }
    
    df = pd.DataFrame(contacts_data)
    excel_file = 'test_frontend_contacts.xlsx'
    df.to_excel(excel_file, index=False)
    
    print(f"✅ Created {excel_file} with {len(df)} contacts and descriptions")
    return excel_file

def encode_excel_file(file_path):
    """Encode Excel file to base64 for API request."""
    with open(file_path, 'rb') as f:
        file_data = f.read()
    return base64.b64encode(file_data).decode('utf-8')

def test_frontend_with_real_excel():
    """Test frontend integration with real Excel data and descriptions."""
    
    print("🚀 Testing Frontend AI Personalization with Real Excel Data")
    print("=" * 65)
    
    # Create test Excel file
    excel_file = create_test_excel()
    
    # Encode Excel file
    excel_data = encode_excel_file(excel_file)
    
    # Prepare frontend request with actual Excel data
    frontend_request = {
        "user_id": "frontend_user_123",
        "user_input": "Send a personalized thank you email to all our contacts based on their individual descriptions and background",
        "excel_file_data": excel_data,
        "excel_file_name": "test_frontend_contacts.xlsx",
        "mode": "interactive",
        "use_context_personalization": True,  # ✨ Enable AI personalization
        "personalization_mode": "aggressive",
        "google_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI",
        "mailjet_api_key": "cca56ed08f5272f813370d7fc5a34a24",
        "mailjet_api_secret": "60fb43675233e2ac775f1c6cb8fe455c",
        "consent_tokens": {
            "vault.read.email": "HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQucmVhZC5lbWFpbHwxNzU1OTQ2MzA5NjU0fDE3NTYwMzI3MDk2NTQ=.e98cb6fe90a9d4a6ded5bf2a37b25028d1ea82a7e5dde4223552a312dba75b36",
            "vault.write.email": "HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQud3JpdGUuZW1haWx8MTc1NTk0NjMwOTY1NHwxNzU2MDMyNzA5NjU0.107cf985c5c82413b218a436e8206856b1f982e37a70d6c5ab2fabd97c0ef60e",
            "vault.read.file": "HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQucmVhZC5maWxlfDE3NTU5NDYzMDk2NTR8MTc1NjAzMjcwOTY1NA==.5549616fd68e1a507ff89e18692134c8301d40ec077df18e62b803059ca17642",
            "vault.write.file": "HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQud3JpdGUuZmlsZXwxNzU1OTQ2MzA5NjU1fDE3NTYwMzI3MDk2NTU=.42fe283d1d7e27c05b31ad2b1370aac464e9b15c1a7b4740de335e349b5ee817",
            "custom.temporary": "HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8Y3VzdG9tLnRlbXBvcmFyeXwxNzU1OTQ2MzA5NjU1fDE3NTYwMzI3MDk2NTU=.2c80196d5ae2f4709ee0c4b08531cacd15221bbee1c4a441a7f2b754e291e4d2"
        }
    }
    
    print("🎯 Test Configuration:")
    print(f"  ✅ AI Personalization: {frontend_request['use_context_personalization']}")
    print(f"  🤖 Mode: {frontend_request['personalization_mode']}")
    print(f"  📁 Excel File: {excel_file} (with descriptions)")
    print(f"  👥 Contacts: 3 (all with descriptions)")
    print(f"  📊 Excel Data Size: {len(excel_data)} characters")
    
    print("\n📡 Sending frontend request with real Excel data...")
    
    try:
        url = "http://localhost:8001/agents/mailerpanda/mass-email"
        response = requests.post(url, json=frontend_request, timeout=120)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS! Frontend Integration Working with AI Personalization!")
            print(f"  📊 Status: {result.get('status')}")
            print(f"  🆔 Campaign ID: {result.get('campaign_id')}")
            print(f"  📧 Emails Sent: {result.get('emails_sent', 0)}")
            print(f"  ✨ Context Personalization: {result.get('context_personalization_enabled', False)}")
            print(f"  📝 Recipients Processed: {result.get('recipients_processed', 0)}")
            print(f"  ⏱️ Processing Time: {result.get('processing_time', 0):.2f}s")
            
            if result.get('context_personalization_enabled'):
                print("\n🎉 AI PERSONALIZATION IS ACTIVE!")
                print("📧 The agent is customizing emails based on descriptions!")
                
                # Show Excel analysis
                if result.get('excel_analysis'):
                    analysis = result['excel_analysis']
                    print(f"\n📊 Excel Analysis:")
                    print(f"  📁 File Uploaded: {analysis.get('file_uploaded', False)}")
                    print(f"  👥 Total Contacts: {analysis.get('total_contacts', 0)}")
                    print(f"  📝 Description Column: {analysis.get('description_column_exists', False)}")
                    print(f"  ✨ Contacts with Descriptions: {analysis.get('contacts_with_descriptions', 0)}")
                    print(f"  🎛️ Context Toggle: {analysis.get('context_toggle_status', 'N/A')}")
                    
            else:
                print("\n❌ AI Personalization not activated!")
                print("💡 Check if description column was detected in Excel file")
                
            if result.get('requires_approval'):
                print("\n✅ Campaign ready for approval via frontend")
                
                # Show the generated template
                if result.get('email_template'):
                    template = result['email_template']
                    print(f"\n📧 Generated Template:")
                    print(f"  Subject: {template.get('subject', 'N/A')}")
                    body_preview = template.get('body', 'N/A')
                    if len(body_preview) > 300:
                        body_preview = body_preview[:300] + "..."
                    print(f"  Body: {body_preview}")
                    
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_frontend_with_real_excel()
