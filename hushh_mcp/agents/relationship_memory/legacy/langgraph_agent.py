"""
LangGraph-based Relationship Memory Agent with AI-powered input parsing and full Hush MCP compliance.
Uses state management and vault integration for persistent storage.
"""

from typing import Dict, List, Optional, TypedDict, Literal, Annotated
from datetime import datetime
import json
import uuid
import re
from dataclasses import dataclass

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Hush MCP imports
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.types import VaultKey, VaultRecord, EncryptedPayload, UserID, AgentID, ConsentScope
from hushh_mcp.consent.token import HushhConsentToken

# ==================== Pydantic Models for Structured Output ====================

class ContactInfo(BaseModel):
    """Structured contact information extracted from user input"""
    name: Optional[str] = Field(None, description="Full name of the contact")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company or workplace")
    location: Optional[str] = Field(None, description="Location or address")
    notes: Optional[str] = Field(None, description="Additional notes or context")

class MemoryInfo(BaseModel):
    """Structured memory information"""
    contact_name: str = Field(..., description="Name of the person this memory is about")
    summary: str = Field(..., description="Summary of the memory or interaction")
    location: Optional[str] = Field(None, description="Where this memory took place")
    date: Optional[str] = Field(None, description="When this memory occurred")
    tags: List[str] = Field(default_factory=list, description="Tags to categorize this memory")

class ReminderInfo(BaseModel):
    """Structured reminder information"""
    contact_name: str = Field(..., description="Name of the person this reminder is about")
    title: str = Field(..., description="What to be reminded about")
    date: str = Field(..., description="When to be reminded (YYYY-MM-DD format)")
    priority: Literal["low", "medium", "high"] = Field("medium", description="Priority level")

class UserIntent(BaseModel):
    """Parsed user intent and extracted information"""
    action: Literal["add_contact", "add_memory", "add_reminder", "show_contacts", "show_memories", "show_reminders", "search_contacts", "unknown"] = Field(..., description="The intended action")
    confidence: float = Field(..., description="Confidence level (0.0 to 1.0)")
    contact_info: Optional[ContactInfo] = Field(None, description="Contact information if adding/updating contact")
    memory_info: Optional[MemoryInfo] = Field(None, description="Memory information if adding memory")
    reminder_info: Optional[ReminderInfo] = Field(None, description="Reminder information if setting reminder")
    search_query: Optional[str] = Field(None, description="Search query if searching")
    error_message: Optional[str] = Field(None, description="Error message if input cannot be parsed")

# ==================== LangGraph State ====================

class RelationshipMemoryState(TypedDict):
    """State for the relationship memory agent"""
    user_input: str
    user_id: str
    agent_id: str
    vault_key: str
    
    # Parsed information
    parsed_intent: Optional[UserIntent]
    
    # Processing results
    contacts: List[Dict]
    memories: List[Dict]
    reminders: List[Dict]
    
    # Response
    response: Dict
    
    # Error handling
    error: Optional[str]
    
    # Conversation context
    conversation_history: List[Dict]

# ==================== Vault Manager ====================

