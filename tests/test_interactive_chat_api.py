#!/usr/bin/env python3
"""
Interactive Chat API Test for Relationship Memory Agent
========================================================

This script demonstrates the new interactive chat endpoints that provide:
- Session-based conversations
- Persistent chat history
- Real-time message exchange
- Session management

Usage: python test_interactive_chat_api.py
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://127.0.0.1:8001"
RELATIONSHIP_MEMORY_BASE = f"{API_BASE_URL}/agents/relationship_memory"

class InteractiveChatTester:
    """Test the interactive chat functionality of the Relationship Memory agent."""
    
    def __init__(self):
        self.session_id = None
        self.conversation_count = 0
        
    def create_demo_tokens(self) -> Dict[str, str]:
        """Create demo tokens for testing."""
        # In a real implementation, these would be properly issued tokens
        return {
            "vault.read.contacts": "demo_token_read_contacts",
            "vault.write.contacts": "demo_token_write_contacts", 
            "vault.read.memory": "demo_token_read_memory",
            "vault.write.memory": "demo_token_write_memory",
            "vault.read.reminder": "demo_token_read_reminder",
            "vault.write.reminder": "demo_token_write_reminder"
        }
    
    def start_chat_session(self) -> bool:
        """Start a new interactive chat session."""
        print("🚀 Starting Interactive Chat Session...")
        print("=" * 50)
        
        payload = {
            "user_id": "interactive_test_user",
            "tokens": self.create_demo_tokens(),
            "vault_key": "demo_vault_key_for_interactive_chat",
            "session_name": "demo_chat",
            "gemini_api_key": "your_gemini_api_key_here"  # This would be real in production
        }
        
        try:
            response = requests.post(
                f"{RELATIONSHIP_MEMORY_BASE}/chat/start",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.session_id = result["session_id"]
                print(f"✅ Chat session started successfully!")
                print(f"📋 Session ID: {self.session_id}")
                print(f"💬 Message: {result['message']}")
                
                if "session_info" in result:
                    print("\n🎯 Available Commands:")
                    for cmd in result["session_info"]["available_commands"]:
                        print(f"   • {cmd}")
                
                return True
            else:
                print(f"❌ Failed to start session: {response.status_code}")
                print(f"📋 Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting session: {str(e)}")
            return False
    
    def send_message(self, message: str) -> bool:
        """Send a message in the chat session."""
        if not self.session_id:
            print("❌ No active session. Start a session first.")
            return False
        
        print(f"\n[{self.conversation_count + 1}] 🗣️ You: {message}")
        
        payload = {
            "session_id": self.session_id,
            "message": message
        }
        
        try:
            response = requests.post(
                f"{RELATIONSHIP_MEMORY_BASE}/chat/message",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.conversation_count = result["conversation_count"]
                
                print(f"🤖 Agent: {result['agent_response']}")
                print(f"⏱️ Processing time: {result['processing_time']:.2f}s")
                print(f"🕒 Timestamp: {result['timestamp']}")
                return True
            else:
                print(f"❌ Failed to send message: {response.status_code}")
                print(f"📋 Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending message: {str(e)}")
            return False
    
    def get_chat_history(self) -> bool:
        """Get the conversation history."""
        if not self.session_id:
            print("❌ No active session.")
            return False
        
        try:
            response = requests.get(f"{RELATIONSHIP_MEMORY_BASE}/chat/{self.session_id}/history")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n📚 Chat History (Total: {result['total_messages']} messages)")
                print("=" * 50)
                
                for entry in result["conversation_history"]:
                    print(f"[{entry['id']}] 🗣️ You: {entry['user_message']}")
                    print(f"[{entry['id']}] 🤖 Agent: {entry['agent_response']}")
                    print(f"    ⏱️ {entry['processing_time']:.2f}s | 🕒 {entry['timestamp']}")
                    print("-" * 30)
                
                return True
            else:
                print(f"❌ Failed to get history: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting history: {str(e)}")
            return False
    
    def list_sessions(self) -> bool:
        """List all active chat sessions."""
        try:
            response = requests.get(f"{RELATIONSHIP_MEMORY_BASE}/chat/sessions")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n📋 Active Sessions: {result['active_sessions']}")
                print("=" * 50)
                
                for session in result["sessions"]:
                    print(f"🆔 {session['session_id']}")
                    print(f"   👤 User: {session['user_id']}")
                    print(f"   📛 Name: {session['session_name']}")
                    print(f"   💬 Messages: {session['conversation_count']}")
                    print(f"   🕒 Created: {session['created_at']}")
                    print(f"   🕒 Last Activity: {session['last_activity']}")
                    print("-" * 30)
                
                return True
            else:
                print(f"❌ Failed to list sessions: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error listing sessions: {str(e)}")
            return False
    
    def end_session(self) -> bool:
        """End the current chat session."""
        if not self.session_id:
            print("❌ No active session.")
            return False
        
        try:
            response = requests.delete(f"{RELATIONSHIP_MEMORY_BASE}/chat/{self.session_id}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n👋 Session ended: {result['message']}")
                
                if "session_summary" in result:
                    summary = result["session_summary"]
                    print(f"📊 Total messages: {summary['total_messages']}")
                    print(f"🕒 Duration: {summary['duration']}")
                
                self.session_id = None
                return True
            else:
                print(f"❌ Failed to end session: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error ending session: {str(e)}")
            return False
    
    def run_demo(self):
        """Run a complete interactive chat demonstration."""
        print("🎯 RELATIONSHIP MEMORY AGENT - INTERACTIVE CHAT API DEMO")
        print("=" * 60)
        
        # Start session
        if not self.start_chat_session():
            return
        
        # Demo conversation
        demo_messages = [
            "add contact John Smith with email john.smith@example.com",
            "add Sarah with phone 555-0123 and email sarah@example.com", 
            "remember that John loves hiking and photography",
            "remind me to call Sarah tomorrow at 2 PM",
            "show my contacts",
            "what should I get John for his birthday?",
            "show my memories about John"
        ]
        
        print(f"\n💬 Running Demo Conversation...")
        print("=" * 50)
        
        for message in demo_messages:
            self.send_message(message)
            time.sleep(1)  # Small delay to make it readable
        
        # Show history
        print(f"\n📚 Displaying Conversation History...")
        self.get_chat_history()
        
        # List all sessions
        print(f"\n📋 Listing All Active Sessions...")
        self.list_sessions()
        
        # End session
        print(f"\n👋 Ending Chat Session...")
        self.end_session()

def main():
    """Main function to run the interactive chat demo."""
    print("🚀 Testing Relationship Memory Agent Interactive Chat API...")
    
    # Test if API is accessible
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        if response.status_code != 200:
            print(f"❌ API server not accessible at {API_BASE_URL}")
            print("Please make sure the API server is running on port 8001")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API server: {str(e)}")
        print("Please make sure the API server is running on port 8001")
        return
    
    # Run the demo
    tester = InteractiveChatTester()
    tester.run_demo()
    
    print("\n🎉 Interactive Chat API Demo Completed!")
    print(f"📚 API Documentation: {API_BASE_URL}/docs")
    print(f"🔧 Test the endpoints interactively at: {API_BASE_URL}/docs")

if __name__ == "__main__":
    main()
