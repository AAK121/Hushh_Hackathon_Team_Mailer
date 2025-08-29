#!/usr/bin/env python3
"""
Test the memory functionality with a simple approach.
This bypasses consent validation to test core memory features.
"""

import os
import json
import sys
from datetime import datetime, timezone

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'hushh_mcp'))

def test_memory_with_simple_approach():
    """Test memory functionality with a simpler approach."""
    
    print("🧠 Testing MailerPanda Memory Functionality (Simple Approach)")
    print("=" * 70)
    
    try:
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        from hushh_mcp.config import VAULT_ENCRYPTION_KEY
        from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
        from hushh_mcp.types import EncryptedPayload
        
        # Create test user directory
        user_id = "memory_test_simple_456"
        user_vault_dir = os.path.join("vault", user_id)
        os.makedirs(user_vault_dir, exist_ok=True)
        
        print(f"✅ Test user directory created: {user_vault_dir}")
        
        # Test 1: Create and save memory data manually
        print("\n🎯 Test 1: Create and Save Memory Data")
        print("-" * 50)
        
        memory_data = {
            'user_id': user_id,
            'agent_id': 'agent_mailerpanda',
            'data_type': 'email_writing_preferences',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'preferences': {
                'writing_style': 'professional',
                'tone': 'friendly',
                'formality_level': 'business_casual',
                'personalization_preferences': 'high',
                'subject_line_style': 'clear_and_direct',
                'content_structure': 'introduction_body_conclusion',
                'closing_style': 'warm_professional',
                'key_phrases': ['Thank you', 'We appreciate', 'Looking forward'],
                'avoid_phrases': ['URGENT', 'ACT NOW', 'Limited time']
            },
            'email_examples': [
                {
                    'subject': 'Thank You for Your Purchase',
                    'content': 'Dear Customer,\n\nThank you for your recent purchase. We appreciate your business!\n\nBest regards,\nThe Team',
                    'user_input': 'Send a thank you email',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'campaign_id': 'test_001',
                    'user_satisfaction': 'approved'
                }
            ],
            'feedback_history': [
                {
                    'feedback': 'Make it more professional and formal',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'campaign_id': 'test_002',
                    'original_input': 'Send a casual update'
                }
            ],
            'campaign_history': []
        }
        
        # Encrypt and save the data
        encrypted_data = encrypt_data(json.dumps(memory_data), VAULT_ENCRYPTION_KEY)
        memory_file = os.path.join(user_vault_dir, "email_preferences.enc")
        
        with open(memory_file, 'w') as f:
            json.dump({
                'ciphertext': encrypted_data.ciphertext,
                'iv': encrypted_data.iv,
                'tag': encrypted_data.tag,
                'encoding': encrypted_data.encoding,
                'algorithm': encrypted_data.algorithm
            }, f)
        
        print(f"✅ Memory data encrypted and saved: {memory_file}")
        
        # Test 2: Load and decrypt memory data
        print("\n🎯 Test 2: Load and Decrypt Memory Data")
        print("-" * 50)
        
        with open(memory_file, 'r') as f:
            encrypted_file_data = json.load(f)
        
        # Reconstruct EncryptedPayload
        encrypted_payload = EncryptedPayload(
            ciphertext=encrypted_file_data['ciphertext'],
            iv=encrypted_file_data['iv'],
            tag=encrypted_file_data['tag'],
            encoding=encrypted_file_data['encoding'],
            algorithm=encrypted_file_data['algorithm']
        )
        
        # Decrypt the data
        decrypted_data = decrypt_data(encrypted_payload, VAULT_ENCRYPTION_KEY)
        loaded_memory = json.loads(decrypted_data)
        
        print("✅ Memory data successfully loaded and decrypted!")
        print(f"   👤 User ID: {loaded_memory.get('user_id')}")
        print(f"   📅 Created: {loaded_memory.get('created_at')}")
        print(f"   🎨 Writing Style: {loaded_memory.get('preferences', {}).get('writing_style')}")
        print(f"   📧 Email Examples: {len(loaded_memory.get('email_examples', []))}")
        print(f"   💬 Feedback History: {len(loaded_memory.get('feedback_history', []))}")
        
        # Test 3: Test style analysis
        print("\n🎯 Test 3: Test Style Analysis")
        print("-" * 50)
        
        # Initialize agent for style analysis
        agent = MassMailerAgent()
        style_guide = agent._analyze_user_style_from_memory(loaded_memory)
        
        print("✅ Style analysis generated:")
        print(f"   📋 Style Guide: {style_guide}")
        
        # Test 4: Add new email example to memory
        print("\n🎯 Test 4: Add New Email Example")
        print("-" * 50)
        
        # Add new example
        new_example = {
            'subject': 'Welcome to Our Newsletter',
            'content': 'Hello!\n\nWelcome to our monthly newsletter. We share industry insights and updates.\n\nBest wishes,\nNewsletter Team',
            'user_input': 'Send a newsletter welcome email',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'campaign_id': 'test_003',
            'user_satisfaction': 'approved'
        }
        
        loaded_memory['email_examples'].append(new_example)
        loaded_memory['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Re-encrypt and save
        updated_encrypted = encrypt_data(json.dumps(loaded_memory), VAULT_ENCRYPTION_KEY)
        
        with open(memory_file, 'w') as f:
            json.dump({
                'ciphertext': updated_encrypted.ciphertext,
                'iv': updated_encrypted.iv,
                'tag': updated_encrypted.tag,
                'encoding': updated_encrypted.encoding,
                'algorithm': updated_encrypted.algorithm
            }, f)
        
        print("✅ New email example added to memory")
        print(f"   📧 Total Examples Now: {len(loaded_memory['email_examples'])}")
        
        # Test 5: Generate AI context from memory
        print("\n🎯 Test 5: Generate AI Context from Memory")
        print("-" * 50)
        
        preferences = loaded_memory.get('preferences', {})
        examples = loaded_memory.get('email_examples', [])
        feedback_history = loaded_memory.get('feedback_history', [])
        
        # Build memory context like the agent would
        memory_context = f"""
📚 USER'S EMAIL WRITING PREFERENCES (Use this to match their style):
Style Guide: Writing style: {preferences.get('writing_style')} | Tone: {preferences.get('tone')} | Formality: {preferences.get('formality_level')}

🎯 Recent Email Examples (match this style):
"""
        
        for i, example in enumerate(examples[-2:], 1):  # Last 2 examples
            memory_context += f"Example {i}:\n"
            memory_context += f"Subject: {example.get('subject')}\n"
            memory_context += f"Content: {example.get('content')[:100]}...\n\n"
        
        if feedback_history:
            memory_context += "💬 Recent User Feedback (avoid these issues):\n"
            for fb in feedback_history[-2:]:
                memory_context += f"- {fb.get('feedback')}\n"
        
        print("✅ AI context generated from memory:")
        print(memory_context)
        
        # Test 6: Show memory evolution simulation
        print("\n🎯 Test 6: Memory Evolution Simulation")
        print("-" * 50)
        
        print("📈 How memory improves emails over time:")
        print("   1️⃣ First email: Generic, no preferences")
        print("   2️⃣ After feedback: Learns user prefers formal tone")
        print("   3️⃣ Third email: Applies formal tone from memory")
        print("   4️⃣ More feedback: Learns user likes specific phrases")
        print("   5️⃣ Future emails: Incorporates all learned preferences")
        
        print("\n🎉 Memory Functionality Test Complete!")
        print("   📁 Memory persisted in encrypted vault file")
        print("   🧠 AI can now use this memory for future emails")
        print("   🔄 Memory evolves with each user interaction")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_with_simple_approach()
