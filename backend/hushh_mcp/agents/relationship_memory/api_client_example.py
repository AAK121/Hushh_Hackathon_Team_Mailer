"""
Example API Client for Proactive Relationship Manager
Demonstrates how to interact with the FastAPI backend
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class RelationshipManagerClient:
    """Client for interacting with the Proactive Relationship Manager API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", auth_token: str = "demo_user_token"):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"Error details: {error_detail}")
                except:
                    print(f"Response text: {e.response.text}")
            raise
    
    # ==================== Core API Methods ====================
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._make_request("GET", "/health")
    
    def create_session(self, user_id: str) -> Dict[str, Any]:
        """Create a new user session"""
        return self._make_request("POST", f"/auth/session?user_id={user_id}")
    
    def process_natural_language(self, user_input: str, user_id: str, is_startup: bool = False) -> Dict[str, Any]:
        """Process natural language input through the agent"""
        data = {
            "user_input": user_input,
            "user_id": user_id,
            "is_startup": is_startup
        }
        return self._make_request("POST", "/agent/process", data)
    
    def proactive_check(self, user_id: str) -> Dict[str, Any]:
        """Run proactive check for upcoming events"""
        data = {"user_id": user_id}
        return self._make_request("POST", "/agent/proactive-check", data)
    
    # ==================== Contact Management ====================
    
    def add_contact(self, name: str, email: str = None, phone: str = None, 
                   company: str = None, priority: str = "medium") -> Dict[str, Any]:
        """Add a single contact"""
        data = {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "priority": priority
        }
        return self._make_request("POST", "/contacts/add", data)
    
    def add_batch_contacts(self, contacts: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
        """Add multiple contacts in batch"""
        data = {
            "contacts": contacts,
            "user_id": user_id
        }
        return self._make_request("POST", "/contacts/batch", data)
    
    def get_contacts(self, user_id: str) -> Dict[str, Any]:
        """Get all contacts"""
        return self._make_request("GET", "/contacts", params={"user_id": user_id})
    
    def get_contact_details(self, contact_name: str, user_id: str) -> Dict[str, Any]:
        """Get detailed information about a contact"""
        return self._make_request("GET", f"/contacts/{contact_name}/details", params={"user_id": user_id})
    
    def search_contacts(self, query: str, user_id: str) -> Dict[str, Any]:
        """Search contacts"""
        return self._make_request("GET", "/search/contacts", params={"query": query, "user_id": user_id})
    
    # ==================== Memory Management ====================
    
    def add_memory(self, contact_name: str, summary: str, user_id: str, 
                  location: str = None, tags: List[str] = None) -> Dict[str, Any]:
        """Add a memory about a contact"""
        data = {
            "contact_name": contact_name,
            "summary": summary,
            "user_id": user_id,
            "location": location,
            "tags": tags or []
        }
        return self._make_request("POST", "/memories/add", data)
    
    def get_memories(self, user_id: str, contact_name: str = None) -> Dict[str, Any]:
        """Get memories"""
        params = {"user_id": user_id}
        if contact_name:
            params["contact_name"] = contact_name
        return self._make_request("GET", "/memories", params=params)
    
    # ==================== Reminder Management ====================
    
    def add_reminder(self, contact_name: str, title: str, user_id: str, 
                    date: str = None, priority: str = "medium") -> Dict[str, Any]:
        """Add a reminder"""
        data = {
            "contact_name": contact_name,
            "title": title,
            "user_id": user_id,
            "date": date,
            "priority": priority
        }
        return self._make_request("POST", "/reminders/add", data)
    
    def get_reminders(self, user_id: str) -> Dict[str, Any]:
        """Get all reminders"""
        return self._make_request("GET", "/reminders", params={"user_id": user_id})
    
    # ==================== Advice and Dates ====================
    
    def get_advice(self, contact_name: str, question: str, user_id: str) -> Dict[str, Any]:
        """Get conversational advice about a contact"""
        data = {
            "contact_name": contact_name,
            "question": question,
            "user_id": user_id
        }
        return self._make_request("POST", "/advice", data)
    
    def get_upcoming_dates(self, user_id: str) -> Dict[str, Any]:
        """Get upcoming birthdays and important dates"""
        return self._make_request("GET", "/dates/upcoming", params={"user_id": user_id})
    
    def add_important_date(self, contact_name: str, date_type: str, date_value: str, 
                          user_id: str, year: str = None) -> Dict[str, Any]:
        """Add an important date"""
        params = {
            "contact_name": contact_name,
            "date_type": date_type,
            "date_value": date_value,
            "user_id": user_id
        }
        if year:
            params["year"] = year
        return self._make_request("POST", "/dates/add", params=params)


def demo_api_usage():
    """Demonstrate API usage with examples"""
    print("🚀 Proactive Relationship Manager API Client Demo")
    print("=" * 60)
    
    # Initialize client
    client = RelationshipManagerClient()
    user_id = "demo_user_001"
    
    try:
        # 1. Health check
        print("\n1. Health Check:")
        health = client.health_check()
        print(f"   Status: {health.get('status')}")
        
        # 2. Create session
        print("\n2. Creating User Session:")
        session = client.create_session(user_id)
        print(f"   Session created for user: {session.get('user_id')}")
        
        # 3. Add contacts
        print("\n3. Adding Contacts:")
        
        # Single contact
        result = client.add_contact(
            name="Alice Johnson",
            email="alice@techstartup.com",
            company="TechStartup Inc",
            priority="high"
        )
        print(f"   Single contact: {result.get('message')}")
        
        # Batch contacts
        batch_contacts = [
            {"name": "Bob Wilson", "phone": "+1-555-0123", "priority": "medium"},
            {"name": "Carol Davis", "email": "carol@designstudio.com", "company": "Design Studio"}
        ]
        result = client.add_batch_contacts(batch_contacts, user_id)
        print(f"   Batch contacts: {result.get('message')}")
        
        # 4. Add memories
        print("\n4. Adding Memories:")
        result = client.add_memory(
            contact_name="Alice Johnson",
            summary="loves rock climbing and photography",
            user_id=user_id,
            location="Coffee shop"
        )
        print(f"   Memory added: {result.get('message')}")
        
        # 5. Add important date
        print("\n5. Adding Important Date:")
        result = client.add_important_date(
            contact_name="Alice Johnson",
            date_type="birthday",
            date_value="March 15th",
            user_id=user_id
        )
        print(f"   Date added: {result.get('message')}")
        
        # 6. Get contacts
        print("\n6. Retrieving Contacts:")
        result = client.get_contacts(user_id)
        print(f"   Contacts: {result.get('message')}")
        
        # 7. Get advice
        print("\n7. Getting Advice:")
        result = client.get_advice(
            contact_name="Alice Johnson",
            question="What should I get Alice for her birthday?",
            user_id=user_id
        )
        print(f"   Advice: {result.get('message')[:100]}...")
        
        # 8. Proactive check
        print("\n8. Proactive Check:")
        result = client.proactive_check(user_id)
        print(f"   Proactive: {result.get('message')}")
        
        # 9. Natural language processing
        print("\n9. Natural Language Processing:")
        result = client.process_natural_language(
            user_input="remember that Bob Wilson is a software engineer who loves cooking",
            user_id=user_id
        )
        print(f"   NLP Result: {result.get('message')}")
        
        print(f"\n✅ API Demo completed successfully!")
        print(f"🌐 API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print(f"💡 Make sure the API server is running: python api.py")


if __name__ == "__main__":
    demo_api_usage()