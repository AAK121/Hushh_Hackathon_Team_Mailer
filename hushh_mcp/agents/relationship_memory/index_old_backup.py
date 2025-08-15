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
    VaultManager = None

# ==================== Pydantic Models for Function Tool Calling ====================

class ContactInfo(BaseModel):
    """Structured contact information for function tool calling"""
    name: str = Field(..., description="Full name of the contact")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company or workplace")
    location: Optional[str] = Field(None, description="Location or address")
    notes: Optional[str] = Field(None, description="Additional notes or context")

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
    """Parsed user intent with extracted structured data"""
    action: Literal[
        "add_contact", "add_memory", "add_reminder", 
        "show_contacts", "show_memories", "show_reminders", 
        "search_contacts", "get_contact_details", "unknown"
    ] = Field(..., description="The intended action")
    confidence: float = Field(..., description="Confidence level (0.0 to 1.0)")
    contact_info: Optional[ContactInfo] = Field(None, description="Contact information if adding/updating contact")
    memory_info: Optional[MemoryInfo] = Field(None, description="Memory information if adding memory")
    reminder_info: Optional[ReminderInfo] = Field(None, description="Reminder information if setting reminder")
    search_query: Optional[str] = Field(None, description="Search query if searching")
    contact_name: Optional[str] = Field(None, description="Contact name for queries")

# ==================== LangGraph State ====================

class RelationshipMemoryState(TypedDict):
    """State for the LangGraph workflow"""
    user_input: str
    user_id: str
    vault_key: str
    parsed_intent: Optional[UserIntent]
    result_data: List[Dict]
    response_message: str
    error: Optional[str]
    action_taken: str

# ==================== LangGraph-based Relationship Memory Agent ====================

