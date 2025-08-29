#!/usr/bin/env python3
"""
Focused test to verify memory system is working correctly.
Tests memory functionality directly and verifies integration.
"""

import os
import sys
import json
from datetime import datetime, timezone

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'hushh_mcp'))

def test_memory_integration_step_by_step():
    """Test memory integration step by step."""
    
    print("🧠 Testing MailerPanda Memory Integration - Step by Step")
    print("=" * 70)
    
    try:
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # Initialize agent
        api_keys = {
            "google_api_key": "AIzaSyCYmItUaAVeo1pRFnBdFPqTibIqas17TBI",
            "mailjet_api_key": "cca56ed08f5272f813370d7fc5a34a24",
            "mailjet_api_secret": "60fb43675233e2ac775f1c6cb8fe455c"
        }
        agent = MassMailerAgent(api_keys=api_keys)
        
        # Test user configuration
        user_id = "integration_test_999"
        
        # Mock consent tokens (for direct testing)
        consent_tokens = {
            "vault.read.email": "test_token_read",
            "vault.write.email": "test_token_write",
            "vault.read.file": "test_token_read_file",
            "vault.write.file": "test_token_write_file",
            "custom.temporary": "test_token_temp"
        }
        
        print("✅ MailerPanda agent initialized")
        print(f"👤 Test user: {user_id}")
        
        # Test 1: Create memory manually and test loading
        print("\n🎯 Test 1: Memory Creation and Loading")
        print("-" * 50)
        
        # Create user vault directory
        user_vault_dir = os.path.join("vault", user_id)
        os.makedirs(user_vault_dir, exist_ok=True)
        
        # Create initial memory data
        initial_memory = {
            'user_id': user_id,
            'agent_id': 'agent_mailerpanda',
            'data_type': 'email_writing_preferences',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'preferences': {
                'writing_style': 'professional',
                'tone': 'friendly',
                'formality_level': 'business_casual',
                'personalization_preferences': 'moderate',
                'subject_line_style': 'clear_and_direct',
                'content_structure': 'greeting_body_closing',
                'closing_style': 'warm_professional',
                'key_phrases': ['Thank you', 'We appreciate'],
                'avoid_phrases': ['URGENT', 'ACT NOW']
            },
            'email_examples': [],
            'feedback_history': [],
            'campaign_history': []
        }
        
        # Save memory manually using agent's method (bypassing consent validation)
        try:
            # Temporarily disable consent validation for testing
            original_validate = agent._validate_consent_for_operation
            agent._validate_consent_for_operation = lambda *args, **kwargs: True
            
            # Test saving memory
            memory_file = agent._save_user_email_memory(user_id, {
                'email_template': 'Test email content',
                'subject': 'Test Subject',
                'user_input': 'Test campaign',
                'writing_style': 'professional',
                'tone': 'friendly'
            }, consent_tokens)
            
            if memory_file:
                print("✅ Memory saved successfully")
                print(f"   📁 File: {os.path.basename(memory_file)}")
            else:
                print("❌ Failed to save memory")
                
            # Test loading memory
            loaded_memory = agent._load_user_email_memory(user_id, consent_tokens)
            
            if loaded_memory:
                print("✅ Memory loaded successfully")
                print(f"   👤 User ID: {loaded_memory.get('user_id')}")
                print(f"   📧 Examples: {len(loaded_memory.get('email_examples', []))}")
                print(f"   💬 Feedback: {len(loaded_memory.get('feedback_history', []))}")
            else:
                print("❌ Failed to load memory")
                
            # Restore original method
            agent._validate_consent_for_operation = original_validate
            
        except Exception as e:
            print(f"❌ Memory save/load test failed: {e}")
            
        # Test 2: Test style analysis
        print("\n🎯 Test 2: Style Analysis from Memory")
        print("-" * 50)
        
        if loaded_memory:
            style_guide = agent._analyze_user_style_from_memory(loaded_memory)
            print("✅ Style analysis generated")
            print(f"   📋 Style Guide: {style_guide}")
            
            if 'professional' in style_guide.lower():
                print("   ✅ Style analysis correctly detected professional tone")
            if 'friendly' in style_guide.lower():
                print("   ✅ Style analysis correctly detected friendly tone")
        else:
            print("❌ Cannot test style analysis without loaded memory")
            
        # Test 3: Test memory evolution
        print("\n🎯 Test 3: Memory Evolution Simulation")
        print("-" * 50)
        
        if loaded_memory:
            # Simulate adding feedback
            feedback_data = {
                'email_template': 'Updated email with formal tone',
                'subject': 'Formal Subject Line',
                'user_input': 'Second campaign',
                'user_feedback': 'Make it more formal and professional',
                'user_satisfaction': 'needs_improvement'
            }
            
            try:
                # Add feedback to memory
                agent._validate_consent_for_operation = lambda *args, **kwargs: True
                updated_file = agent._save_user_email_memory(user_id, feedback_data, consent_tokens)
                
                if updated_file:
                    print("✅ Feedback added to memory")
                    
                    # Load updated memory
                    updated_memory = agent._load_user_email_memory(user_id, consent_tokens)
                    
                    if updated_memory:
                        print(f"   📧 Examples: {len(updated_memory.get('email_examples', []))}")
                        print(f"   💬 Feedback: {len(updated_memory.get('feedback_history', []))}")
                        
                        # Test updated style analysis
                        new_style = agent._analyze_user_style_from_memory(updated_memory)
                        print(f"   📋 Updated Style: {new_style}")
                        
                        if 'formal' in new_style.lower():
                            print("   ✅ Memory evolution working - detected formality preference")
                            
                agent._validate_consent_for_operation = original_validate
                
            except Exception as e:
                print(f"❌ Memory evolution test failed: {e}")
                
        # Test 4: Test AI context generation
        print("\n🎯 Test 4: AI Context Generation")
        print("-" * 50)
        
        if loaded_memory:
            # Simulate how memory context would be built for AI
            preferences = loaded_memory.get('preferences', {})
            examples = loaded_memory.get('email_examples', [])
            feedback = loaded_memory.get('feedback_history', [])
            
            print("✅ AI context simulation:")
            print(f"   🎨 Writing Style: {preferences.get('writing_style', 'N/A')}")
            print(f"   🗣️ Tone: {preferences.get('tone', 'N/A')}")
            print(f"   📧 Recent Examples: {len(examples)}")
            print(f"   💬 Feedback Items: {len(feedback)}")
            
            # Show how this would appear in AI prompt
            if examples:
                print("   📝 Example content preview:")
                for i, ex in enumerate(examples[-2:], 1):
                    print(f"      {i}. {ex.get('subject', 'N/A')[:30]}...")
                    
            if feedback:
                print("   💭 Recent feedback:")
                for fb in feedback[-2:]:
                    print(f"      - {fb.get('feedback', 'N/A')[:50]}...")
                    
        # Test 5: Verify file persistence
        print("\n🎯 Test 5: File Persistence Verification")
        print("-" * 50)
        
        memory_file_path = os.path.join(user_vault_dir, "email_preferences.enc")
        
        if os.path.exists(memory_file_path):
            file_size = os.path.getsize(memory_file_path)
            print(f"✅ Memory file exists: {file_size} bytes")
            
            # Verify it's encrypted (should not contain plain text)
            with open(memory_file_path, 'r') as f:
                content = f.read()
                
            if 'ciphertext' in content and 'iv' in content:
                print("   ✅ File is properly encrypted")
            else:
                print("   ❌ File may not be properly encrypted")
                
            # Verify JSON structure
            try:
                encrypted_data = json.loads(content)
                required_fields = ['ciphertext', 'iv', 'tag', 'encoding', 'algorithm']
                
                if all(field in encrypted_data for field in required_fields):
                    print("   ✅ Encrypted file has correct structure")
                else:
                    print("   ❌ Encrypted file missing required fields")
                    
            except json.JSONDecodeError:
                print("   ❌ File is not valid JSON")
                
        else:
            print("❌ Memory file was not created")
            
        print("\n🎉 Integration Test Complete!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def verify_memory_files():
    """Verify existing memory files."""
    
    print("\n🔍 Existing Memory Files Verification")
    print("-" * 50)
    
    vault_dir = "vault"
    if not os.path.exists(vault_dir):
        print("❌ Vault directory does not exist")
        return
        
    users = [d for d in os.listdir(vault_dir) if os.path.isdir(os.path.join(vault_dir, d))]
    print(f"📁 Found {len(users)} user directories")
    
    memory_count = 0
    for user in users:
        memory_file = os.path.join(vault_dir, user, "email_preferences.enc")
        if os.path.exists(memory_file):
            file_size = os.path.getsize(memory_file)
            print(f"   ✅ {user}: {file_size} bytes")
            memory_count += 1
        
    print(f"\n📊 Summary: {memory_count}/{len(users)} users have email memory")
    
    if memory_count > 0:
        print("✅ Memory system is working and creating files!")
    else:
        print("⚠️ No memory files found - may need to run more tests")

if __name__ == "__main__":
    test_memory_integration_step_by_step()
    verify_memory_files()
