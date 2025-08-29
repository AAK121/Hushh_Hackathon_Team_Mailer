#!/usr/bin/env python3
"""
Direct test of the MailerPanda agent's memory functionality.
This tests the memory methods directly without going through the API.
"""

import os
import sys
import json
from datetime import datetime, timezone

# Add the hushh_mcp path to import the agent
sys.path.append(os.path.join(os.path.dirname(__file__), 'hushh_mcp'))

def test_memory_methods_directly():
    """Test the memory methods directly."""
    
    print("🧠 Testing MailerPanda Memory Methods Directly")
    print("=" * 65)
    
    try:
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # Initialize agent
        api_keys = {
            "google_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI",
            "mailjet_api_key": "cca56ed08f5272f813370d7fc5a34a24", 
            "mailjet_api_secret": "60fb43675233e2ac775f1c6cb8fe455c"
        }
        agent = MassMailerAgent(api_keys=api_keys)
        
        # Test user
        user_id = "memory_test_direct_123"
        consent_tokens = {
            "vault.read.email": "HCT:bWVtb3J5X3Rlc3RfZGlyZWN0XzEyM3xtYWlsZXJwYW5kYXx2YXVsdC5yZWFkLmVtYWlsfDE3NTU5NDYzMDk2NTR8MTc1NjAzMjcwOTY1NA==.e98cb6fe90a9d4a6ded5bf2a37b25028d1ea82a7e5dde4223552a312dba75b36",
            "vault.write.email": "HCT:bWVtb3J5X3Rlc3RfZGlyZWN0XzEyM3xtYWlsZXJwYW5kYXx2YXVsdC53cml0ZS5lbWFpbHwxNzU1OTQ2MzA5NjU0fDE3NTYwMzI3MDk2NTQ=.107cf985c5c82413b218a436e8206856b1f982e37a70d6c5ab2fabd97c0ef60e",
            "vault.read.file": "HCT:bWVtb3J5X3Rlc3RfZGlyZWN0XzEyM3xtYWlsZXJwYW5kYXx2YXVsdC5yZWFkLmZpbGV8MTc1NTk0NjMwOTY1NHwxNzU2MDMyNzA5NjU0.5549616fd68e1a507ff89e18692134c8301d40ec077df18e62b803059ca17642",
            "vault.write.file": "HCT:bWVtb3J5X3Rlc3RfZGlyZWN0XzEyM3xtYWlsZXJwYW5kYXx2YXVsdC53cml0ZS5maWxlfDE3NTU5NDYzMDk2NTV8MTc1NjAzMjcwOTY1NQ==.42fe283d1d7e27c05b31ad2b1370aac464e9b15c1a7b4740de335e349b5ee817",
            "custom.temporary": "HCT:bWVtb3J5X3Rlc3RfZGlyZWN0XzEyM3xtYWlsZXJwYW5kYXxjdXN0b20udGVtcG9yYXJ5fDE3NTU5NDYzMDk2NTV8MTc1NjAzMjcwOTY1NQ==.2c80196d5ae2f4709ee0c4b08531cacd15221bbee1c4a441a7f2b754e291e4d2"
        }
        
        print("✅ MailerPanda agent initialized")
        
        # Test 1: Load memory when none exists
        print("\n🎯 Test 1: Load Memory (No Memory Exists)")
        print("-" * 50)
        
        memory = agent._load_user_email_memory(user_id, consent_tokens)
        if memory is None:
            print("✅ Correctly returned None when no memory exists")
        else:
            print(f"❓ Unexpected memory found: {memory}")
        
        # Test 2: Save first email to memory
        print("\n🎯 Test 2: Save First Email to Memory")
        print("-" * 50)
        
        email_data_1 = {
            'email_template': "Dear {name},\n\nThank you for your recent purchase. We appreciate your business!\n\nBest regards,\nThe Team",
            'subject': "Thank You for Your Purchase",
            'user_input': "Send a thank you email to customers",
            'user_feedback': "",
            'campaign_id': "test_campaign_001",
            'writing_style': 'professional',
            'tone': 'friendly',
            'formality_level': 'professional'
        }
        
        result_1 = agent._save_user_email_memory(user_id, email_data_1, consent_tokens)
        if result_1:
            print(f"✅ First email saved to memory: {os.path.basename(result_1)}")
        else:
            print("❌ Failed to save first email")
            
        # Test 3: Load memory after saving
        print("\n🎯 Test 3: Load Memory After Saving")
        print("-" * 50)
        
        memory_after_save = agent._load_user_email_memory(user_id, consent_tokens)
        if memory_after_save:
            print("✅ Memory loaded successfully!")
            print(f"   📅 Created: {memory_after_save.get('created_at', 'N/A')}")
            print(f"   📧 Examples: {len(memory_after_save.get('email_examples', []))}")
            print(f"   💬 Feedback: {len(memory_after_save.get('feedback_history', []))}")
            
            # Show the saved preferences
            prefs = memory_after_save.get('preferences', {})
            print(f"   🎨 Writing Style: {prefs.get('writing_style', 'N/A')}")
            print(f"   🗣️ Tone: {prefs.get('tone', 'N/A')}")
            print(f"   🎭 Formality: {prefs.get('formality_level', 'N/A')}")
        else:
            print("❌ Failed to load memory after saving")
            return
            
        # Test 4: Save second email with feedback
        print("\n🎯 Test 4: Save Second Email with User Feedback")
        print("-" * 50)
        
        email_data_2 = {
            'email_template': "Hi {name},\n\nWe're excited to announce our new product launch! Check it out at our website.\n\nCheers,\nTeam",
            'subject': "Exciting New Product Launch!",
            'user_input': "Send a product launch announcement",
            'user_feedback': "Make it more formal and professional",
            'campaign_id': "test_campaign_002",
            'user_satisfaction': 'needs_improvement'
        }
        
        result_2 = agent._save_user_email_memory(user_id, email_data_2, consent_tokens)
        if result_2:
            print("✅ Second email with feedback saved to memory")
        else:
            print("❌ Failed to save second email")
            
        # Test 5: Analyze style from accumulated memory
        print("\n🎯 Test 5: Analyze User Style from Memory")
        print("-" * 50)
        
        updated_memory = agent._load_user_email_memory(user_id, consent_tokens)
        style_guide = agent._analyze_user_style_from_memory(updated_memory)
        
        if style_guide:
            print("✅ Style analysis generated:")
            print(f"   📋 Style Guide: {style_guide}")
            
            # Check if feedback analysis works
            if 'formal' in style_guide.lower():
                print("   ✅ Feedback analysis working - detected formality preference")
            else:
                print("   ❓ Feedback analysis may need improvement")
        else:
            print("❌ No style guide generated")
            
        # Test 6: Test memory evolution over time
        print("\n🎯 Test 6: Memory Evolution (Third Email)")
        print("-" * 50)
        
        email_data_3 = {
            'email_template': "Dear Valued Customer,\n\nWe would like to formally invite you to our annual conference.\n\nSincerely,\nThe Executive Team",
            'subject': "Formal Invitation to Annual Conference",
            'user_input': "Send conference invitation",
            'user_feedback': "",
            'campaign_id': "test_campaign_003",
            'user_satisfaction': 'approved'
        }
        
        result_3 = agent._save_user_email_memory(user_id, email_data_3, consent_tokens)
        final_memory = agent._load_user_email_memory(user_id, consent_tokens)
        
        if final_memory:
            examples = final_memory.get('email_examples', [])
            feedback = final_memory.get('feedback_history', [])
            
            print(f"✅ Memory evolution complete:")
            print(f"   📧 Total Examples: {len(examples)}")
            print(f"   💬 Total Feedback: {len(feedback)}")
            print(f"   🎯 Latest Example: {examples[-1].get('subject', 'N/A') if examples else 'None'}")
            
            # Final style analysis
            final_style = agent._analyze_user_style_from_memory(final_memory)
            print(f"   📋 Evolved Style: {final_style}")
            
        print("\n🎉 Memory Testing Complete!")
        print("   📁 Memory file location: vault/{}/email_preferences.enc".format(user_id))
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure the MailerPanda agent is properly installed")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_methods_directly()