class HushhVaultManager:
    """Manages vault operations with full MCP compliance"""
    
    def __init__(self, user_id: str, vault_key: str, agent_id: str = "relationship_memory"):
        self.user_id = UserID(user_id)
        self.agent_id = AgentID(agent_id)
        self.vault_key = vault_key
        
        # Define vault keys for different data types
        self.contacts_key = VaultKey(user_id=self.user_id, scope=ConsentScope.VAULT_WRITE_CONTACTS)
        self.memories_key = VaultKey(user_id=self.user_id, scope=ConsentScope.VAULT_WRITE_MEMORY)
        self.reminders_key = VaultKey(user_id=self.user_id, scope=ConsentScope.VAULT_WRITE_REMINDER)
        
        # In-memory storage (replace with actual vault in production)
        self._contacts = []
        self._memories = []
        self._reminders = []
    
    def _create_vault_record(self, key: VaultKey, data: dict) -> VaultRecord:
        """Create an encrypted vault record"""
        encrypted = encrypt_data(json.dumps(data), self.vault_key)
        return VaultRecord(
            key=key,
            data=encrypted,
            agent_id=self.agent_id,
            created_at=int(datetime.now().timestamp() * 1000),
            metadata={"data_type": key.scope.value}
        )
    
    def _decrypt_vault_record(self, record: VaultRecord) -> dict:
        """Decrypt and load data from vault record"""
        decrypted = decrypt_data(record.data, self.vault_key)
        return json.loads(decrypted)
    
    def store_contact(self, contact_data: Dict) -> str:
        """Store contact with MCP compliance"""
        contact_id = str(uuid.uuid4())
        contact_record = {
            "id": contact_id,
            "name": contact_data.get("name", ""),
            "email": contact_data.get("email"),
            "phone": contact_data.get("phone"),
            "company": contact_data.get("company"),
            "location": contact_data.get("location"),
            "notes": contact_data.get("notes"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Store in vault (encrypted)
        vault_record = self._create_vault_record(self.contacts_key, contact_record)
        
        # Store in memory for demo (replace with actual vault storage)
        self._contacts.append(contact_record)
        
        return contact_id
    
    def get_contacts(self) -> List[Dict]:
        """Retrieve all contacts"""
        return self._contacts
    
    def search_contacts(self, query: str) -> List[Dict]:
        """Search contacts by name, email, or company"""
        query_lower = query.lower()
        results = []
        for contact in self._contacts:
            if (query_lower in contact.get("name", "").lower() or
                query_lower in contact.get("email", "").lower() or
                query_lower in contact.get("company", "").lower()):
                results.append(contact)
        return results
    
    def store_memory(self, memory_data: Dict) -> str:
        """Store memory with MCP compliance"""
        memory_id = str(uuid.uuid4())
        memory_record = {
            "id": memory_id,
            "contact_name": memory_data.get("contact_name", ""),
            "summary": memory_data.get("summary", ""),
            "location": memory_data.get("location"),
            "date": memory_data.get("date"),
            "tags": memory_data.get("tags", []),
            "created_at": datetime.now().isoformat()
        }
        
        vault_record = self._create_vault_record(self.memories_key, memory_record)
        self._memories.append(memory_record)
        
        return memory_id
    
    def get_memories(self, contact_name: Optional[str] = None) -> List[Dict]:
        """Retrieve memories, optionally filtered by contact"""
        if contact_name:
            return [m for m in self._memories if contact_name.lower() in m.get("contact_name", "").lower()]
        return self._memories
    
    def store_reminder(self, reminder_data: Dict) -> str:
        """Store reminder with MCP compliance"""
        reminder_id = str(uuid.uuid4())
        reminder_record = {
            "id": reminder_id,
            "contact_name": reminder_data.get("contact_name", ""),
            "title": reminder_data.get("title", ""),
            "date": reminder_data.get("date", ""),
            "priority": reminder_data.get("priority", "medium"),
            "created_at": datetime.now().isoformat(),
            "completed": False
        }
        
        vault_record = self._create_vault_record(self.reminders_key, reminder_record)
        self._reminders.append(reminder_record)
        
        return reminder_id
    
    def get_reminders(self, contact_name: Optional[str] = None) -> List[Dict]:
        """Retrieve reminders, optionally filtered by contact"""
        if contact_name:
            return [r for r in self._reminders if contact_name.lower() in r.get("contact_name", "").lower()]
        return [r for r in self._reminders if not r.get("completed", False)]

# ==================== LangGraph Nodes ====================

class RelationshipMemoryAgent:
    """LangGraph-based Relationship Memory Agent"""
    
    def __init__(self, user_id: str, vault_key: str, llm_model: str = "gemini-1.5-flash"):
        self.user_id = user_id
        self.vault_key = vault_key
        self.agent_id = "relationship_memory"
        
        # Load environment variables from main project folder
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        main_env_path = os.path.join(project_root, '.env')
        from dotenv import load_dotenv
        load_dotenv(main_env_path)
        
        # Initialize Gemini LLM for parsing
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.llm = ChatGoogleGenerativeAI(
            model=llm_model, 
            temperature=0,
            google_api_key=gemini_api_key
        )
        
        # Initialize vault manager
        self.vault_manager = HushhVaultManager(user_id, vault_key, self.agent_id)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(RelationshipMemoryState)
        
        # Add nodes
        workflow.add_node("parse_input", self._parse_input_node)
        workflow.add_node("process_contact", self._process_contact_node)
        workflow.add_node("process_memory", self._process_memory_node)
        workflow.add_node("process_reminder", self._process_reminder_node)
        workflow.add_node("retrieve_data", self._retrieve_data_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Define flow
        workflow.set_entry_point("parse_input")
        
        # Conditional routing based on parsed intent
        workflow.add_conditional_edges(
            "parse_input",
            self._route_based_on_intent,
            {
                "add_contact": "process_contact",
                "add_memory": "process_memory", 
                "add_reminder": "process_reminder",
                "retrieve": "retrieve_data",
                "error": "handle_error"
            }
        )
        
        # All processing nodes lead to response generation
        workflow.add_edge("process_contact", "generate_response")
        workflow.add_edge("process_memory", "generate_response")
        workflow.add_edge("process_reminder", "generate_response")
        workflow.add_edge("retrieve_data", "generate_response")
        workflow.add_edge("handle_error", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def _parse_input_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Parse user input using AI to extract intent and structured information"""
        
        system_prompt = """You are an expert at parsing user input for a relationship memory assistant.
        Extract the user's intent and any relevant information from their message.
        
        Possible actions:
        - add_contact: User wants to add a new contact
        - add_memory: User wants to record a memory about someone
        - add_reminder: User wants to set a reminder related to someone
        - show_contacts: User wants to see their contacts
        - show_memories: User wants to see memories
        - show_reminders: User wants to see reminders
        - search_contacts: User wants to search for specific contacts
        - unknown: Intent cannot be determined
        
        IMPORTANT: When the action is "add_contact", you MUST extract the contact information:
        - Extract the name from phrases like "add John Smith", "add alok as a contact"
        - Extract email from patterns like "email john@example.com", "with email user@domain.com"
        - Extract phone from patterns like "phone 123-456-7890", "with phone 9876543210"
        
        When the action is "add_memory", extract:
        - contact_name: Who the memory is about
        - summary: What the memory is about
        
        When the action is "add_reminder", extract:
        - contact_name: Who the reminder is for
        - title: What to be reminded about
        - date: When to be reminded (if mentioned)
        
        Be flexible with natural language variations. Examples:
        - "Add John Smith with email john@example.com" -> add_contact with name="John Smith", email="john@example.com"
        - "add alok as a contact with email 23b2223@iitb.ac.in" -> add_contact with name="Alok", email="23b2223@iitb.ac.in"
        - "Remember that I met Sarah at the conference" -> add_memory with contact_name="Sarah", summary="I met Sarah at the conference"
        - "Remind me to call Mike tomorrow" -> add_reminder with contact_name="Mike", title="call Mike"
        - "Show my contacts" -> show_contacts
        - "Who do I know at Google?" -> search_contacts with search_query="Google"
        """
        
        user_message = f"""Parse this user input and extract ALL relevant information:
        
        User input: "{state['user_input']}"
        
        Make sure to:
        1. Identify the correct action
        2. Extract ALL relevant data (names, emails, phones, etc.)
        3. Fill in the appropriate fields based on the action type
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        try:
            # Use structured output parsing
            structured_llm = self.llm.with_structured_output(UserIntent)
            parsed_intent = structured_llm.invoke(messages)
            
            # Debug: Print what was parsed
            print(f"🔍 Debug - Parsed action: {parsed_intent.action}")
            if parsed_intent.contact_info:
                print(f"🔍 Debug - Contact info: {parsed_intent.contact_info}")
            if parsed_intent.memory_info:
                print(f"🔍 Debug - Memory info: {parsed_intent.memory_info}")
            if parsed_intent.reminder_info:
                print(f"🔍 Debug - Reminder info: {parsed_intent.reminder_info}")
            
            state["parsed_intent"] = parsed_intent
            
        except Exception as e:
            print(f"❌ Parsing error: {e}")
            state["error"] = f"Failed to parse input: {str(e)}"
            state["parsed_intent"] = UserIntent(
                action="unknown",
                confidence=0.0,
                error_message=f"Parsing error: {str(e)}"
            )
        
        return state
    
    def _route_based_on_intent(self, state: RelationshipMemoryState) -> str:
        """Route to appropriate node based on parsed intent"""
        if state.get("error"):
            return "error"
        
        intent = state.get("parsed_intent")
        if not intent:
            return "error"
        
        action = intent.action
        
        if action == "add_contact":
            return "add_contact"
        elif action == "add_memory":
            return "add_memory"
        elif action == "add_reminder":
            return "add_reminder"
        elif action in ["show_contacts", "show_memories", "show_reminders", "search_contacts"]:
            return "retrieve"
        else:
            return "error"
    
    def _process_contact_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Process contact addition"""
        intent = state["parsed_intent"]
        
        # Check if we have contact info, if not try to extract from user input directly
        if not intent.contact_info or not intent.contact_info.name:
            # Fallback extraction from user input
            user_input = state["user_input"].lower()
            contact_data = self._extract_contact_fallback(state["user_input"])
            
            if not contact_data.get("name"):
                state["error"] = "Contact name is required"
                return state
        else:
            contact_data = {
                "name": intent.contact_info.name,
                "email": intent.contact_info.email,
                "phone": intent.contact_info.phone,
                "company": intent.contact_info.company,
                "location": intent.contact_info.location,
                "notes": intent.contact_info.notes
            }
        
        try:
            contact_id = self.vault_manager.store_contact(contact_data)
            
            state["response"] = {
                "status": "success",
                "action": "contact_added",
                "message": f"Successfully added {contact_data['name']} to your contacts",
                "contact_id": contact_id,
                "contact": contact_data
            }
            
        except Exception as e:
            state["error"] = f"Failed to add contact: {str(e)}"
        
        return state
    
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
        
        # Extract contact name - look for names mentioned
        # Pattern: "remember that [name]" or "remember [name]"
        name_match = re.search(r'remember\s+(?:that\s+)?([a-zA-Z\s]+?)\s+(?:is|was|loves|likes|works|lives|from)', text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()
            memory_data['contact_name'] = ' '.join(word.capitalize() for word in name.split())
        
        # Extract the summary - everything after contact name or "remember that"
        if 'remember that' in text.lower():
            summary_start = text.lower().find('remember that') + len('remember that')
            summary = text[summary_start:].strip()
        elif 'remember' in text.lower():
            summary_start = text.lower().find('remember') + len('remember')
            summary = text[summary_start:].strip()
        else:
            summary = text
        
        memory_data['summary'] = summary
        
        # Extract location if mentioned
        location_patterns = [
            r'at\s+([a-zA-Z\s]+)',
            r'in\s+([a-zA-Z\s]+)',
            r'from\s+([a-zA-Z\s]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Filter out common non-location words
                if location.lower() not in ['the', 'a', 'an', 'that', 'this', 'he', 'she']:
                    memory_data['location'] = location
                    break
        
        return memory_data
    
    def _extract_reminder_fallback(self, user_input: str) -> dict:
        """Fallback reminder extraction using regex patterns"""
        import re
        
        reminder_data = {}
        text = user_input.strip()
        
        # Extract contact name - look for names after "call", "meet", "email", etc.
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
    
    def _process_memory_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Process memory addition"""
        intent = state["parsed_intent"]
        
        # Use fallback extraction if LLM didn't extract memory info
        if not intent.memory_info:
            memory_data = self._extract_memory_fallback(state["user_input"])
            
            if not memory_data.get("contact_name") and not memory_data.get("summary"):
                state["error"] = "Memory information is required - please specify what to remember about whom"
                return state
        else:
            memory_data = {
                "contact_name": intent.memory_info.contact_name,
                "summary": intent.memory_info.summary,
                "location": intent.memory_info.location,
                "date": intent.memory_info.date,
                "tags": intent.memory_info.tags
            }

        try:
            memory_id = self.vault_manager.store_memory(memory_data)
            
            contact_name = memory_data.get('contact_name', 'someone')
            state["response"] = {
                "status": "success",
                "action": "memory_added",
                "message": f"Successfully recorded memory about {contact_name}",
                "memory_id": memory_id,
                "memory": memory_data
            }
            
        except Exception as e:
            state["error"] = f"Failed to add memory: {str(e)}"
        
        return state
    
    def _process_reminder_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Process reminder creation"""
        intent = state["parsed_intent"]
        
        # Use fallback extraction if LLM didn't extract reminder info
        if not intent.reminder_info:
            reminder_data = self._extract_reminder_fallback(state["user_input"])
            
            if not reminder_data.get("title"):
                state["error"] = "Reminder information is required - please specify what you want to be reminded about"
                return state
        else:
            reminder_data = {
                "contact_name": intent.reminder_info.contact_name,
                "title": intent.reminder_info.title,
                "date": intent.reminder_info.date,
                "priority": intent.reminder_info.priority
            }

        try:
            reminder_id = self.vault_manager.store_reminder(reminder_data)
            
            contact_name = reminder_data.get('contact_name', 'someone')
            state["response"] = {
                "status": "success",
                "action": "reminder_added",
                "message": f"Successfully set reminder: {reminder_data['title']}",
                "reminder_id": reminder_id,
                "reminder": reminder_data
            }
            
        except Exception as e:
            state["error"] = f"Failed to add reminder: {str(e)}"
        
        return state
    
    def _retrieve_data_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Retrieve and return requested data"""
        intent = state["parsed_intent"]
        action = intent.action
        
        try:
            if action == "show_contacts":
                contacts = self.vault_manager.get_contacts()
                state["response"] = {
                    "status": "success",
                    "action": "contacts_retrieved",
                    "message": f"Found {len(contacts)} contacts",
                    "contacts": contacts
                }
            
            elif action == "show_memories":
                memories = self.vault_manager.get_memories()
                state["response"] = {
                    "status": "success",
                    "action": "memories_retrieved",
                    "message": f"Found {len(memories)} memories",
                    "memories": memories
                }
            
            elif action == "show_reminders":
                reminders = self.vault_manager.get_reminders()
                state["response"] = {
                    "status": "success",
                    "action": "reminders_retrieved",
                    "message": f"Found {len(reminders)} reminders",
                    "reminders": reminders
                }
            
            elif action == "search_contacts":
                if intent.search_query:
                    results = self.vault_manager.search_contacts(intent.search_query)
                    state["response"] = {
                        "status": "success",
                        "action": "contacts_searched",
                        "message": f"Found {len(results)} contacts matching '{intent.search_query}'",
                        "contacts": results,
                        "search_query": intent.search_query
                    }
                else:
                    state["error"] = "Search query is required"
            
        except Exception as e:
            state["error"] = f"Failed to retrieve data: {str(e)}"
        
        return state
    
    def _handle_error_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Handle errors and provide helpful feedback"""
        error_msg = state.get("error", "Unknown error occurred")
        
        state["response"] = {
            "status": "error",
            "action": "error",
            "message": error_msg,
            "suggestions": [
                "Try: 'Add John Smith with email john@example.com'",
                "Try: 'Remember that I met Sarah at the conference'",
                "Try: 'Remind me to call Mike on 2024-03-15'",
                "Try: 'Show my contacts'",
                "Try: 'Search for contacts at Google'"
            ]
        }
        
        return state
    
    def _generate_response_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Generate final response with conversation context"""
        # Add to conversation history
        if "conversation_history" not in state:
            state["conversation_history"] = []
        
        state["conversation_history"].append({
            "user_input": state["user_input"],
            "response": state.get("response", {}),
            "timestamp": datetime.now().isoformat()
        })
        
        return state
    
    def process_input(self, user_input: str) -> Dict:
        """Main entry point for processing user input"""
        initial_state = RelationshipMemoryState(
            user_input=user_input,
            user_id=self.user_id,
            agent_id=self.agent_id,
            vault_key=self.vault_key,
            parsed_intent=None,
            contacts=[],
            memories=[],
            reminders=[],
            response={},
            error=None,
            conversation_history=[]
        )
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        return final_state.get("response", {"status": "error", "message": "No response generated"})
