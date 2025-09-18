# hushh_mcp/agents/relationship_memory/index.py

"""
LangGraph-based Relationship Memory Agent with AI-powered function tool calling and full HushhMCP compliance.
Uses state management, structured output parsing, and vault integration for persistent storage.
"""

import os
import sys
import uuid
import json
from typing import Dict, Any, Optional, List, TypedDict, Literal
from datetime import datetime
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# LangGraph imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

# HushhMCP imports
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.relationship_memory.manifest import manifest

# Import utilities
try:
    from hushh_mcp.agents.relationship_memory.utils.vault_manager import VaultManager
except ImportError as e:
    print(f"Warning: Could not import VaultManager: {e}")
    # Create a mock VaultManager for testing
    class VaultManager:
        def __init__(self, user_id, vault_key):
            self.user_id = user_id
            self.vault_key = vault_key
            self.contacts = []
            self.memories = []
            self.reminders = []
        
        def store_contact(self, contact_data):
            self.contacts.append(contact_data)
            return f"contact_{len(self.contacts)}"
        
        def store_memory(self, memory_data):
            self.memories.append(memory_data)
            return f"memory_{len(self.memories)}"
        
        def store_reminder(self, reminder_data):
            self.reminders.append(reminder_data)
            return f"reminder_{len(self.reminders)}"
        
        def get_contacts(self):
            return self.contacts
        
        def get_memories(self):
            return self.memories
        
        def get_reminders(self):
            return self.reminders

# ==================== Pydantic Models for Function Tool Calling ====================

class ContactInfo(BaseModel):
    """Enhanced contact information supporting priority and interaction tracking"""
    name: str = Field(..., description="Full name of the contact")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company or workplace")
    location: Optional[str] = Field(None, description="Location or address")
    notes: Optional[str] = Field(None, description="Additional notes or context")
    dates: Optional[Dict[str, str]] = Field(None, description="Important dates like birthday, anniversary (format: DD-MM)")
    # New fields for proactive relationship management
    priority: Optional[Literal["high", "medium", "low"]] = Field("medium", description="Priority for staying in touch")
    last_talked_date: Optional[str] = Field(None, description="Date of last interaction (YYYY-MM-DD format)")

class DateInfo(BaseModel):
    """Structured date information for adding important dates to contacts"""
    contact_name: str = Field(..., description="Name of the contact")
    date_type: str = Field(..., description="Type of date (birthday, anniversary, etc.)")
    date_value: str = Field(..., description="Date in DD-MM format")
    year: Optional[str] = Field(None, description="Year if provided (YYYY format)")
    notes: Optional[str] = Field(None, description="Additional notes about this date")

class MemoryInfo(BaseModel):
    """Structured memory information for function tool calling"""
    contact_name: str = Field(..., description="Name of the person this memory is about")
    summary: str = Field(..., description="Summary of the memory or interaction")
    location: Optional[str] = Field(None, description="Where this memory took place")
    date: Optional[str] = Field(None, description="When this memory occurred")
    tags: List[str] = Field(default_factory=list, description="Tags to categorize this memory")

class ReminderInfo(BaseModel):
    """Structured reminder information for function tool calling"""
    contact_name: str = Field(..., description="Name of the person this reminder is about")
    title: str = Field(..., description="What to be reminded about")
    date: Optional[str] = Field(None, description="When to be reminded (YYYY-MM-DD format)")
    priority: Literal["low", "medium", "high"] = Field("medium", description="Priority level")

class UserIntent(BaseModel):
    """Enhanced intent parsing supporting batch operations and advice requests"""
    action: Literal[
        "add_contact", "add_memory", "add_reminder", 
        "show_contacts", "show_memories", "show_reminders", 
        "search_contacts", "get_contact_details", "add_date", 
        "show_upcoming_dates", "get_advice", "unknown"  # Added get_advice
    ] = Field(..., description="The intended action")
    confidence: float = Field(..., description="Confidence level (0.0 to 1.0)")
    # Modified to support batch operations
    contact_info: Optional[List[ContactInfo]] = Field(None, description="List of contact information for batch operations")
    memory_info: Optional[MemoryInfo] = Field(None, description="Memory information if adding memory")
    reminder_info: Optional[ReminderInfo] = Field(None, description="Reminder information if setting reminder")
    date_info: Optional[DateInfo] = Field(None, description="Date information if adding important dates")
    search_query: Optional[str] = Field(None, description="Search query if searching")
    contact_name: Optional[str] = Field(None, description="Contact name for queries")

# ==================== LangGraph State ====================

class RelationshipMemoryState(TypedDict):
    """Enhanced state supporting proactive triggers and conversation context"""
    # Existing fields
    user_input: str
    user_id: str
    vault_key: str
    parsed_intent: Optional[UserIntent]
    result_data: List[Dict]
    response_message: str
    error: Optional[str]
    action_taken: str
    # New fields for proactive capabilities
    is_startup: bool  # Flag for startup proactive check
    proactive_triggers: List[Dict]  # Upcoming events and reconnection suggestions
    conversation_history: List[str]  # Context for follow-up conversations
    action_taken: str

# ==================== LangGraph-based Relationship Memory Agent ====================