class RelationshipMemoryAgent:
    """
    Full LangGraph implementation with function tool calling and HushhMCP compliance.
    """
    
    def __init__(self):
        self.agent_id = manifest["id"]
        self.required_scopes = manifest["scopes"]
        
        # Load environment variables
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            main_env_path = os.path.join(project_root, '.env')
            load_dotenv(main_env_path)
        
        # Initialize Gemini LLM
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=gemini_api_key
        )
        
        # Build the LangGraph workflow
        self.graph = self._build_langgraph_workflow()
    
    def handle(self, user_id: str, tokens: Dict[str, str], user_input: str, vault_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Main handler method using LangGraph workflow with function tool calling.
        """
        
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
            # Run the LangGraph workflow
            initial_state = RelationshipMemoryState(
                user_input=user_input,
                user_id=user_id,
                vault_key=vault_key,
                parsed_intent=None,
                result_data=[],
                response_message="",
                error=None,
                action_taken=""
            )
            
            final_state = self.graph.invoke(initial_state)
            
            # Format response
            if final_state.get("error"):
                return {
                    "status": "error",
                    "message": f"❌ {final_state['error']}",
                    "agent_id": self.agent_id,
                    "user_id": user_id
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
            return {
                "status": "error",
                "message": f"❌ LangGraph workflow failed: {str(e)}",
                "agent_id": self.agent_id,
                "user_id": user_id
            }
    
    def _build_langgraph_workflow(self) -> StateGraph:
        """Build the complete LangGraph workflow with function tool calling"""
        
        workflow = StateGraph(RelationshipMemoryState)
        
        # Add nodes for the workflow
        workflow.add_node("parse_intent", self._parse_intent_node)
        workflow.add_node("add_contact_tool", self._add_contact_tool)
        workflow.add_node("add_memory_tool", self._add_memory_tool)
        workflow.add_node("add_reminder_tool", self._add_reminder_tool)
        workflow.add_node("show_contacts_tool", self._show_contacts_tool)
        workflow.add_node("show_memories_tool", self._show_memories_tool)
        workflow.add_node("show_reminders_tool", self._show_reminders_tool)
        workflow.add_node("search_contacts_tool", self._search_contacts_tool)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Set entry point
        workflow.set_entry_point("parse_intent")
        
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
        workflow.add_edge("handle_error", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def _parse_intent_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Parse user input using structured output to extract intent and data"""
        
        system_prompt = """You are an expert at parsing user input for a relationship memory assistant.
        Extract the user's intent and structured information from their message.
        
        Available actions:
        - add_contact: User wants to add a new contact (extract name, email, phone, etc.)
        - add_memory: User wants to record a memory about someone
        - add_reminder: User wants to set a reminder related to someone  
        - show_contacts: User wants to see all their contacts
        - show_memories: User wants to see memories (all or for specific person)
        - show_reminders: User wants to see reminders
        - search_contacts: User wants to search for specific contacts
        - unknown: Intent cannot be determined clearly
        
        IMPORTANT: Extract ALL relevant information:
        - For add_contact: Extract name, email, phone, company, location, notes
        - For add_memory: Extract contact_name and summary of the memory
        - For add_reminder: Extract contact_name, title, date if mentioned
        - For searches: Extract the search query or contact name
        
        Examples:
        - "Add John Smith with email john@example.com" -> add_contact, ContactInfo(name="John Smith", email="john@example.com")
        - "Remember that Sarah loves hiking" -> add_memory, MemoryInfo(contact_name="Sarah", summary="Sarah loves hiking")
        - "Show me all my contacts" -> show_contacts
        - "What do you know about Alice?" -> show_memories, contact_name="Alice"
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
        """Route to appropriate tool based on parsed intent"""
        if state.get("error"):
            return "error"
        
        intent = state.get("parsed_intent")
        if not intent or intent.confidence < 0.3:
            return "error"
        
        return intent.action if intent.action != "unknown" else "error"
    
    # ==================== Function Tool Implementations ====================
    
    def _add_contact_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Function tool for adding contacts"""
        intent = state["parsed_intent"]
        
        if not intent.contact_info or not intent.contact_info.name:
            state["error"] = "Contact name is required"
            return state
        
        try:
            if VaultManager is None:
                state["error"] = "VaultManager not available"
                return state
            
            vault_manager = VaultManager(user_id=state["user_id"], vault_key=state["vault_key"])
            
            contact_data = {
                "name": intent.contact_info.name,
                "email": intent.contact_info.email,
                "phone": intent.contact_info.phone,
                "company": intent.contact_info.company,
                "location": intent.contact_info.location,
                "notes": intent.contact_info.notes
            }
            
            contact_id = vault_manager.store_contact(contact_data)
            
            state["action_taken"] = "add_contact"
            state["response_message"] = f"✅ Successfully added {intent.contact_info.name} to your contacts"
            state["result_data"] = [{"contact_id": contact_id, "name": intent.contact_info.name}]
            
        except Exception as e:
            state["error"] = f"Failed to add contact: {str(e)}"
        
        return state
    
    def _add_memory_tool(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Function tool for adding memories"""
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
            
            state["action_taken"] = "add_memory"
            state["response_message"] = f"🧠 Successfully recorded memory about {intent.memory_info.contact_name}"
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
            
            # Check if looking for specific contact
            contact_name = None
            if state["parsed_intent"].contact_name:
                contact_name = state["parsed_intent"].contact_name
            
            memories = vault_manager.get_all_memories(contact_name)
            
            state["action_taken"] = "show_memories"
            if contact_name:
                state["response_message"] = f"🧠 Found {len(memories)} memories about {contact_name}"
            else:
                state["response_message"] = f"🧠 Found {len(memories)} memories"
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
    
    def _generate_response_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Generate final response with context-aware formatting"""
        if state.get("error"):
            return state
        
        # Response is already set by the tool functions
        return state
    
    def _handle_error_node(self, state: RelationshipMemoryState) -> RelationshipMemoryState:
        """Handle errors and unknown intents"""
        if not state.get("error"):
            state["error"] = "Could not understand your request"
        
        state["response_message"] = f"❌ {state['error']}. Try: 'add contact', 'show contacts', 'remember', or 'remind me'"
        state["action_taken"] = "error"
        
        return state
    
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


# ==================== Entry Point Function ====================

def run(user_id: str, tokens: Dict[str, str], user_input: str, vault_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Entry point function for the LangGraph-based Relationship Memory Agent.
    """
    agent = RelationshipMemoryAgent()
    return agent.handle(user_id, tokens, user_input, vault_key)
