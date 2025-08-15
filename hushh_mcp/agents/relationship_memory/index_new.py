# hushh_mcp/agents/relationship_memory/index.py

"""
Relationship Memory Agent - Main Entry Point
AI-powered agent for managing contacts, memories, and reminders with full MCP compliance.
According to HushhMCP docs structure.
"""

import os
import sys
import uuid
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.relationship_memory.manifest import manifest

# Import utilities
try:
    from hushh_mcp.agents.relationship_memory.utils.vault_manager import VaultManager
    from hushh_mcp.agents.relationship_memory.utils.llm import GeminiLLM
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    VaultManager = None
    GeminiLLM = None

class RelationshipMemoryAgent:
    """
    Main Relationship Memory Agent class following HushhMCP docs pattern.
    All logic contained in index.py as per docs requirements.
    """
    
    def __init__(self):
        self.agent_id = manifest["id"]
        self.required_scopes = manifest["scopes"]
        
        # Load environment variables
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            # Fallback to project root .env
            main_env_path = os.path.join(project_root, '.env')
            load_dotenv(main_env_path)
    
    def handle(self, user_id: str, tokens: Dict[str, str], user_input: str, vault_key: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Main handler method following HushhMCP docs pattern.
        
        Args:
            user_id: User identifier
            tokens: Dictionary of consent tokens by scope
            user_input: Natural language input from user
            vault_key: Optional vault encryption key
            
        Returns:
            Dictionary with agent response
        """
        
        # Generate vault key if not provided
        if not vault_key:
            vault_key = os.urandom(32)
        
        # Validate at least one token
        if not tokens:
            return {
                "status": "error",
                "message": "❌ No consent tokens provided",
                "agent_id": self.agent_id
            }
        
        # Validate permissions for required scopes
        validated_scopes = []
        for scope in self.required_scopes:
            token = tokens.get(scope.value)
            if token:
                valid, reason = self._validate_permissions(user_id, token, scope)
                if valid:
                    validated_scopes.append(scope)
                else:
                    print(f"⚠️ Scope {scope.value} validation failed: {reason}")
        
        if not validated_scopes:
            return {
                "status": "error",
                "message": "❌ No valid tokens found for required scopes",
                "agent_id": self.agent_id
            }
        
        # Initialize components
        try:
            if VaultManager is None or GeminiLLM is None:
                return {
                    "status": "error",
                    "message": "❌ Required dependencies not available",
                    "agent_id": self.agent_id
                }
            
            vault_manager = VaultManager(user_id=user_id, encryption_key=vault_key)
            llm = GeminiLLM()
            
            # Process the user input
            result = self._process_input(user_input, vault_manager, llm)
            
            # Add metadata
            result.update({
                "agent_id": self.agent_id,
                "user_id": user_id,
                "validated_scopes": [scope.value for scope in validated_scopes]
            })
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Agent execution failed: {str(e)}",
                "agent_id": self.agent_id,
                "user_id": user_id
            }
    
    def _validate_permissions(self, user_id: str, token: str, required_scope: ConsentScope) -> tuple[bool, str]:
        """Validate token and permissions for the given scope"""
        try:
            valid, reason, parsed = validate_token(token, expected_scope=required_scope)
            
            if not valid:
                return False, f"❌ Invalid token: {reason}"
                
            if parsed.user_id != user_id:
                return False, "❌ Token user mismatch"
                
            return True, "✅ Token validated successfully"
            
        except Exception as e:
            return False, f"❌ Token validation error: {str(e)}"
    
    def _process_input(self, user_input: str, vault_manager, llm) -> Dict[str, Any]:
        """Process user input and return appropriate response"""
        
        # Parse intent using LLM
        try:
            intent = llm.parse_intent(user_input)
            action = intent.get('action', 'unknown')
            
            print(f"🔍 Debug - Parsed action: {action}")
            
            # Route based on action
            if action == 'add_contact':
                return self._add_contact(user_input, vault_manager, llm)
            elif action == 'show_contacts':
                return self._show_contacts(vault_manager)
            elif action == 'search_contacts':
                query = intent.get('search_query', '')
                return self._search_contacts(query, vault_manager)
            elif action == 'add_memory':
                return self._add_memory(user_input, vault_manager, llm)
            elif action == 'show_memories':
                return self._show_memories(vault_manager)
            elif action == 'add_reminder':
                return self._add_reminder(user_input, vault_manager, llm)
            elif action == 'show_reminders':
                return self._show_reminders(vault_manager)
            else:
                return {
                    "status": "error",
                    "message": f"❌ Unknown action: {action}. Try: 'add contact', 'show contacts', 'remember', or 'remind me'"
                }
                
        except Exception as e:
            # Fallback to regex parsing if LLM fails
            print(f"⚠️ LLM parsing failed: {e}, using fallback")
            return self._process_fallback(user_input, vault_manager)
    
    def _process_fallback(self, user_input: str, vault_manager) -> Dict[str, Any]:
        """Fallback processing using regex when LLM fails"""
        text = user_input.lower()
        
        if any(word in text for word in ['add', 'new']) and 'contact' in text:
            return self._add_contact_fallback(user_input, vault_manager)
        elif 'show' in text and 'contact' in text:
            return self._show_contacts(vault_manager)
        elif any(word in text for word in ['remember', 'memory']):
            return self._add_memory_fallback(user_input, vault_manager)
        elif any(word in text for word in ['remind', 'reminder']):
            return self._add_reminder_fallback(user_input, vault_manager)
        else:
            return {
                "status": "error",
                "message": "❌ Could not understand your request. Try: 'add contact', 'show contacts', 'remember', or 'remind me'"
            }
    
    def _add_contact(self, user_input: str, vault_manager, llm) -> Dict[str, Any]:
        """Add a new contact"""
        try:
            # Extract contact info using LLM
            contact_data = llm.extract_contact_info(user_input)
            
            # Fallback to regex if LLM fails
            if not contact_data.get('name'):
                contact_data = self._extract_contact_fallback(user_input)
            
            if not contact_data.get('name'):
                return {
                    "status": "error",
                    "message": "❌ Could not extract contact name. Please specify a name."
                }
            
            # Store contact
            contact_id = vault_manager.store_contact(contact_data)
            
            return {
                "status": "success",
                "action": "contact_added",
                "message": f"✅ Successfully added {contact_data['name']} to your contacts",
                "contact_id": contact_id,
                "contact": contact_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Failed to add contact: {str(e)}"
            }
    
    def _add_contact_fallback(self, user_input: str, vault_manager) -> Dict[str, Any]:
        """Add contact using fallback regex parsing"""
        contact_data = self._extract_contact_fallback(user_input)
        
        if not contact_data.get('name'):
            return {
                "status": "error",
                "message": "❌ Could not extract contact name. Please specify a name."
            }
        
        try:
            contact_id = vault_manager.store_contact(contact_data)
            return {
                "status": "success",
                "action": "contact_added",
                "message": f"✅ Successfully added {contact_data['name']} to your contacts",
                "contact_id": contact_id,
                "contact": contact_data
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Failed to add contact: {str(e)}"
            }
    
    def _show_contacts(self, vault_manager) -> Dict[str, Any]:
        """Show all contacts"""
        try:
            contacts = vault_manager.get_contacts()
            return {
                "status": "success",
                "action": "contacts_retrieved",
                "message": f"📋 Found {len(contacts)} contacts",
                "contacts": contacts
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Failed to retrieve contacts: {str(e)}"
            }
    
    def _search_contacts(self, query: str, vault_manager) -> Dict[str, Any]:
        """Search contacts"""
        try:
            results = vault_manager.search_contacts(query)
            return {
                "status": "success",
                "action": "contacts_searched",
                "message": f"🔍 Found {len(results)} contacts matching '{query}'",
                "contacts": results,
                "search_query": query
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Search failed: {str(e)}"
            }
    
    def _add_memory(self, user_input: str, vault_manager, llm) -> Dict[str, Any]:
        """Add a memory"""
        try:
            # Extract memory info using LLM
            memory_data = llm.extract_memory_info(user_input)
            
            # Fallback to regex if LLM fails
            if not memory_data.get('summary'):
                memory_data = self._extract_memory_fallback(user_input)
            
            if not memory_data.get('summary'):
                return {
                    "status": "error",
                    "message": "❌ Could not extract memory information. Please specify what to remember."
                }
            
            # Store memory
            memory_id = vault_manager.store_memory(memory_data)
            
            contact_name = memory_data.get('contact_name', 'someone')
            return {
                "status": "success",
                "action": "memory_added",
                "message": f"🧠 Successfully recorded memory about {contact_name}",
                "memory_id": memory_id,
                "memory": memory_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Failed to add memory: {str(e)}"
            }
    
    def _add_memory_fallback(self, user_input: str, vault_manager) -> Dict[str, Any]:
        """Add memory using fallback regex parsing"""
        memory_data = self._extract_memory_fallback(user_input)
        
        if not memory_data.get('summary'):
            return {
                "status": "error",
                "message": "❌ Could not extract memory information. Please specify what to remember."
            }
        
        try:
            memory_id = vault_manager.store_memory(memory_data)
            contact_name = memory_data.get('contact_name', 'someone')
            return {
                "status": "success",
                "action": "memory_added",
                "message": f"🧠 Successfully recorded memory about {contact_name}",
                "memory_id": memory_id,
                "memory": memory_data
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Failed to add memory: {str(e)}"
            }
    
    def _show_memories(self, vault_manager) -> Dict[str, Any]:
        """Show all memories"""
        try:
            memories = vault_manager.get_memories()
            return {
                "status": "success",
                "action": "memories_retrieved",
                "message": f"🧠 Found {len(memories)} memories",
                "memories": memories
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Failed to retrieve memories: {str(e)}"
            }
    
    def _add_reminder(self, user_input: str, vault_manager, llm) -> Dict[str, Any]:
        """Add a reminder"""
        try:
            # Extract reminder info using LLM
            reminder_data = llm.extract_reminder_info(user_input)
            
            # Fallback to regex if LLM fails
            if not reminder_data.get('title'):
                reminder_data = self._extract_reminder_fallback(user_input)
            
            if not reminder_data.get('title'):
                return {
                    "status": "error",
                    "message": "❌ Could not extract reminder information. Please specify what to be reminded about."
                }
            
            # Store reminder
            reminder_id = vault_manager.store_reminder(reminder_data)
            
            return {
                "status": "success",
                "action": "reminder_added",
                "message": f"⏰ Successfully set reminder: {reminder_data['title']}",
                "reminder_id": reminder_id,
                "reminder": reminder_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Failed to add reminder: {str(e)}"
            }
    
    def _add_reminder_fallback(self, user_input: str, vault_manager) -> Dict[str, Any]:
        """Add reminder using fallback regex parsing"""
        reminder_data = self._extract_reminder_fallback(user_input)
        
        if not reminder_data.get('title'):
            return {
                "status": "error",
                "message": "❌ Could not extract reminder information. Please specify what to be reminded about."
            }
        
        try:
            reminder_id = vault_manager.store_reminder(reminder_data)
            return {
                "status": "success",
                "action": "reminder_added",
                "message": f"⏰ Successfully set reminder: {reminder_data['title']}",
                "reminder_id": reminder_id,
                "reminder": reminder_data
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Failed to add reminder: {str(e)}"
            }
    
    def _show_reminders(self, vault_manager) -> Dict[str, Any]:
        """Show all reminders"""
        try:
            reminders = vault_manager.get_reminders()
            return {
                "status": "success",
                "action": "reminders_retrieved",
                "message": f"⏰ Found {len(reminders)} reminders",
                "reminders": reminders
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Failed to retrieve reminders: {str(e)}"
            }
    
    def _extract_contact_fallback(self, user_input: str) -> dict:
        """Fallback contact extraction using regex patterns"""
        import re
        
        contact_data = {}
        text = user_input.strip()
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            contact_data['email'] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r'\b\d{10}\b', text)
        if phone_match:
            contact_data['phone'] = phone_match.group(0)
        
        # Extract name - multiple patterns
        name = None
        
        # Pattern: "add [name] as" or "add [name] with"
        match = re.search(r'add\s+([a-zA-Z\s]+?)\s+(?:as|with|email)', text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
        
        # Pattern: "add [name]" at beginning
        if not name:
            match = re.search(r'add\s+([a-zA-Z\s]+)', text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                # Filter out common words
                words = candidate.split()
                name_words = [w for w in words if w.lower() not in ['new', 'contact', 'user', 'person', 'as', 'with', 'email', 'phone']]
                if name_words:
                    name = ' '.join(name_words)
        
        if name:
            contact_data['name'] = ' '.join(word.capitalize() for word in name.split())
        
        return contact_data
    
    def _extract_memory_fallback(self, user_input: str) -> dict:
        """Fallback memory extraction using regex patterns"""
        import re
        
        memory_data = {}
        text = user_input.strip()
        
        # Extract contact name
        name_match = re.search(r'remember\s+(?:that\s+)?([a-zA-Z\s]+?)\s+(?:is|was|loves|likes|works|lives|from)', text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()
            memory_data['contact_name'] = ' '.join(word.capitalize() for word in name.split())
        
        # Extract the summary
        if 'remember that' in text.lower():
            summary_start = text.lower().find('remember that') + len('remember that')
            summary = text[summary_start:].strip()
        elif 'remember' in text.lower():
            summary_start = text.lower().find('remember') + len('remember')
            summary = text[summary_start:].strip()
        else:
            summary = text
        
        memory_data['summary'] = summary
        
        return memory_data
    
    def _extract_reminder_fallback(self, user_input: str) -> dict:
        """Fallback reminder extraction using regex patterns"""
        import re
        
        reminder_data = {}
        text = user_input.strip()
        
        # Extract contact name
        action_patterns = [
            r'(?:call|email|meet|contact|text|message)\s+([a-zA-Z\s]+?)(?:\s+(?:tomorrow|today|next|on|at|$))',
            r'remind\s+me\s+to\s+(?:call|email|meet|contact|text|message)\s+([a-zA-Z\s]+)',
            r'to\s+(?:call|email|meet|contact|text|message)\s+([a-zA-Z\s]+)'
        ]
        
        for pattern in action_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                reminder_data['contact_name'] = ' '.join(word.capitalize() for word in name.split())
                break
        
        # Extract the title/action
        if 'remind me to' in text.lower():
            title_start = text.lower().find('remind me to') + len('remind me to')
            title = text[title_start:].strip()
        elif 'set a reminder to' in text.lower():
            title_start = text.lower().find('set a reminder to') + len('set a reminder to')
            title = text[title_start:].strip()
        else:
            title = text
        
        reminder_data['title'] = title
        
        # Extract date/time if mentioned
        time_patterns = [
            r'tomorrow',
            r'today',
            r'next\s+\w+',
            r'on\s+\w+',
            r'at\s+\d+',
            r'\d+\s*(?:am|pm)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                reminder_data['date'] = match.group(0)
                break
        
        # Default priority
        reminder_data['priority'] = 'medium'
        
        return reminder_data


# Main function for running the agent (following docs pattern)
def run(user_id: str = None, vault_key: bytes = None, demo_mode: bool = True) -> Dict[str, Any]:
    """
    Main function to run the agent (for testing/demo purposes)
    Following HushhMCP docs pattern.
    """
    
    if not user_id:
        user_id = f"demo_user_{str(uuid.uuid4())[:8]}"
    
    if not vault_key:
        vault_key = os.urandom(32)
    
    agent = RelationshipMemoryAgent()
    
    if demo_mode:
        # Demo mode with mock tokens
        print("🚀 Running in demo mode with mock tokens...")
        
        # Create mock tokens for demo
        mock_tokens = {}
        for scope in manifest["scopes"]:
            mock_tokens[scope.value] = f"mock_token_for_{scope.value}"
        
        # Demo interactions
        demo_inputs = [
            "add alok as a contact with email 23b2223@iitb.ac.in",
            "add sarah with phone 9876543210",
            "show my contacts",
            "remember that alok loves cricket",
            "remind me to call sarah tomorrow"
        ]
        
        results = []
        for user_input in demo_inputs:
            print(f"\n🔍 Testing: {user_input}")
            result = agent.handle(user_id, mock_tokens, user_input, vault_key)
            print(f"📋 Result: {result.get('message', 'No message')}")
            results.append(result)
        
        return {"demo_results": results}
    
    else:
        print("🤖 Agent initialized. Use agent.handle(user_id, tokens, user_input) to process requests.")
        return {"agent": agent, "status": "ready"}
