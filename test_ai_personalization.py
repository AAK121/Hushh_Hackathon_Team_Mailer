#!/usr/bin/env python3
"""
Test the AI-powered description-based personalization in MailerPanda.
This test specifically demonstrates how the agent uses descriptions to create personalized emails.
"""

import requests
import json

def test_ai_personalization():
    """Test AI-powered personalization using contact descriptions."""
    
    print("🤖 Testing AI-Powered Email Personalization")
    print("=" * 60)
    
    # Test data with personalization ENABLED
    test_data = {
        "user_id": "test_ai_personalization",
        "consent_tokens": {
            "content_generation": "test_token_content_ai",
            "email_sending": "test_token_email_ai", 
            "contact_management": "test_token_contacts_ai"
        },
        "user_input": "Send a personalized appreciation email using the context about each contact",
        "mode": "headless",
        "frontend_approved": True,
        "send_approved": True,
        # ✨ KEY: Enable AI personalization
        "enable_description_personalization": True,
        "personalization_mode": "smart",
        # ✨ Use the Excel file with descriptions
        "excel_file_path": r"c:\Users\Asus\Desktop\Pda_mailer\hushh_mcp\agents\mailerpanda\email_list_with_descriptions.xlsx",
        # ✨ Pre-approved template that will be CUSTOMIZED by AI
        "pre_approved_template": """Dear {name},

I hope this email finds you well. I wanted to reach out to express my appreciation for your partnership with us.

Thank you for your continued trust and collaboration.

Best regards,
The MailerPanda Team""",
        "pre_approved_subject": "Thank you for your partnership, {name}!"
    }
    
    print("🎯 Test Configuration:")
    print(f"  ✅ AI Personalization: {test_data['enable_description_personalization']}")
    print(f"  📁 Excel File: Uses descriptions")
    print(f"  🤖 Mode: {test_data['personalization_mode']}")
    print(f"  📧 Base Template: Generic appreciation message")
    
    print("\n📝 Expected Behavior:")
    print("  For Alok: Should mention technical details/documentation")
    print("  For Ashok: Should mention gentle introduction/support")  
    print("  For Chandresh: Should be brief and business-focused")
    
    print("\n📤 Sending API request...")
    
    try:
        url = "http://localhost:8001/agents/mailerpanda/execute"
        response = requests.post(url, json=test_data, timeout=120)  # Longer timeout for AI processing
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Response Summary:")
            print(f"  📊 Status: {result.get('status')}")
            print(f"  📧 Emails Sent: {result.get('emails_sent', 0)}")
            print(f"  ✨ Personalized Count: {result.get('personalized_count', 0)}")
            print(f"  📝 Standard Count: {result.get('standard_count', 0)}")
            print(f"  📋 Description Column Detected: {result.get('description_column_detected', False)}")
            print(f"  ⏱️ Processing Time: {result.get('processing_time', 0):.2f}s")
            
            if result.get('personalized_count', 0) > 0:
                print("\n🎉 SUCCESS! AI Personalization is working!")
                print("📧 The following emails should have been personalized:")
                print("  📧 Alok (alokkale121@gmail.com) - Technical details focus")
                print("  📧 Ashok (kaleashok92@gmail.com) - Gentle introduction focus")
                print("  📧 Chandresh (chandresht149@gmail.com) - Brief business focus")
                
                print("\n✅ Instead of generic placeholders, the AI should have:")
                print("  🤖 Analyzed each contact's description")
                print("  ✏️ Customized the message content accordingly")
                print("  🎯 Made each email feel personally relevant")
                print("  📝 Maintained professional tone throughout")
                
            elif result.get('emails_sent', 0) > 0:
                print("\n⚠️ Emails sent but no AI personalization detected")
                print("   This might mean:")
                print("   - AI personalization flag not properly set")
                print("   - Descriptions not being read correctly")
                print("   - Google API issues")
                
            else:
                print(f"\n❌ No emails were sent")
                print("   Possible issues:")
                print("   - Mailjet configuration")
                print("   - Email validation")
                print("   - API configuration")
                
                # Show full response for debugging
                print(f"\n🔍 Full Response:")
                print(json.dumps(result, indent=2))
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_standard_vs_ai_comparison():
    """Compare standard vs AI personalization."""
    
    print("\n" + "=" * 60)
    print("🆚 Standard vs AI Personalization Comparison")
    print("=" * 60)
    
    print("📝 Standard Personalization (placeholders only):")
    print("   Dear Alok,")
    print("   I hope this email finds you well...")
    print("   (Generic message for everyone)")
    
    print("\n🤖 AI Personalization (context-aware):")
    print("   Dear Alok,")
    print("   Given your technical background and preference for detailed")
    print("   documentation, I wanted to share our latest technical guides...")
    print("   (Customized based on description)")
    
    print("\n💡 The difference:")
    print("   ❌ Old way: Just replace {name} with actual name")
    print("   ✅ New way: AI reads description and customizes entire content")

if __name__ == "__main__":
    test_ai_personalization()
    test_standard_vs_ai_comparison()