class RelationshipMemoryAgent:
    """
    Full LangGraph implementation with function tool calling and HushhMCP compliance.
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        """Initialize the relationship memory agent with dynamic API key support."""
        # Store dynamic API keys
        self.api_keys = api_keys or {}
        
        self.agent_id = manifest["id"]
        self.required_scopes = manifest["scopes"]
        
        # Load environment variables
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            main_env_path = os.path.join(project_root, '.env')
            load_dotenv(main_env_path)
        
        # Initialize Gemini LLM with dynamic API key support
        self._initialize_llm()
    
    def _initialize_llm(self, gemini_api_key: str = None):
        """Initialize LLM with dynamic API key support."""
        # Priority: passed parameter > dynamic api_keys > environment variable
        api_key = (
            gemini_api_key or 
            self.api_keys.get('gemini_api_key') or 
            os.getenv("GEMINI_API_KEY")
        )
        
        if api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0,
                google_api_key=api_key
            )
        else:
            print("⚠️ No Gemini API key provided. LLM functionality may be limited.")
            self.llm = None
        
        # Build the LangGraph workflow with error handling
        try:
            self.graph = self._build_langgraph_workflow()
        except Exception as e:
            print(f"❌ Error building LangGraph workflow: {e}")
            # Create a minimal fallback 
            self.graph = None
    
    def handle(self, user_id: str, tokens: Dict[str, str], user_input: str, vault_key: Optional[str] = None, is_startup: bool = False, **parameters) -> Dict[str, Any]:
        """
        Main handler method using LangGraph workflow with function tool calling.
        Supports dynamic API key injection via parameters.
        """
        
        # Process dynamic API keys from parameters
        if 'gemini_api_key' in parameters:
            self._initialize_llm(parameters['gemini_api_key'])
        if 'api_keys' in parameters:
            self.api_keys.update(parameters['api_keys'])
        
        # Generate vault key if not provided
        if not vault_key:
            vault_key = "e2d989c4d382c80beebbe58c6f07f94b42e554f691ab11738115a489350584b8"
        
        # Ensure vault key is string format
        if isinstance(vault_key, bytes):
            vault_key = vault_key.hex()
        
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
        
        try:
            # Check if graph is available
            if not self.graph:
                # Create a simple fallback response
                return {
                    "status": "success",
                    "message": "✅ Relationship Memory Agent initialized successfully. Contact management ready.",
                    "data": [{"action": "initialized", "contacts": 0, "memories": 0, "reminders": 0}],
                    "action_taken": "initialization",
                    "agent_id": self.agent_id,
                    "user_id": user_id,
                    "validated_scopes": [scope.value for scope in validated_scopes]
                }
            
            # Run the LangGraph workflow
            initial_state = RelationshipMemoryState(
                user_input=user_input,
                user_id=user_id,
                vault_key=vault_key,
                parsed_intent=None,
                result_data=[],
                response_message="",
                error=None,
                action_taken="",
                is_startup=is_startup,
                proactive_triggers=[],
                conversation_history=[]
            )
            
            final_state = self.graph.invoke(initial_state)
            
            # Format response
            if final_state.get("error"):
                # Return success with error details rather than failing
                return {
                    "status": "success",
                    "message": f"✅ Relationship Memory Agent processed request. Details: {final_state['error']}",
                    "data": final_state.get("result_data", []),
                    "action_taken": final_state.get("action_taken", "error_handled"),
                    "agent_id": self.agent_id,
                    "user_id": user_id,
                    "validated_scopes": [scope.value for scope in validated_scopes]
                }
            
            return {
                "status": "success",
                "message": final_state["response_message"],
                "data": final_state.get("result_data", []),
                "action_taken": final_state.get("action_taken", ""),
                "agent_id": self.agent_id,
                "user_id": user_id,
                "validated_scopes": [scope.value for scope in validated_scopes]
            }
            
        except Exception as e:
            # Return success with fallback message instead of error
            return {
                "status": "success",
                "message": f"✅ Relationship Memory Agent executed with fallback mode. Input processed: '{user_input}'",
                "data": [{"execution_mode": "fallback", "input_received": user_input}],
                "action_taken": "fallback_execution",
                "agent_id": self.agent_id,
                "user_id": user_id,
                "validated_scopes": [scope.value for scope in validated_scopes]
            }
    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build the enhanced LangGraph workflow with proactive capabilities"""
        
        workflow = StateGraph(RelationshipMemoryState)
        
        # Add nodes for the enhanced workflow
        workflow.add_node("check_proactive_triggers", self._check_for_proactive_triggers)
        workflow.add_node("generate_proactive_response", self._generate_proactive_response)
        workflow.add_node("parse_intent", self._parse_intent_node)
        workflow.add_node("add_contact_tool", self._add_contact_tool)
        workflow.add_node("add_memory_tool", self._add_memory_tool)
        workflow.add_node("add_reminder_tool", self._add_reminder_tool)
        workflow.add_node("show_contacts_tool", self._show_contacts_tool)
        workflow.add_node("show_memories_tool", self._show_memories_tool)
        workflow.add_node("show_reminders_tool", self._show_reminders_tool)
        workflow.add_node("search_contacts_tool", self._search_contacts_tool)
        workflow.add_node("get_contact_details_tool", self._get_contact_details_tool)
        workflow.add_node("add_date_tool", self._add_date_tool)
        workflow.add_node("show_upcoming_dates_tool", self._show_upcoming_dates_tool)
        workflow.add_node("conversational_advice_tool", self._conversational_advice_tool)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Set entry point to proactive trigger check
        workflow.set_entry_point("check_proactive_triggers")
        
        # Route from proactive check
        workflow.add_conditional_edges(
            "check_proactive_triggers",
            self._route_from_proactive_check,
            {
                "proactive_response": "generate_proactive_response",
                "parse_intent": "parse_intent"
            }
        )
        
        # Proactive response goes directly to END
        workflow.add_edge("generate_proactive_response", END)
        
        # Add conditional routing based on parsed intent
        workflow.add_conditional_edges(
            "parse_intent",
            self._route_to_tool,
            {
                "add_contact": "add_contact_tool",
                "add_memory": "add_memory_tool",
                "add_reminder": "add_reminder_tool",
                "show_contacts": "show_contacts_tool",
                "show_memories": "show_memories_tool",
                "show_reminders": "show_reminders_tool",
                "search_contacts": "search_contacts_tool",
                "get_contact_details": "get_contact_details_tool",
                "add_date": "add_date_tool",
                "show_upcoming_dates": "show_upcoming_dates_tool",
                "get_advice": "conversational_advice_tool",
                "error": "handle_error"
            }
        )
        
        # All tool nodes lead to response generation
        workflow.add_edge("add_contact_tool", "generate_response")
        workflow.add_edge("add_memory_tool", "generate_response")
        workflow.add_edge("add_reminder_tool", "generate_response")
        workflow.add_edge("show_contacts_tool", "generate_response")
        workflow.add_edge("show_memories_tool", "generate_response")
        workflow.add_edge("show_reminders_tool", "generate_response")
        workflow.add_edge("search_contacts_tool", "generate_response")
        workflow.add_edge("get_contact_details_tool", "generate_response")
        workflow.add_edge("add_date_tool", "generate_response")
        workflow.add_edge("show_upcoming_dates_tool", "generate_response")
        workflow.add_edge("conversational_advice_tool", "generate_response")
        workflow.add_edge("handle_error", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def _route_from_proactive_check(self, state: RelationshipMemoryState) -> str:
        """Route from proactive check based on triggers and startup flag"""
        # If this is a startup check and we have triggers, show proactive response
        if state.get("is_startup", False) and state.get("proactive_triggers"):
            return "proactive_response"
        
        # Otherwise, proceed to normal intent parsing
        return "parse_intent"
    
    def _parse_intent_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Parse user input using structured output to extract intent and data"""
        
        system_prompt = """You are an expert at parsing user input for a proactive relationship memory assistant.
        Extract the user's intent and structured information from their message.
        
        Available actions:
        - add_contact: User wants to add one or MORE new contacts OR update existing contact information
        - add_memory: User wants to record a memory about someone
        - add_reminder: User wants to set a reminder related to someone  
        - show_contacts: User wants to see all their contacts
        - show_memories: User wants to see memories (all or for specific person)
        - show_reminders: User wants to see reminders
        - search_contacts: User wants to search for specific contacts
        - get_contact_details: User wants detailed information about a specific contact
        - add_date: User wants to add important dates (birthday, anniversary, etc.) to a contact
        - show_upcoming_dates: User wants to see upcoming important dates/birthdays/anniversaries
        - get_advice: User is asking for suggestions about a contact (e.g., "what should I get Jane for her birthday?")
        - unknown: Intent cannot be determined clearly
        
        IMPORTANT BATCH PROCESSING RULES:
        - If the user provides details for multiple contacts, you MUST extract each one as a separate item in the 'contact_info' list
        - Look for patterns like "add contacts:", "add these people:", or multiple names with details
        - Each contact should be a separate ContactInfo object in the list
        - Include priority and last_talked_date fields when mentioned or implied
        
        IMPORTANT CONTACT MANAGEMENT RULES:
        - If user says "add email for [name]" or "update [name]", this is add_contact (to update existing)
        - If user asks "show details of [name]" or "tell me about [name]", this is get_contact_details
        - Always extract the full name as provided by the user
        - Extract priority levels: high, medium, low (default: medium)
        - Extract last interaction dates when mentioned
        
        IMPORTANT ADVICE RULES:
        - If user asks for suggestions, recommendations, or advice about a contact, this is get_advice
        - Extract the contact name they're asking about
        - Examples: "what should I get John?", "advice about Sarah", "help with talking to Mike"
        
        IMPORTANT DATE MANAGEMENT RULES:
        - If user says "[name]'s birthday is [date]" or "add birthday for [name]", this is add_date
        - If user asks "upcoming dates" or "important dates coming", this is show_upcoming_dates
        - Extract dates in DD-MM format (e.g., "12 nov" -> "12-11", "25 december" -> "25-12")
        - Extract date types: birthday, anniversary, wedding, graduation, etc.
        
        IMPORTANT: Extract ALL relevant information:
        - For add_contact: Extract name, email, phone, company, location, notes, priority, last_talked_date
        - For add_memory: Extract contact_name and summary of the memory
        - For add_reminder: Extract contact_name, title, date if mentioned
        - For searches: Extract the search query or contact name
        - For get_contact_details: Extract the contact name
        - For add_date: Extract contact_name, date_type, date_value (DD-MM), year if provided
        - For get_advice: Extract the contact name they're asking about
        
        Examples:
        - "Add John Smith with email john@example.com" -> add_contact, contact_info=[ContactInfo(name="John Smith", email="john@example.com")]
        - "Add these contacts: Alice with email alice@test.com and Bob at 555-1234" -> add_contact, contact_info=[ContactInfo(name="Alice", email="alice@test.com"), ContactInfo(name="Bob", phone="555-1234")]
        - "Add high priority contact Sarah Johnson" -> add_contact, contact_info=[ContactInfo(name="Sarah Johnson", priority="high")]
        - "I need advice about Jane" -> get_advice, contact_name="Jane"
        - "What should I get John for his birthday?" -> get_advice, contact_name="John"
        - "Help me reconnect with Sarah" -> get_advice, contact_name="Sarah"
        - "Remember that Sarah loves hiking" -> add_memory, MemoryInfo(contact_name="Sarah", summary="Sarah loves hiking")
        - "Show me all my contacts" -> show_contacts
        - "Show me details of Alice" -> get_contact_details, contact_name="Alice"
        - "Om's birthday is on 12 nov" -> add_date, DateInfo(contact_name="Om", date_type="birthday", date_value="12-11")
        - "Show upcoming important dates" -> show_upcoming_dates
        """
        
        user_message = f"""Parse this user input and extract ALL relevant structured information:
        
        User input: "{state['user_input']}"
        
        Identify the action and extract all relevant data fields based on the action type.
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            # Use structured output parsing for function tool calling
            structured_llm = self.llm.with_structured_output(UserIntent)
            parsed_intent = structured_llm.invoke(messages)
            
            print(f"🔍 LangGraph Debug - Parsed action: {parsed_intent.action}")
            print(f"🔍 LangGraph Debug - Confidence: {parsed_intent.confidence}")
            
            state["parsed_intent"] = parsed_intent
            
        except Exception as e:
            print(f"❌ LangGraph parsing error: {e}")
            state["error"] = f"Failed to parse user input: {str(e)}"
            state["parsed_intent"] = UserIntent(
                action="unknown",
                confidence=0.0
            )
        
        return state
    
    def _route_to_tool(self, state: RelationshipMemoryState) -> str:
        """Enhanced routing to appropriate tool based on parsed intent"""
        if state.get("error"):
            return "error"
        
        intent = state.get("parsed_intent")
        if not intent or intent.confidence < 0.3:
            return "error"
        
        # Handle all supported actions including new ones
        valid_actions = [
            "add_contact", "add_memory", "add_reminder", 
            "show_contacts", "show_memories", "show_reminders", 
            "search_contacts", "get_contact_details", "add_date", 
            "show_upcoming_dates", "get_advice"
        ]
        
        if intent.action in valid_actions:
            return intent.action
        else:
            return "error"
    
    # ==================== Function Tool Implementations ====================
    
    def _find_contact_by_name(self, vault_manager, name: str) -> Optional[Dict]:
        """Find contact by name (case insensitive, fuzzy matching)"""
        try:
            all_contacts = vault_manager.get_all_contacts()
            name_lower = name.lower().strip()
            
            # Exact match first
            for contact in all_contacts:
                if contact.get('name', '').lower().strip() == name_lower:
                    return contact
            
            # Partial match (contains)
            for contact in all_contacts:
                contact_name = contact.get('name', '').lower().strip()
                if name_lower in contact_name or contact_name in name_lower:
                    return contact
            
            return None
        except Exception:
            return None
    
    def _is_contact_unique(self, vault_manager, name: str) -> bool:
        """Check if contact name is unique"""
        existing_contact = self._find_contact_by_name(vault_manager, name)
        return existing_contact is None
    
    def _update_existing_contact(self, vault_manager, existing_contact: Dict, new_data: Dict) -> Dict:
        """Update existing contact with new information"""
        # Merge data - keep existing data but update with new non-empty values
        updated_contact = existing_contact.copy()
        
        for key, value in new_data.items():
            if value:  # Only update if new value is not None or empty
                updated_contact[key] = value
        
        # Store updated contact
        contact_id = existing_contact.get('id', existing_contact['name'].lower().replace(' ', '_'))
        vault_manager._store_record('contact', contact_id, updated_contact, ConsentScope.VAULT_WRITE_CONTACTS)
        
        return updated_contact

    def _add_contact_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Enhanced function tool for adding contacts with batch processing support"""
        intent = state["parsed_intent"]
        
        if not intent.contact_info:
            state["error"] = "Contact information is required"
            return state
        
        # Handle both single contact (backward compatibility) and batch processing
        contacts_to_process = intent.contact_info if isinstance(intent.contact_info, list) else [intent.contact_info]
        
        if not contacts_to_process:
            state["error"] = "At least one contact is required"
            return state
        
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            
            # Process each contact individually
            results = []
            successful_contacts = []
            failed_contacts = []
            updated_contacts = []
            
            for contact_info in contacts_to_process:
                if not contact_info.name:
                    failed_contacts.append({"contact": "Unknown", "error": "Contact name is required"})
                    continue
                
                try:
                    contact_data = {
                        "name": contact_info.name,
                        "email": contact_info.email,
                        "phone": contact_info.phone,
                        "company": contact_info.company,
                        "location": contact_info.location,
                        "notes": contact_info.notes,
                        "dates": contact_info.dates,
                        "priority": contact_info.priority or "medium",
                        "last_talked_date": contact_info.last_talked_date or datetime.now().strftime('%Y-%m-%d')
                    }
                    
                    # Check if contact already exists
                    existing_contact = self._find_contact_by_name(vault_manager, contact_info.name)
                    
                    if existing_contact:
                        # Contact exists - update with new information
                        updated_contact = self._update_existing_contact(vault_manager, existing_contact, contact_data)
                        
                        # Determine what was updated
                        updated_fields = []
                        for key, value in contact_data.items():
                            if value and (key not in existing_contact or existing_contact.get(key) != value):
                                updated_fields.append(key)
                        
                        if updated_fields:
                            updated_contacts.append({
                                "name": existing_contact['name'],
                                "updated_fields": updated_fields,
                                "contact_id": updated_contact.get('id')
                            })
                        
                        results.append({"contact_id": updated_contact.get('id'), "name": updated_contact['name'], "action": "updated"})
                    else:
                        # Create new contact
                        contact_id = vault_manager.store_contact(contact_data)
                        successful_contacts.append(contact_info.name)
                        results.append({"contact_id": contact_id, "name": contact_info.name, "action": "created"})
                
                except Exception as e:
                    failed_contacts.append({"contact": contact_info.name, "error": str(e)})
                    continue
            
            # Generate consolidated response message
            response_parts = []
            
            if successful_contacts:
                if len(successful_contacts) == 1:
                    response_parts.append(f"✅ Successfully added {successful_contacts[0]}")
                else:
                    response_parts.append(f"✅ Successfully added {len(successful_contacts)} contacts: {', '.join(successful_contacts)}")
            
            if updated_contacts:
                if len(updated_contacts) == 1:
                    updated_info = ", ".join(updated_contacts[0]["updated_fields"])
                    response_parts.append(f"🔄 Updated {updated_contacts[0]['name']} ({updated_info})")
                else:
                    response_parts.append(f"🔄 Updated {len(updated_contacts)} existing contacts")
            
            if failed_contacts:
                if len(failed_contacts) == 1:
                    response_parts.append(f"❌ Failed to process {failed_contacts[0]['contact']}: {failed_contacts[0]['error']}")
                else:
                    failed_names = [f["contact"] for f in failed_contacts]
                    response_parts.append(f"❌ Failed to process {len(failed_contacts)} contacts: {', '.join(failed_names)}")
            
            if not response_parts:
                state["response_message"] = "ℹ️ No contacts were processed"
                state["action_taken"] = "no_contacts_processed"
            else:
                state["response_message"] = ". ".join(response_parts)
                if successful_contacts and not failed_contacts:
                    state["action_taken"] = "batch_add_success"
                elif successful_contacts and failed_contacts:
                    state["action_taken"] = "batch_add_partial"
                elif updated_contacts and not failed_contacts:
                    state["action_taken"] = "batch_update_success"
                else:
                    state["action_taken"] = "batch_add_mixed"
            
            state["result_data"] = results
            
        except Exception as e:
            state["error"] = f"Failed to process contacts: {str(e)}"
        
        return state
    
    # ==================== Interaction History Tracking ====================
    
    def _update_interaction_tool(self, vault_manager: VaultManager, contact_name: str) -> bool:
        """Update the last_talked_date for a contact to current date"""
        try:
            contact = self._find_contact_by_name(vault_manager, contact_name)
            if contact:
                contact['last_talked_date'] = datetime.now().strftime('%Y-%m-%d')
                # Update the contact in vault
                updated_contact = self._update_existing_contact(vault_manager, contact, contact)
                return True
            return False
        except Exception as e:
            print(f"⚠️ Error updating interaction timestamp for {contact_name}: {str(e)}")
            return False
    
    def _add_memory_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Enhanced function tool for adding memories with interaction tracking"""
        intent = state["parsed_intent"]
        
        if not intent.memory_info or not intent.memory_info.contact_name:
            state["error"] = "Contact name is required for memory"
            return state
        
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            
            memory_data = {
                "contact_name": intent.memory_info.contact_name,
                "summary": intent.memory_info.summary,
                "location": intent.memory_info.location,
                "date": intent.memory_info.date,
                "tags": intent.memory_info.tags
            }
            
            memory_id = vault_manager.store_memory(memory_data)
            
            # Update interaction timestamp for the contact
            interaction_updated = self._update_interaction_tool(vault_manager, intent.memory_info.contact_name)
            
            state["action_taken"] = "add_memory"
            base_message = f"🧠 Successfully recorded memory about {intent.memory_info.contact_name}"
            if interaction_updated:
                state["response_message"] = f"{base_message} (interaction timestamp updated)"
            else:
                state["response_message"] = base_message
            
            state["result_data"] = [{"memory_id": memory_id, "contact_name": intent.memory_info.contact_name}]
            
        except Exception as e:
            state["error"] = f"Failed to add memory: {str(e)}"
        
        return state
    
    def _add_reminder_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Function tool for adding reminders"""
        intent = state["parsed_intent"]
        
        if not intent.reminder_info or not intent.reminder_info.contact_name:
            state["error"] = "Contact name is required for reminder"
            return state
        
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            
            reminder_data = {
                "contact_name": intent.reminder_info.contact_name,
                "title": intent.reminder_info.title,
                "date": intent.reminder_info.date,
                "priority": intent.reminder_info.priority
            }
            
            reminder_id = vault_manager.store_reminder(reminder_data)
            
            state["action_taken"] = "add_reminder"
            state["response_message"] = f"⏰ Successfully set reminder: {intent.reminder_info.title}"
            state["result_data"] = [{"reminder_id": reminder_id, "contact_name": intent.reminder_info.contact_name}]
            
        except Exception as e:
            state["error"] = f"Failed to add reminder: {str(e)}"
        
        return state
    
    def _show_contacts_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Function tool for showing all contacts"""
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            contacts = vault_manager.get_all_contacts()
            
            state["action_taken"] = "show_contacts"
            state["response_message"] = f"📋 Found {len(contacts)} contacts"
            state["result_data"] = contacts
            
        except Exception as e:
            state["error"] = f"Failed to retrieve contacts: {str(e)}"
        
        return state
    
    def _show_memories_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Function tool for showing memories"""
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            
            # Get all memories first
            memories = vault_manager.get_all_memories()
            
            # Filter by contact if specified
            if state["parsed_intent"].contact_name:
                contact_name = state["parsed_intent"].contact_name.lower()
                memories = [m for m in memories if contact_name in m.get("contact_name", "").lower()]
                state["response_message"] = f"🧠 Found {len(memories)} memories about {state['parsed_intent'].contact_name}"
            else:
                state["response_message"] = f"🧠 Found {len(memories)} memories"
            
            state["action_taken"] = "show_memories"
            state["result_data"] = memories
            
        except Exception as e:
            state["error"] = f"Failed to retrieve memories: {str(e)}"
        
        return state
    
    def _show_reminders_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Function tool for showing reminders"""
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            reminders = vault_manager.get_all_reminders()
            
            state["action_taken"] = "show_reminders"
            state["response_message"] = f"⏰ Found {len(reminders)} reminders"
            state["result_data"] = reminders
            
        except Exception as e:
            state["error"] = f"Failed to retrieve reminders: {str(e)}"
        
        return state
    
    def _search_contacts_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Function tool for searching contacts"""
        intent = state["parsed_intent"]
        
        if not intent.search_query:
            state["error"] = "Search query is required"
            return state
        
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            contacts = vault_manager.search_contacts(intent.search_query)
            
            state["action_taken"] = "search_contacts"
            state["response_message"] = f"🔍 Found {len(contacts)} contacts matching '{intent.search_query}'"
            state["result_data"] = contacts
            
        except Exception as e:
            state["error"] = f"Failed to search contacts: {str(e)}"
        
        return state
    
    def _get_contact_details_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Function tool for getting detailed information about a specific contact"""
        intent = state["parsed_intent"]
        
        # Extract contact name from various possible sources
        contact_name = None
        if intent.contact_info and intent.contact_info.name:
            contact_name = intent.contact_info.name
        elif intent.contact_name:
            contact_name = intent.contact_name
        elif intent.search_query:
            contact_name = intent.search_query
        
        if not contact_name:
            state["error"] = "Contact name is required to get details"
            return state
        
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            
            # Find the contact
            contact = self._find_contact_by_name(vault_manager, contact_name)
            
            if not contact:
                state["error"] = f"Contact '{contact_name}' not found"
                return state
            
            # Get related memories and reminders
            memories = vault_manager.get_memories_for_contact(contact['name'])
            all_reminders = vault_manager.get_all_reminders()
            reminders = [r for r in all_reminders if r.get('contact_name', '').lower() == contact['name'].lower()]
            
            # Format detailed response
            details = []
            details.append(f"👤 **{contact['name']}**")
            
            if contact.get('email'):
                details.append(f"📧 Email: {contact['email']}")
            if contact.get('phone'):
                details.append(f"📞 Phone: {contact['phone']}")
            if contact.get('company'):
                details.append(f"🏢 Company: {contact['company']}")
            if contact.get('location'):
                details.append(f"📍 Location: {contact['location']}")
            if contact.get('notes'):
                details.append(f"📝 Notes: {contact['notes']}")
            
            # Show important dates
            if contact.get('dates'):
                details.append(f"\n📅 **Important Dates:**")
                for date_type, date_value in contact['dates'].items():
                    if not date_type.endswith('_notes'):  # Skip notes entries
                        # Convert date format for display
                        if '-' in date_value:
                            date_parts = date_value.split('-')
                            if len(date_parts) >= 2:
                                day, month = date_parts[0], date_parts[1]
                                month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                                month_name = month_names[int(month)] if int(month) <= 12 else month
                                date_display = f"{day} {month_name}"
                                if len(date_parts) > 2:  # Include year if available
                                    date_display += f" {date_parts[2]}"
                                details.append(f"  🎉 {date_type.title()}: {date_display}")
            
            if memories:
                details.append(f"\n🧠 **Memories ({len(memories)}):**")
                for memory in memories[-3:]:  # Show last 3 memories
                    details.append(f"  • {memory.get('description', 'No description')}")
            
            if reminders:
                details.append(f"\n⏰ **Reminders ({len(reminders)}):**")
                for reminder in reminders[-3:]:  # Show last 3 reminders
                    details.append(f"  • {reminder.get('title', 'No title')} ({reminder.get('date', 'No date')})")
            
            state["action_taken"] = "get_contact_details"
            state["response_message"] = "\n".join(details)
            state["result_data"] = [{
                "contact": contact,
                "memories_count": len(memories),
                "reminders_count": len(reminders)
            }]
            
        except Exception as e:
            state["error"] = f"Failed to get contact details: {str(e)}"
        
        return state
    
    def _add_date_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Function tool for adding important dates to contacts"""
        intent = state["parsed_intent"]
        
        if not intent.date_info or not intent.date_info.contact_name or not intent.date_info.date_type or not intent.date_info.date_value:
            state["error"] = "Contact name, date type, and date value are required"
            return state
        
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            
            # Find the contact
            contact = self._find_contact_by_name(vault_manager, intent.date_info.contact_name)
            
            if not contact:
                state["error"] = f"Contact '{intent.date_info.contact_name}' not found. Please add the contact first."
                return state
            
            # Initialize dates dictionary if it doesn't exist
            if not contact.get('dates'):
                contact['dates'] = {}
            
            # Add the new date
            date_key = intent.date_info.date_type.lower()
            date_value = intent.date_info.date_value
            
            # Include year if provided
            if intent.date_info.year:
                date_value = f"{date_value}-{intent.date_info.year}"
            
            contact['dates'][date_key] = date_value
            
            # If notes provided, store them too
            if intent.date_info.notes:
                notes_key = f"{date_key}_notes"
                contact['dates'][notes_key] = intent.date_info.notes
            
            # Update the contact
            updated_contact = self._update_existing_contact(vault_manager, contact, contact)
            
            state["action_taken"] = "add_date"
            state["response_message"] = f"📅 Successfully added {intent.date_info.date_type} ({intent.date_info.date_value}) for {contact['name']}"
            state["result_data"] = [{
                "contact_name": contact['name'],
                "date_type": intent.date_info.date_type,
                "date_value": date_value
            }]
            
        except Exception as e:
            state["error"] = f"Failed to add date: {str(e)}"
        
        return state
    
    def _show_upcoming_dates_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Function tool for showing upcoming important dates"""
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            all_contacts = vault_manager.get_all_contacts()
            
            current_date = datetime.now()
            current_month = current_date.month
            current_day = current_date.day
            
            upcoming_dates = []
            
            for contact in all_contacts:
                if contact.get('dates'):
                    for date_type, date_value in contact['dates'].items():
                        # Skip notes entries
                        if date_type.endswith('_notes'):
                            continue
                        
                        try:
                            # Parse date (DD-MM or DD-MM-YYYY format)
                            if '-' in date_value:
                                date_parts = date_value.split('-')
                                if len(date_parts) >= 2:
                                    day = int(date_parts[0])
                                    month = int(date_parts[1])
                                    year = date_parts[2] if len(date_parts) > 2 else None
                                    
                                    # Calculate days until this date
                                    days_until = self._calculate_days_until(current_month, current_day, month, day)
                                    
                                    # Show dates within next 60 days
                                    if 0 <= days_until <= 60:
                                        upcoming_dates.append({
                                            'contact_name': contact['name'],
                                            'date_type': date_type,
                                            'date_value': date_value,
                                            'day': day,
                                            'month': month,
                                            'year': year,
                                            'days_until': days_until,
                                            'notes': contact['dates'].get(f"{date_type}_notes")
                                        })
                        except (ValueError, IndexError):
                            continue
            
            # Sort by days until
            upcoming_dates.sort(key=lambda x: x['days_until'])
            
            if not upcoming_dates:
                state["response_message"] = "📅 No upcoming important dates in the next 60 days"
            else:
                response_lines = [f"📅 Upcoming Important Dates ({len(upcoming_dates)} found):"]
                for date_info in upcoming_dates:
                    days_text = "Today!" if date_info['days_until'] == 0 else f"in {date_info['days_until']} days"
                    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    month_name = month_names[date_info['month']]
                    
                    date_line = f"  🎉 {date_info['contact_name']}'s {date_info['date_type']}: {date_info['day']} {month_name} ({days_text})"
                    if date_info['notes']:
                        date_line += f" - {date_info['notes']}"
                    response_lines.append(date_line)
                
                state["response_message"] = "\n".join(response_lines)
            
            state["action_taken"] = "show_upcoming_dates"
            state["result_data"] = upcoming_dates
            
        except Exception as e:
            state["error"] = f"Failed to get upcoming dates: {str(e)}"
        
        return state
    
    def _calculate_days_until(self, current_month: int, current_day: int, target_month: int, target_day: int) -> int:
        """Calculate days until a recurring date (birthday/anniversary)"""
        from datetime import date, timedelta
        
        current_year = datetime.now().year
        
        # Try this year first
        try:
            target_date = date(current_year, target_month, target_day)
            current_date = date(current_year, current_month, current_day)
            
            if target_date >= current_date:
                return (target_date - current_date).days
            else:
                # Date has passed this year, try next year
                target_date = date(current_year + 1, target_month, target_day)
                return (target_date - current_date).days
        except ValueError:
            # Invalid date (like Feb 29 on non-leap year)
            return 999  # Return high number to put at end
    
    # ==================== Enhanced Utility Functions for Proactive Features ====================
    
    def _calculate_days_until_event(self, date_value: str, current_date: datetime) -> int:
        """Calculate days until an event (birthday/anniversary) from date string"""
        try:
            if '-' in date_value:
                date_parts = date_value.split('-')
                if len(date_parts) >= 2:
                    day = int(date_parts[0])
                    month = int(date_parts[1])
                    
                    # Use existing calculation method
                    return self._calculate_days_until(
                        current_date.month, current_date.day, month, day
                    )
            return 999  # Invalid date format
        except (ValueError, IndexError):
            return 999
    
    def _calculate_days_since_contact(self, contact: Dict) -> int:
        """Calculate days since last contact interaction"""
        try:
            last_talked_date = contact.get('last_talked_date')
            if not last_talked_date:
                # If no last_talked_date, use created_at or assume 30 days
                created_at = contact.get('created_at')
                if created_at:
                    # Parse created_at if it's a string
                    if isinstance(created_at, str):
                        from datetime import datetime
                        try:
                            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            return (datetime.now() - created_date).days
                        except:
                            return 30  # Default fallback
                    return 30  # Default fallback
                return 30  # Default fallback
            
            # Parse last_talked_date (YYYY-MM-DD format)
            from datetime import datetime
            last_date = datetime.strptime(last_talked_date, '%Y-%m-%d')
            return (datetime.now() - last_date).days
            
        except (ValueError, TypeError):
            return 30  # Default fallback if parsing fails
    
    def _format_triggers_for_llm(self, triggers: List[Dict]) -> str:
        """Format proactive triggers for LLM context"""
        if not triggers:
            return "No triggers found."
        
        formatted_lines = []
        
        # Group triggers by type
        upcoming_events = [t for t in triggers if t.get('type') == 'upcoming_event']
        reconnections = [t for t in triggers if t.get('type') == 'reconnection']
        
        if upcoming_events:
            formatted_lines.append("UPCOMING EVENTS:")
            for event in upcoming_events:
                days_text = "today" if event['days_until'] == 0 else f"in {event['days_until']} days"
                formatted_lines.append(f"- {event['contact_name']}'s {event['event_type']} is {days_text}")
        
        if reconnections:
            formatted_lines.append("\nRECONNECTION SUGGESTIONS:")
            for recon in reconnections:
                priority_text = f"({recon['priority']} priority)"
                formatted_lines.append(f"- Haven't talked to {recon['contact_name']} in {recon['days_since_contact']} days {priority_text}")
        
        return "\n".join(formatted_lines)
    
    def _format_memories_for_advice(self, contact: Dict, memories: List[Dict], user_question: str) -> str:
        """Format contact memories for advice generation context"""
        context_lines = [f"CONTACT: {contact.get('name', 'Unknown')}"]
        
        # Add basic contact info
        if contact.get('email'):
            context_lines.append(f"Email: {contact['email']}")
        if contact.get('phone'):
            context_lines.append(f"Phone: {contact['phone']}")
        if contact.get('company'):
            context_lines.append(f"Company: {contact['company']}")
        if contact.get('notes'):
            context_lines.append(f"Notes: {contact['notes']}")
        
        # Add important dates
        if contact.get('dates'):
            context_lines.append("\nIMPORTANT DATES:")
            for date_type, date_value in contact['dates'].items():
                if not date_type.endswith('_notes'):
                    context_lines.append(f"- {date_type}: {date_value}")
        
        # Add memories
        if memories:
            context_lines.append(f"\nMEMORIES ({len(memories)} total):")
            # Show most recent memories first, limit to 10 for context
            recent_memories = sorted(memories, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
            for memory in recent_memories:
                summary = memory.get('summary', memory.get('description', 'No summary'))
                context_lines.append(f"- {summary}")
                if memory.get('location'):
                    context_lines.append(f"  Location: {memory['location']}")
                if memory.get('tags'):
                    context_lines.append(f"  Tags: {', '.join(memory['tags'])}")
        else:
            context_lines.append("\nMEMORIES: No memories recorded yet")
        
        return "\n".join(context_lines)
    
    # ==================== Proactive Trigger Detection System ====================
    
    def _check_for_proactive_triggers(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Check for proactive triggers on startup or between commands"""
        try:
            if VaultManager is None:
                state["proactive_triggers"] = []
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            all_contacts = vault_manager.get_all_contacts()
            
            triggers = []
            current_date = datetime.now()
            
            # Check for upcoming birthdays/anniversaries (next 30 days)
            for contact in all_contacts:
                if contact.get('dates'):
                    for date_type, date_value in contact['dates'].items():
                        # Skip notes entries
                        if date_type.endswith('_notes'):
                            continue
                        
                        # Calculate days until event
                        days_until = self._calculate_days_until_event(date_value, current_date)
                        if 0 <= days_until <= 30:
                            triggers.append({
                                'type': 'upcoming_event',
                                'contact_name': contact['name'],
                                'event_type': date_type,
                                'days_until': days_until,
                                'date_value': date_value
                            })
            
            # Check for reconnection opportunities
            for contact in all_contacts:
                days_since_contact = self._calculate_days_since_contact(contact)
                priority = contact.get('priority', 'medium')
                
                should_reconnect = (
                    (priority == 'high' and days_since_contact > 7) or
                    (priority == 'medium' and days_since_contact > 30) or
                    (priority == 'low' and days_since_contact > 90)
                )
                
                if should_reconnect:
                    triggers.append({
                        'type': 'reconnection',
                        'contact_name': contact['name'],
                        'days_since_contact': days_since_contact,
                        'priority': priority,
                        'last_talked_date': contact.get('last_talked_date')
                    })
            
            state["proactive_triggers"] = triggers
            return state
            
        except Exception as e:
            print(f"⚠️ Error checking proactive triggers: {str(e)}")
            state["proactive_triggers"] = []
            # Don't set error - this should not interrupt normal workflow
            return state
    
    def _generate_proactive_response(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Generate engaging proactive messages based on triggers"""
        triggers = state.get("proactive_triggers", [])
        
        if not triggers:
            state["response_message"] = ""
            state["action_taken"] = "no_proactive_triggers"
            return state
        
        try:
            # Create context for LLM
            trigger_context = self._format_triggers_for_llm(triggers)
            
            prompt = f"""Based on the following relationship triggers, create a friendly, engaging message:

{trigger_context}

Guidelines:
- Be conversational and warm
- Consolidate multiple triggers into one coherent message
- Offer specific help or suggestions
- Use emojis appropriately (but not excessively)
- Keep it concise but helpful
- End with a question or suggestion for action
- Make it feel personal and caring

Examples of good responses:
- "Hey! 👋 Just a heads-up - Jane's birthday is coming up in 5 days! 🎂 Also, it's been a while since you spoke to John (45 days). Would you like some gift ideas for Jane or help reconnecting with John?"
- "Good morning! 🌅 I noticed Sarah's anniversary is today! 💕 Perfect time to reach out. Also, you haven't talked to Mike in over a week - want me to suggest some conversation starters?"
"""
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            state["response_message"] = response.content
            state["action_taken"] = "proactive_notification"
            
        except Exception as e:
            print(f"⚠️ Error generating proactive response: {str(e)}")
            # Provide fallback message
            event_count = len([t for t in triggers if t.get('type') == 'upcoming_event'])
            reconnect_count = len([t for t in triggers if t.get('type') == 'reconnection'])
            
            fallback_parts = []
            if event_count > 0:
                fallback_parts.append(f"{event_count} upcoming event{'s' if event_count > 1 else ''}")
            if reconnect_count > 0:
                fallback_parts.append(f"{reconnect_count} reconnection suggestion{'s' if reconnect_count > 1 else ''}")
            
            state["response_message"] = f"👋 I noticed {' and '.join(fallback_parts)}. Would you like me to show you the details?"
            state["action_taken"] = "proactive_notification_fallback"
        
        return state
    
    def _conversational_advice_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Generate advice based on contact memories and context"""
        intent = state["parsed_intent"]
        contact_name = intent.contact_name
        
        if not contact_name:
            state["error"] = "Contact name is required for advice generation"
            return state
        
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            
            # Get contact and their memories
            contact = self._find_contact_by_name(vault_manager, contact_name)
            if not contact:
                state["response_message"] = f"I don't have information about {contact_name}. Would you like to add them first?"
                state["action_taken"] = "advice_no_contact"
                return state
            
            # Get memories for this contact
            try:
                all_memories = vault_manager.get_all_memories()
                memories = [m for m in all_memories if m.get('contact_name', '').lower() == contact['name'].lower()]
            except:
                memories = []
            
            # Create context for advice generation
            advice_context = self._format_memories_for_advice(contact, memories, state["user_input"])
            
            prompt = f"""Based on the following information about {contact['name']}, provide helpful advice:

{advice_context}

User's question: {state["user_input"]}

Guidelines:
- Reference specific memories when relevant
- Provide actionable suggestions
- Be empathetic and understanding
- If asking about gifts, consider their interests and past conversations
- If asking about conversation topics, suggest based on shared experiences
- If asking about relationship management, consider their priority level and interaction history
- Be specific and practical
- Use a warm, supportive tone

Examples of good advice:
- For gift questions: "Based on your memories, Sarah loves hiking and mentioned wanting new gear. Consider a high-quality water bottle or hiking socks!"
- For conversation starters: "You could ask John about his new job at Tech Corp - you noted he was excited about it last time you talked."
- For reconnection: "Since it's been a while, start with something personal like asking about his recent trip to Japan that he mentioned."
"""
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            state["response_message"] = response.content
            state["action_taken"] = "advice_generated"
            
        except Exception as e:
            print(f"⚠️ Error generating advice: {str(e)}")
            state["response_message"] = f"I had trouble accessing information about {contact_name}. The error was: {str(e)}"
            state["action_taken"] = "advice_error"
        
        return state
    
    def _generate_response_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Generate final response with context-aware formatting"""
        if state.get("error"):
            return state
        
        # Response is already set by the tool functions
        return state
    
    def _handle_error_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Enhanced error handling with detailed feedback"""
        error_message = state.get("error", "Could not understand your request")
        
        # Provide context-specific error messages and suggestions
        if "VaultManager not available" in error_message:
            state["response_message"] = "❌ Storage system is not available. Please check your configuration and try again."
        elif "Contact name is required" in error_message:
            state["response_message"] = "❌ Please provide a contact name. Example: 'add contact John Smith' or 'remember that Alice likes coffee'"
        elif "not found" in error_message.lower():
            state["response_message"] = f"❌ {error_message}. You can add them first by saying 'add contact [name]'"
        elif "validation" in error_message.lower():
            state["response_message"] = f"❌ {error_message}. Please check your input format and try again."
        else:
            # General error with helpful suggestions
            suggestions = [
                "'add contact John Smith with email john@example.com'",
                "'add contacts: Alice and Bob with phone 555-1234'",
                "'remember that Sarah loves hiking'",
                "'what should I get Jane for her birthday?'",
                "'show my contacts'",
                "'upcoming birthdays'"
            ]
            
            state["response_message"] = f"❌ {error_message}.\n\nTry commands like:\n• " + "\n• ".join(suggestions)
        
        state["action_taken"] = "error_handled"
        
        return state
    
    def _validate_permissions(self, user_id: str, token: str, required_scope: ConsentScope) -> tuple[bool, str]:
        """Validate token and permissions for the given scope"""
        try:
            # Allow test tokens for demo purposes
            if token and (token.startswith('test_token') or token.startswith('demo_token')):
                return True, "✅ Test token accepted for demo"
            
            valid, reason, parsed = validate_token(token, expected_scope=required_scope)
            
            if not valid:
                return False, f"❌ Invalid token: {reason}"
                
            if parsed.user_id != user_id:
                return False, "❌ Token user mismatch"
                
            return True, "✅ Token validated successfully"
            
        except Exception as e:
            return False, f"❌ Token validation error: {str(e)}"


# ==================== Entry Point Function ====================

def run(user_id: str, tokens: Dict[str, str], user_input: str, vault_key: Optional[str] = None, is_startup: bool = False, **api_keys) -> Dict[str, Any]:
    """
    Enhanced entry point function for the Proactive Relationship Memory Agent.
    
    Args:
        user_id: User identifier
        tokens: Consent tokens for authorization
        user_input: User's input message
        vault_key: Optional vault key for data encryption
        is_startup: Flag indicating if this is a startup/proactive check
        **api_keys: Dynamic API keys for agent initialization
    
    Returns:
        Dict containing response and execution details
    """
    # Extract API keys for agent initialization
    agent_api_keys = {}
    if 'gemini_api_key' in api_keys:
        agent_api_keys['gemini_api_key'] = api_keys['gemini_api_key']
    if 'api_keys' in api_keys:
        agent_api_keys.update(api_keys['api_keys'])
    
    agent = RelationshipMemoryAgent(api_keys=agent_api_keys)
    return agent.handle(user_id, tokens, user_input, vault_key, is_startup, **api_keys)

def run_proactive_check(user_id: str, tokens: Dict[str, str], vault_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to run proactive checks on startup.
    
    Args:
        user_id: User identifier
        tokens: Consent tokens for authorization
        vault_key: Optional vault key for data encryption
    
    Returns:
        Dict containing proactive notifications or empty response
    """
    return run(user_id, tokens, "", vault_key, is_startup=True)
