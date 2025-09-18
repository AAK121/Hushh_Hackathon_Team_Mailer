"""
MCP Server for Relationship Memory Agent
Provides Model Context Protocol interface for the relationship memory functionality
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server import Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    EmbeddedResource,
    GetPromptRequest,
    GetPromptResult,
    ListPromptsRequest,
    ListPromptsResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    ListResourcesRequest,
    ListResourcesResult,
    ReadResourceRequest,
    ReadResourceResult,
    Resource
)

from .agent import RelationshipMemoryAgent
from .manifest import MANIFEST

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("relationship_memory_mcp")

class RelationshipMemoryMCPServer:
    """MCP Server for Relationship Memory Agent"""
    
    def __init__(self):
        self.server = Server("relationship_memory")
        self.agents: Dict[str, RelationshipMemoryAgent] = {}
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools for relationship memory management"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="add_contact",
                        description="Add a new contact to the relationship memory system",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User identifier"},
                                "vault_key": {"type": "string", "description": "Vault encryption key"},
                                "name": {"type": "string", "description": "Contact name"},
                                "email": {"type": "string", "description": "Contact email (optional)"},
                                "phone": {"type": "string", "description": "Contact phone (optional)"},
                                "company": {"type": "string", "description": "Contact company (optional)"},
                                "notes": {"type": "string", "description": "Additional notes (optional)"}
                            },
                            "required": ["user_id", "vault_key", "name"]
                        }
                    ),
                    Tool(
                        name="get_contacts",
                        description="Retrieve all contacts for a user",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User identifier"},
                                "vault_key": {"type": "string", "description": "Vault encryption key"}
                            },
                            "required": ["user_id", "vault_key"]
                        }
                    ),
                    Tool(
                        name="search_contacts",
                        description="Search contacts by name or details",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User identifier"},
                                "vault_key": {"type": "string", "description": "Vault encryption key"},
                                "query": {"type": "string", "description": "Search query"}
                            },
                            "required": ["user_id", "vault_key", "query"]
                        }
                    ),
                    Tool(
                        name="add_memory",
                        description="Add a memory about a contact",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User identifier"},
                                "vault_key": {"type": "string", "description": "Vault encryption key"},
                                "contact_name": {"type": "string", "description": "Contact name"},
                                "summary": {"type": "string", "description": "Memory summary"}
                            },
                            "required": ["user_id", "vault_key", "contact_name", "summary"]
                        }
                    ),
                    Tool(
                        name="get_memories",
                        description="Get memories for a contact or all memories",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User identifier"},
                                "vault_key": {"type": "string", "description": "Vault encryption key"},
                                "contact_name": {"type": "string", "description": "Contact name (optional - if not provided, returns all memories)"}
                            },
                            "required": ["user_id", "vault_key"]
                        }
                    ),
                    Tool(
                        name="set_reminder",
                        description="Set a reminder for a contact",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User identifier"},
                                "vault_key": {"type": "string", "description": "Vault encryption key"},
                                "contact_name": {"type": "string", "description": "Contact name"},
                                "title": {"type": "string", "description": "Reminder title"},
                                "date": {"type": "string", "description": "Reminder date (ISO format)"}
                            },
                            "required": ["user_id", "vault_key", "contact_name", "title", "date"]
                        }
                    ),
                    Tool(
                        name="get_reminders",
                        description="Get reminders for a contact or all reminders",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User identifier"},
                                "vault_key": {"type": "string", "description": "Vault encryption key"},
                                "contact_name": {"type": "string", "description": "Contact name (optional - if not provided, returns all reminders)"}
                            },
                            "required": ["user_id", "vault_key"]
                        }
                    ),
                    Tool(
                        name="process_natural_language",
                        description="Process natural language input for relationship memory operations",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User identifier"},
                                "vault_key": {"type": "string", "description": "Vault encryption key"},
                                "input": {"type": "string", "description": "Natural language input"}
                            },
                            "required": ["user_id", "vault_key", "input"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool calls"""
            try:
                args = request.params.arguments
                user_id = args.get("user_id")
                vault_key = args.get("vault_key")
                
                if not user_id or not vault_key:
                    return CallToolResult(
                        content=[TextContent(type="text", text="Error: user_id and vault_key are required")]
                    )
                
                # Get or create agent for this user
                agent_key = f"{user_id}:{hash(vault_key)}"
                if agent_key not in self.agents:
                    self.agents[agent_key] = RelationshipMemoryAgent(user_id, vault_key)
                
                agent = self.agents[agent_key]
                
                # Handle different tool calls
                if request.params.name == "add_contact":
                    contact_data = {
                        "name": args.get("name"),
                        "email": args.get("email"),
                        "phone": args.get("phone"),
                        "company": args.get("company"),
                        "notes": args.get("notes")
                    }
                    # Remove None values
                    contact_data = {k: v for k, v in contact_data.items() if v is not None}
                    result = agent.add_contact(contact_data)
                    
                elif request.params.name == "get_contacts":
                    contacts = agent.get_contacts()
                    result = {
                        "status": "success",
                        "contacts": contacts,
                        "count": len(contacts)
                    }
                    
                elif request.params.name == "search_contacts":
                    query = args.get("query")
                    results = agent.vault_manager.search_contacts(query)
                    result = {
                        "status": "success",
                        "contacts": results,
                        "count": len(results),
                        "query": query
                    }
                    
                elif request.params.name == "add_memory":
                    contact_name = args.get("contact_name")
                    summary = args.get("summary")
                    result = agent.add_memory(contact_name, summary)
                    
                elif request.params.name == "get_memories":
                    contact_name = args.get("contact_name")
                    if contact_name:
                        memories = agent.get_memories(contact_name)
                    else:
                        memories = agent.vault_manager.get_all_memories()
                    result = {
                        "status": "success",
                        "memories": memories,
                        "count": len(memories),
                        "contact_name": contact_name
                    }
                    
                elif request.params.name == "set_reminder":
                    contact_name = args.get("contact_name")
                    title = args.get("title")
                    date_str = args.get("date")
                    try:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        result = agent.set_reminder(contact_name, title, date)
                    except ValueError:
                        result = {"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}
                    
                elif request.params.name == "get_reminders":
                    contact_name = args.get("contact_name")
                    reminders = agent.get_reminders(contact_name)
                    result = {
                        "status": "success",
                        "reminders": reminders,
                        "count": len(reminders),
                        "contact_name": contact_name
                    }
                    
                elif request.params.name == "process_natural_language":
                    user_input = args.get("input")
                    result = agent.process_input(user_input)
                    
                else:
                    result = {"error": f"Unknown tool: {request.params.name}"}
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
                
            except Exception as e:
                logger.error(f"Error in tool call {request.params.name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
        
        @self.server.list_prompts()
        async def list_prompts() -> ListPromptsResult:
            """List available prompts"""
            return ListPromptsResult(
                prompts=[
                    Prompt(
                        name="relationship_summary",
                        description="Generate a summary of relationships and memories",
                        arguments=[
                            PromptArgument(
                                name="user_id",
                                description="User identifier",
                                required=True
                            ),
                            PromptArgument(
                                name="vault_key", 
                                description="Vault encryption key",
                                required=True
                            )
                        ]
                    ),
                    Prompt(
                        name="contact_analysis",
                        description="Analyze contact patterns and relationships",
                        arguments=[
                            PromptArgument(
                                name="user_id",
                                description="User identifier", 
                                required=True
                            ),
                            PromptArgument(
                                name="vault_key",
                                description="Vault encryption key",
                                required=True
                            ),
                            PromptArgument(
                                name="contact_name",
                                description="Specific contact to analyze (optional)",
                                required=False
                            )
                        ]
                    )
                ]
            )
        
        @self.server.get_prompt()
        async def get_prompt(request: GetPromptRequest) -> GetPromptResult:
            """Get prompt content"""
            try:
                args = request.params.arguments
                user_id = args.get("user_id")
                vault_key = args.get("vault_key")
                
                if not user_id or not vault_key:
                    return GetPromptResult(
                        description="Error: Missing required arguments",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text",
                                    text="Error: user_id and vault_key are required"
                                )
                            )
                        ]
                    )
                
                # Get or create agent
                agent_key = f"{user_id}:{hash(vault_key)}"
                if agent_key not in self.agents:
                    self.agents[agent_key] = RelationshipMemoryAgent(user_id, vault_key)
                
                agent = self.agents[agent_key]
                
                if request.params.name == "relationship_summary":
                    contacts = agent.get_contacts()
                    memories = agent.vault_manager.get_all_memories()
                    reminders = agent.get_reminders()
                    
                    summary = f"""# Relationship Memory Summary

## Contacts ({len(contacts)})
{chr(10).join([f"- {c.get('name', 'Unknown')}: {c.get('details', {})}" for c in contacts[:10]])}
{'...' if len(contacts) > 10 else ''}

## Recent Memories ({len(memories)})
{chr(10).join([f"- {m.get('contact_name', 'Unknown')}: {m.get('summary', '')}" for m in memories[:5]])}
{'...' if len(memories) > 5 else ''}

## Upcoming Reminders ({len(reminders)})
{chr(10).join([f"- {r.get('contact_name', 'Unknown')}: {r.get('title', '')} ({r.get('date', '')})" for r in reminders[:5]])}
{'...' if len(reminders) > 5 else ''}
"""
                    
                    return GetPromptResult(
                        description="Relationship memory summary",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(type="text", text=summary)
                            )
                        ]
                    )
                
                elif request.params.name == "contact_analysis":
                    contact_name = args.get("contact_name")
                    
                    if contact_name:
                        # Analyze specific contact
                        contact_memories = agent.get_memories(contact_name)
                        contact_reminders = agent.get_reminders(contact_name)
                        
                        analysis = f"""# Contact Analysis: {contact_name}

## Memories ({len(contact_memories)})
{chr(10).join([f"- {m.get('summary', '')} ({m.get('created_at', '')})" for m in contact_memories])}

## Reminders ({len(contact_reminders)})
{chr(10).join([f"- {r.get('title', '')} ({r.get('date', '')})" for r in contact_reminders])}

## Relationship Insights
- Total interactions recorded: {len(contact_memories)}
- Future scheduled interactions: {len(contact_reminders)}
"""
                    else:
                        # General analysis
                        contacts = agent.get_contacts()
                        memories = agent.vault_manager.get_all_memories()
                        
                        analysis = f"""# Contact Network Analysis

## Overview
- Total contacts: {len(contacts)}
- Total memories: {len(memories)}
- Most active relationships: {', '.join([m.get('contact_name', 'Unknown') for m in memories[:3]])}

## Contact Categories
{chr(10).join([f"- {c.get('name', 'Unknown')}: {len([m for m in memories if m.get('contact_name', '').lower() == c.get('name', '').lower()])} memories" for c in contacts[:10]])}
"""
                    
                    return GetPromptResult(
                        description=f"Contact analysis for {contact_name or 'all contacts'}",
                        messages=[
                            PromptMessage(
                                role="user", 
                                content=TextContent(type="text", text=analysis)
                            )
                        ]
                    )
                
            except Exception as e:
                logger.error(f"Error in get_prompt: {str(e)}")
                return GetPromptResult(
                    description="Error generating prompt",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(type="text", text=f"Error: {str(e)}")
                        )
                    ]
                )
    
    async def run(self, transport):
        """Run the MCP server"""
        async with self.server.run(transport) as ctx:
            await ctx.wait_for_completion()


# Server instance
mcp_server = RelationshipMemoryMCPServer()

if __name__ == "__main__":
    import mcp.server.stdio
    
    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await mcp_server.run(mcp.server.Session(read_stream, write_stream))
    
    asyncio.run(main())
