#!/usr/bin/env python3
"""
Simple test to check the notes API and fix chronological order.
"""

import requests
import json

def test_and_fix_notes():
    """Test notes API and fix order if possible."""
    
    print("🔍 Testing Notes API...")
    
    # Try different API endpoints
    base_url = "http://localhost:8001"
    
    endpoints_to_try = [
        f"{base_url}/research/notes",
        f"{base_url}/notes",
        f"{base_url}/research/notes/AI%20Responses",
        f"{base_url}/api/notes/AI%20Responses"
    ]
    
    for endpoint in endpoints_to_try:
        try:
            print(f"📡 Trying: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Success! Found working endpoint")
                return
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🤔 Let me try a different approach...")
    
    # Try the research agent chat API to see if backend is working
    try:
        chat_url = f"{base_url}/research/chat"
        test_payload = {
            "message": "test",
            "paper_id": "test"
        }
        
        response = requests.post(chat_url, json=test_payload, timeout=10)
        print(f"📡 Chat API test: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backend is working! The issue might be with the notes endpoint.")
        else:
            print("❌ Backend might not be fully operational.")
            
    except Exception as e:
        print(f"❌ Backend connection error: {e}")

if __name__ == "__main__":
    test_and_fix_notes()
