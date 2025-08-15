from typing import List, Dict, Optional
from datetime import datetime
import json
import uuid
import re
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.types import VaultKey, VaultRecord, EncryptedPayload, UserID, AgentID, ConsentScope
from .vault_manager import VaultManager

class RelationshipMemoryAgent:
    def __init__(self, user_id: str, vault_key: str):
        self.user_id = UserID(user_id)
        self.agent_id = AgentID("relationship_memory")
        self.vault_key = vault_key
        
        # Initialize vault manager for persistent storage
        self.vault_manager = VaultManager(user_id, vault_key)
        
        # Legacy vault keys for compatibility
        self._contacts_key = VaultKey(user_id=self.user_id, scope=ConsentScope.VAULT_WRITE_CONTACTS)
        self._memories_key = VaultKey(user_id=self.user_id, scope=ConsentScope.VAULT_WRITE_MEMORY)
        self._reminders_key = VaultKey(user_id=self.user_id, scope=ConsentScope.VAULT_WRITE_REMINDER)
        
    def _store_data(self, key: VaultKey, data: dict) -> VaultRecord:
        encrypted = encrypt_data(json.dumps(data), self.vault_key)
        return VaultRecord(
            key=key,
            data=encrypted,
            agent_id=self.agent_id,
            created_at=int(datetime.now().timestamp() * 1000)
        )

    def _load_data(self, record: VaultRecord) -> dict:
        decrypted = decrypt_data(record.data, self.vault_key)
        return json.loads(decrypted)

    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from text"""
        info = {}
        text = text.strip()
        text_lower = text.lower()
        
        # Extract email first
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            info['email'] = email_match.group(0)
        
        # Extract phone numbers
        phone_patterns = [
            r'(?:phone|tel|number|mobile)[:\s]+([+\d\s\-\(\)]{7,15})',  # After keywords
            r'\b(\d{10})\b',  # 10 digit number
            r'\b(\+\d{1,3}[\s\-]?\d{10})\b'  # International format
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                info['phone'] = phone_match.group(1).strip()
                break
        
        # Extract name - improved logic
        name = None
        
        # Pattern 1: "add [name] as" or "add [name] with"
        match = re.search(r'add\s+(?:new\s+)?(?:user\s+)?(?:contact\s+)?(\w+(?:\s+\w+)*?)\s+(?:as|with|email|phone)', text_lower)
        if match:
            candidate = match.group(1).strip()
            # Filter out common words
            name_words = [word for word in candidate.split() if word.lower() not in ['new', 'user', 'contact', 'his', 'her', 'the', 'a']]
            if name_words:
                name = ' '.join(name_words)
        
        # Pattern 2: "add [name] and" 
        if not name:
            match = re.search(r'add\s+(?:new\s+)?(?:user\s+)?(?:contact\s+)?(\w+(?:\s+\w+)*?)\s+and', text_lower)
            if match:
                candidate = match.group(1).strip()
                name_words = [word for word in candidate.split() if word.lower() not in ['new', 'user', 'contact', 'his', 'her', 'the', 'a']]
                if name_words:
                    name = ' '.join(name_words)
        
        # Pattern 3: Simple "add [name]" at the beginning (single or double word names)
        if not name:
            match = re.search(r'add\s+(?:new\s+)?(?:user\s+)?(?:contact\s+)?(\w+(?:\s+\w+)?)', text_lower)
            if match:
                candidate = match.group(1).strip()
                # Make sure it's not a keyword and is likely a name
                words = candidate.split()
                name_words = [word for word in words if word.lower() not in ['new', 'user', 'contact', 'his', 'her', 'the', 'a', 'also', 'with', 'number', 'email', 'phone']]
                if name_words and len(name_words) <= 3:  # Reasonable name length
                    name = ' '.join(name_words)
        
        # Pattern 4: Look for names in context like "his name is [name]" or similar
        if not name:
            name_patterns = [
                r'(?:name\s+is|called|named)\s+(\w+(?:\s+\w+)?)',
                r'(\w+(?:\s+\w+)?)\s+(?:with|email|phone)'
            ]
            for pattern in name_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    candidate = match.group(1).strip()
                    name_words = [word for word in candidate.split() if word.lower() not in ['new', 'user', 'contact', 'his', 'her', 'the', 'a', 'also', 'with', 'number', 'email', 'phone']]
                    if name_words:
                        name = ' '.join(name_words)
                        break
        
        if name:
            # Clean up and capitalize the name
            name = ' '.join(word.capitalize() for word in name.split())
            if name:
                info['name'] = name
        
        # Extract company/work information
        company_match = re.search(r'(?:works?\s+at|employed\s+at|company)[:\s]+([^,\n]+)', text_lower)
        if company_match:
            info['company'] = company_match.group(1).strip()
        
        return info

    def process_input(self, user_input: str) -> Dict:
        """Process natural language input with flexible pattern matching"""
        input_lower = user_input.lower()
        
        # Show contacts
        if any(x in input_lower for x in ['show contacts', 'list contacts', 'get contacts', 'who do i know', 'show my contacts', 'all contacts']):
            contacts = self.get_contacts()
            if not contacts:
                return {"message": "No contacts found. Try adding some contacts first!"}
            return {
                "status": "success",
                "message": f"Found {len(contacts)} contacts:",
                "contacts": contacts
            }

        # Search contacts
        if any(x in input_lower for x in ['search contacts', 'find contact', 'search for']):
            # Extract search query
            search_query = None
            for phrase in ['search contacts', 'find contact', 'search for']:
                if phrase in input_lower:
                    parts = input_lower.split(phrase, 1)
                    if len(parts) > 1:
                        search_query = parts[1].strip()
                        break
            
            if search_query:
                results = self.vault_manager.search_contacts(search_query)
                return {
                    "status": "success",
                    "message": f"Found {len(results)} contacts matching '{search_query}':",
                    "contacts": results
                }
            else:
                return {"error": "Please specify what to search for (e.g., 'search contacts for John')"}

        # Show all memories
        if any(x in input_lower for x in ['show all memories', 'list all memories', 'all memories']):
            memories = self.vault_manager.get_all_memories()
            return {
                "status": "success",
                "message": f"Found {len(memories)} memories:",
                "memories": memories
            }

        # Show all reminders
        if any(x in input_lower for x in ['show reminders', 'list reminders', 'all reminders', 'my reminders']):
            reminders = self.get_reminders()
            return {
                "status": "success",
                "message": f"Found {len(reminders)} reminders:",
                "reminders": reminders
            }

        # Add contact - much more flexible patterns
        add_patterns = [
            'add contact', 'new contact', 'create contact', 'add new',
            'add user', 'add person', 'add someone'
        ]
        
        # Check if this is an add contact request
        is_add_request = (
            any(pattern in input_lower for pattern in add_patterns) or
            (input_lower.startswith('add ') and any(word in input_lower for word in ['email', 'phone', 'name', 'as'])) or
            re.search(r'add\s+\w+', input_lower)  # Simple "add [name]" pattern
        )
        
        if is_add_request:
            contact_data = self._extract_contact_info(user_input)
            if contact_data and contact_data.get('name'):
                return self.add_contact(contact_data)
            else:
                return {"error": "Could not extract contact information. Please provide at least a name. Try: 'Add John Smith with email john@example.com'"}

        # Add memory
        if any(word in input_lower for word in ['remember', 'memory', 'note', 'met']):
            # Try to find contact name and memory text
            contact_name = None
            memory_text = user_input
            
            # Look for contact name after common phrases
            for phrase in ['about', 'with', 'met', 'saw']:
                if phrase in input_lower:
                    parts = input_lower.split(phrase, 1)
                    if len(parts) > 1:
                        # Get the first word after the phrase as the name
                        contact_name = parts[1].strip().split()[0].strip('.,!?')
                        memory_text = parts[1].strip()
                        break
            
            if not contact_name:
                return {"error": "Could not determine who this memory is about. Please mention their name."}
                
            return self.add_memory(contact_name, memory_text)

        # Get memories for contact
        if 'memories' in input_lower or 'remember about' in input_lower:
            contact_name = None
            if 'about' in input_lower:
                parts = input_lower.split('about', 1)
                if len(parts) > 1:
                    contact_name = parts[1].strip().split()[0].strip('.,!?')
            
            if not contact_name:
                return {"error": "Please specify whose memories you want to see (e.g., 'memories about John')"}
                
            return {'memories': self.get_memories(contact_name)}

        # Set reminder
        if any(word in input_lower for word in ['remind', 'reminder', 'schedule']):
            # Try to extract reminder details
            match = re.search(r'(?:remind|remember)\s+(?:me\s+)?(?:to\s+)?(.+?)(?:\s+(?:on|by|at)\s+(.+))?$', input_lower)
            if match:
                task = match.group(1)
                date_str = match.group(2) if match.group(2) else None
                
                # Try to extract contact name from task
                contact_name = None
                for word in ['with', 'for', 'about']:
                    if word in task:
                        parts = task.split(word, 1)
                        if len(parts) > 1:
                            contact_name = parts[1].strip().split()[0].strip('.,!?')
                            task = parts[0].strip()
                            break
                
                if not contact_name:
                    return {"error": "Could not determine who this reminder is for. Please specify a contact."}
                
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
                    return self.set_reminder(contact_name, task, date)
                except ValueError:
                    return {"error": "Could not understand the date format. Please use YYYY-MM-DD"}
                    
            return {"error": "Could not understand the reminder details. Please specify what to remember."}

        return {
            "error": "I'm not sure what you want to do. Try:\n"
            "- Add [name] as a contact\n"
            "- Add [name] with email [email@example.com]\n"
            "- Remember that I met [name] at [place]\n"
            "- Remind me to call [name] on [date]\n"
            "- Show my contacts\n"
            "- Search contacts for [query]\n"
            "- Show memories about [name]\n"
            "- Show all memories\n"
            "- Show reminders"
        }

    def add_contact(self, contact_data: Dict) -> Dict:
        """Add or update a contact using vault storage"""
        # Extract name from various possible inputs
        name = None
        if 'name' in contact_data:
            name = contact_data['name']
        elif 'full_name' in contact_data:
            name = contact_data['full_name']
        elif any(k for k in contact_data.keys() if 'name' in k.lower()):
            # Find any key containing 'name'
            name_key = next(k for k in contact_data.keys() if 'name' in k.lower())
            name = contact_data[name_key]
            
        if not name:
            # Try to extract a name from any string value in the data
            for value in contact_data.values():
                if isinstance(value, str) and len(value.split()) <= 4:  # Allow up to 4 words for names
                    name = value
                    break
                    
        if not name:
            return {"error": "Could not determine contact name from input"}
            
        # Standardize the name format
        name = " ".join(name.split())  # Normalize whitespace
        contact_id = name.lower().replace(' ', '_')
        
        # Check for existing contact
        existing_contact = self.vault_manager.get_contact(contact_id)
        
        if existing_contact:
            # Update existing contact
            existing_contact['updated_at'] = datetime.now().isoformat()
            # Update details
            for key, value in contact_data.items():
                if key not in ['id', 'name', 'created_at', 'updated_at']:
                    if 'details' not in existing_contact:
                        existing_contact['details'] = {}
                    existing_contact['details'][key] = value
            contact_record = existing_contact
        else:
            # Create new contact
            contact_record = {
                "id": contact_id,
                "name": name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "details": {}  # Store additional info here
            }
            
            # Add all other data to details
            for key, value in contact_data.items():
                if key not in ['id', 'name', 'created_at', 'updated_at']:
                    contact_record['details'][key] = value
                
        # Store in vault using vault manager
        self.vault_manager.store_contact(contact_record)
        
        return {
            "status": "success", 
            "message": "Contact added successfully",
            "contact": {
                "name": name,
                "details": contact_record['details']
            }
        }

    def get_contacts(self) -> List[Dict]:
        """Get all contacts from vault storage"""
        try:
            return self.vault_manager.get_all_contacts()
        except Exception as e:
            print(f"Error retrieving contacts: {str(e)}")
            return []

    def add_memory(self, contact_name: str, summary: str) -> Dict:
        """Add a memory for a contact using vault storage"""
        memory_id = str(uuid.uuid4())
        memory_data = {
            "id": memory_id,
            "contact_name": contact_name,
            "summary": summary,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            self.vault_manager.store_memory(memory_data)
            return {
                "status": "success", 
                "message": f"Memory added for {contact_name}",
                "memory": memory_data
            }
        except Exception as e:
            return {"error": f"Failed to store memory: {str(e)}"}

    def get_memories(self, contact_name: str) -> List[Dict]:
        """Get memories for a contact from vault storage"""
        try:
            return self.vault_manager.get_memories_for_contact(contact_name)
        except Exception as e:
            print(f"Error retrieving memories: {str(e)}")
            return []

    def set_reminder(self, contact_name: str, title: str, date: datetime) -> Dict:
        """Set a reminder for a contact using vault storage"""
        reminder_id = str(uuid.uuid4())
        reminder_data = {
            "id": reminder_id,
            "contact_name": contact_name,
            "title": title,
            "date": date.isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        try:
            self.vault_manager.store_reminder(reminder_data)
            return {
                "status": "success",
                "message": f"Reminder set for {contact_name}",
                "reminder": reminder_data
            }
        except Exception as e:
            return {"error": f"Failed to store reminder: {str(e)}"}

    def get_reminders(self, contact_name: Optional[str] = None) -> List[Dict]:
        """Get reminders for a contact or all reminders from vault storage"""
        try:
            if contact_name:
                return self.vault_manager.get_reminders_for_contact(contact_name)
            else:
                return self.vault_manager.get_all_reminders()
        except Exception as e:
            print(f"Error retrieving reminders: {str(e)}")
            return []
