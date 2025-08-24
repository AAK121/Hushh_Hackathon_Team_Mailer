#!/usr/bin/env python3
"""Test MailerPanda complete workflow"""

import requests
import json

def test_mailerpanda_workflow():
    print("🎯 Testing complete MailerPanda workflow...")
    
    # 1. Create campaign
    print("\n1. Creating campaign...")
    r1 = requests.post('http://127.0.0.1:8001/agents/mailerpanda/mass-email', json={
        'user_id': 'test_user',
        'user_input': 'Send a welcome email to new customers',
        'mode': 'interactive',
        'consent_tokens': {},
        'excel_file_data': '',
        'use_context_personalization': False
    })
    
    result1 = r1.json()
    print(f"   Status: {result1.get('status')}")
    print(f"   Campaign ID: {result1.get('campaign_id')}")
    
    email_template = result1.get('email_template', {})
    if email_template:
        print(f"   Subject: {email_template.get('subject')}")
        print(f"   Body preview: {email_template.get('body', '')[:100]}...")
    
    campaign_id = result1.get('campaign_id')
    
    if not campaign_id:
        print("❌ Failed to create campaign")
        return
    
    # 2. Test approval
    print("\n2. Testing approval...")
    r2 = requests.post('http://127.0.0.1:8001/agents/mailerpanda/mass-email/approve', json={
        'user_id': 'test_user',
        'campaign_id': campaign_id,
        'action': 'approve'
    })
    
    result2 = r2.json()
    print(f"   Approval Status: {result2.get('status')}")
    
    # 3. Test suggestion workflow
    print("\n3. Testing suggestion workflow...")
    r3 = requests.post('http://127.0.0.1:8001/agents/mailerpanda/mass-email/approve', json={
        'user_id': 'test_user',
        'campaign_id': campaign_id,
        'action': 'modify',
        'feedback': 'Make the tone more casual and friendly'
    })
    
    result3 = r3.json()
    print(f"   Suggestion Status: {result3.get('status')}")
    
    print("\n✅ MailerPanda workflow test complete!")
    print("\nFull Results:")
    print(f"1. Campaign Creation: {json.dumps(result1, indent=2)[:300]}...")
    print(f"2. Approval: {json.dumps(result2, indent=2)[:200]}...")
    print(f"3. Suggestion: {json.dumps(result3, indent=2)[:200]}...")

if __name__ == "__main__":
    test_mailerpanda_workflow()

