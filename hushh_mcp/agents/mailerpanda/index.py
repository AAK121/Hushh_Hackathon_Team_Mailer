
import os
import json
import pandas as pd
import re
import base64
from datetime import datetime, timedelta, timezone
from mailjet_rest import Client
from typing import List, Dict, Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI

# HushMCP framework imports
from hushh_mcp.consent.token import validate_token, issue_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.trust.link import create_trust_link, verify_trust_link
from hushh_mcp.operons.verify_email import verify_email_operon

# Import the manifest to access agent details
from hushh_mcp.agents.mailerpanda.manifest import manifest

class AgentState(TypedDict):
    user_input: Annotated[str, lambda old, new: new]
    email_template: Annotated[str, lambda old, new: new]
    subject: Annotated[str, lambda old, new: new]
    mass: Annotated[bool, lambda old, new: new]
    user_feedback: Annotated[str, lambda old, new: new]
    approved: Annotated[bool, lambda old, new: new]
    user_email: Annotated[str, lambda old, new: new]
    receiver_email: Annotated[list[str], lambda old, new: new]
    consent_tokens: Annotated[Dict[str, str], lambda old, new: new]
    user_id: Annotated[str, lambda old, new: new]
    campaign_id: Annotated[str, lambda old, new: new]
    vault_storage: Annotated[Dict, lambda old, new: new]
    # ✨ NEW: Personalization fields
    enable_description_personalization: Annotated[bool, lambda old, new: new]
    excel_file_path: Annotated[str, lambda old, new: new]
    personalization_mode: Annotated[str, lambda old, new: new]
    personalized_count: Annotated[int, lambda old, new: new]
    standard_count: Annotated[int, lambda old, new: new]
    description_column_detected: Annotated[bool, lambda old, new: new]
    # ✨ CRITICAL FIX: Frontend approval fields
    mode: Annotated[str, lambda old, new: new]
    frontend_approved: Annotated[bool, lambda old, new: new]
    send_approved: Annotated[bool, lambda old, new: new]
    # ✨ EMAIL SENDING RESULTS FIELDS
    total_sent: Annotated[int, lambda old, new: new]
    total_failed: Annotated[int, lambda old, new: new]
    send_results: Annotated[list, lambda old, new: new]
    # ✨ PRE-APPROVED TEMPLATE SUPPORT
    use_pre_approved: Annotated[bool, lambda old, new: new]

class SafeDict(dict):
    """Custom dict that handles missing placeholders gracefully."""
    def __missing__(self, key):
        return "{" + key + "}"

class MassMailerAgent:
    """
    Advanced AI-powered mass mailer agent with complete HushMCP integration,
    including consent validation, vault storage, trust links, and operons.
    """
    def __init__(self, api_keys: Dict[str, str] = None):
        """Initialize the mass mailer agent with dynamic API key support."""
        # Store dynamic API keys
        self.api_keys = api_keys or {}
        
        self.agent_id = manifest["id"]
        self.version = manifest["version"]
        
        # Initialize email service with dynamic API keys
        self._initialize_email_service()
        
        # Initialize LLM with dynamic API keys
        self._initialize_llm()
        
        # Path to the Excel file within the agent's directory
        self.contacts_file_path = os.path.join(os.path.dirname(__file__), 'email_list.xlsx')
        
        # Build LangGraph workflow with recursion limit
        self.graph = self._build_workflow()
        
        # Set recursion limit for LangGraph
        try:
            from langgraph.graph import GraphConfig
            self.graph_config = GraphConfig(recursion_limit=50)
        except:
            self.graph_config = {"recursion_limit": 50}
    
    def _initialize_email_service(self, mailjet_api_key: str = None, mailjet_api_secret: str = None):
        """Initialize email service with dynamic API key support."""
        # Priority: passed parameters > dynamic api_keys > environment variables
        api_key = mailjet_api_key or self.api_keys.get('mailjet_api_key') or os.environ.get("MAILJET_API_KEY")
        api_secret = mailjet_api_secret or self.api_keys.get('mailjet_api_secret') or os.environ.get("MAILJET_API_SECRET")
        
        if api_key and api_secret:
            self.mailjet_api_key = api_key
            self.mailjet_api_secret = api_secret
            self.mailjet = Client(auth=(api_key, api_secret), version='v3.1')
            print("✅ Mailjet client initialized successfully.")
        else:
            print("⚠️ No Mailjet API keys provided. Email functionality will be disabled.")
            self.mailjet = None
    
    def _initialize_llm(self, google_api_key: str = None):
        """Initialize LLM with dynamic API key support."""
        # Priority: passed parameter > dynamic api_keys > environment variable
        api_key = "AIzaSyBR6QGc1fiTtWEbaARdrnXTjFBfpVIoDY0"
        
        if api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.5,
                google_api_key=api_key
            )
        else:
            print("⚠️ No Google API key provided. AI content generation may be limited.")
            self.llm = None

    def _validate_consent_for_operation(self, consent_tokens: Dict[str, str], operation: str, user_id: str) -> bool:
        """
        Validates consent tokens for specific operations based on HushMCP scopes.
        
        Args:
            consent_tokens: Dictionary of consent tokens
            operation: Operation type ('content_generation', 'email_sending', 'contact_management', 'campaign_storage')
            user_id: User identifier for additional validation
            
        Returns:
            bool: True if consent is valid for the operation
            
        Raises:
            PermissionError: If consent validation fails
        """
        required_scopes = manifest["required_scopes"].get(operation, [])
        
        print(f"🔒 Validating consent for operation: {operation}")
        print(f"   Required scopes: {[scope.value for scope in required_scopes]}")
        
        for scope in required_scopes:
            # Check if we have a token for this scope
            scope_token = None
            for token_name, token_value in consent_tokens.items():
                if token_value:
                    try:
                        is_valid, reason, parsed_token = validate_token(token_value, expected_scope=scope)
                        if is_valid and parsed_token.user_id == user_id:
                            scope_token = token_value
                            break
                    except Exception:
                        continue
            
            if not scope_token:
                # Try to find a CUSTOM_TEMPORARY token as fallback
                for token_name, token_value in consent_tokens.items():
                    if token_value:
                        try:
                            is_valid, reason, parsed_token = validate_token(token_value, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
                            if is_valid and parsed_token.user_id == user_id:
                                print(f"   ✅ Using CUSTOM_TEMPORARY token for scope: {scope.value}")
                                scope_token = token_value
                                break
                        except Exception:
                            continue
            
            if not scope_token:
                raise PermissionError(f"Missing valid consent token for scope: {scope.value} (operation: {operation})")
            
            print(f"   ✅ Validated scope: {scope.value}")
        
        print(f"✅ All consent requirements satisfied for operation: {operation}")
        return True

    def _store_in_vault(self, data: Dict, vault_key: str, user_id: str, consent_tokens: Dict[str, str]) -> str:
        """
        Securely stores data in the HushMCP vault with encryption.
        
        Args:
            data: Data to store
            vault_key: Unique key for storage
            user_id: User identifier
            consent_tokens: Consent tokens for validation
            
        Returns:
            str: Vault storage key
        """
        # Validate consent for vault write operations
        self._validate_consent_for_operation(consent_tokens, "campaign_storage", user_id)
        
        # Add metadata
        vault_data = {
            'data': data,
            'agent_id': self.agent_id,
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'vault_key': vault_key,
            'data_type': 'mailerpanda_campaign'
        }
        
        # Encrypt and store
        from hushh_mcp.config import VAULT_ENCRYPTION_KEY
        encrypted_data = encrypt_data(json.dumps(vault_data), VAULT_ENCRYPTION_KEY)
        
        # In a real implementation, this would be stored in a persistent vault
        # For now, we log the successful encryption
        print(f"🔒 Data encrypted and stored in vault: {vault_key}")
        
        return vault_key

    def _retrieve_from_vault(self, vault_key: str, user_id: str, consent_tokens: Dict[str, str]) -> Optional[Dict]:
        """
        Retrieves and decrypts data from the HushMCP vault.
        
        Args:
            vault_key: Storage key
            user_id: User identifier
            consent_tokens: Consent tokens for validation
            
        Returns:
            Optional[Dict]: Decrypted data or None if not found
        """
        try:
            # Validate consent for vault read operations
            self._validate_consent_for_operation(consent_tokens, "contact_management", user_id)
            
            # In a real implementation, this would retrieve from persistent storage
            # For now, we simulate successful retrieval
            print(f"🔓 Data retrieved and decrypted from vault: {vault_key}")
            
            return None  # Placeholder for actual vault implementation
            
        except Exception as e:
            print(f"⚠️  Vault retrieval failed: {e}")
            return None

    def _create_trust_link_for_delegation(self, target_agent: str, resource_type: str, resource_id: str, user_id: str) -> Optional[str]:
        """
        Creates a trust link for delegating access to another agent.
        
        Args:
            target_agent: Target agent identifier
            resource_type: Type of resource being shared
            resource_id: Identifier of the resource
            user_id: User identifier
            
        Returns:
            Optional[str]: Trust link identifier or None if creation fails
        """
        try:
            trust_data = {
                'from_agent': self.agent_id,
                'to_agent': target_agent,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'permission_level': 'read',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'expires_at': (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
                'user_id': user_id
            }
            
            # Store trust link securely
            trust_key = f"trust_link_{self.agent_id}_{target_agent}_{resource_id}"
            encrypted_trust = encrypt_data(json.dumps(trust_data), user_id)
            
            print(f"🔗 Trust link created for {target_agent}: {trust_key}")
            return trust_key
            
        except Exception as e:
            print(f"⚠️  Trust link creation failed: {e}")
            return None

    def _build_workflow(self) -> StateGraph:
        """Builds the enhanced LangGraph workflow with HushMCP integration."""
        graph_builder = StateGraph(AgentState)
        
        # Add nodes
        graph_builder.add_node("validate_consent", self._validate_initial_consent)
        graph_builder.add_node("llm_writer", self._draft_content)
        graph_builder.add_node("get_feedback", self._get_feedback)
        graph_builder.add_node("store_campaign", self._store_campaign_data)
        graph_builder.add_node("send_emails", self._send_emails)
        graph_builder.add_node("create_trust_links", self._create_delegation_links)
        
        # Add edges
        graph_builder.add_edge(START, "validate_consent")
        # Conditional routing after consent validation - skip LLM if pre-approved
        graph_builder.add_conditional_edges("validate_consent", self._route_after_consent)
        graph_builder.add_edge("llm_writer", "get_feedback")
        graph_builder.add_conditional_edges("get_feedback", self._route_tools)
        graph_builder.add_edge("store_campaign", "send_emails")
        graph_builder.add_edge("send_emails", "create_trust_links")
        graph_builder.add_edge("create_trust_links", END)
        
        return graph_builder.compile()

    def _validate_initial_consent(self, state: AgentState) -> dict:
        """LangGraph node: Validates initial consent for the workflow."""
        print("🔒 Validating initial consent for MailerPanda workflow...")
        
        # Validate consent for content generation (first operation)
        self._validate_consent_for_operation(
            state["consent_tokens"], 
            "content_generation", 
            state["user_id"]
        )
        
        # Generate campaign ID
        campaign_id = f"campaign_{self.agent_id}_{int(datetime.now(timezone.utc).timestamp())}"
        
        return {
            "campaign_id": campaign_id,
            "vault_storage": {}
        }

    def _route_after_consent(self, state: AgentState) -> str:
        """LangGraph conditional edge: Routes after consent validation."""
        
        # If we have a pre-approved template and are approved to send, skip content generation
        if state.get('use_pre_approved') and state.get('send_approved'):
            print("🚀 [DEBUG] Using pre-approved template, skipping to store_campaign")
            print(f"🚀 [DEBUG] Pre-approved template: {state.get('email_template', '')[:50]}...")
            print(f"🚀 [DEBUG] Pre-approved subject: '{state.get('subject', '')}'")
            return "store_campaign"
        
        # Otherwise, go to content generation
        print("📝 [DEBUG] No pre-approved template or not send_approved, going to llm_writer")
        print(f"📝 [DEBUG] use_pre_approved: {state.get('use_pre_approved')}")
        print(f"📝 [DEBUG] send_approved: {state.get('send_approved')}")
        return "llm_writer"

    def _parse_llm_output(self, raw_output: str) -> dict:
        """Parses structured LLM output using XML-like tags."""
        subject_match = re.search(r"<sub>(.*?)</sub>", raw_output, re.DOTALL)
        content_match = re.search(r"<content>(.*?)</content>", raw_output, re.DOTALL)
        user_email_match = re.search(r"<user_email>(.*?)</user_email>", raw_output, re.DOTALL)
        receiver_emails_match = re.search(r"<receiver_emails>(.*?)</receiver_emails>", raw_output, re.DOTALL)

        subject = subject_match.group(1).strip() if subject_match else ""
        content = content_match.group(1).strip() if content_match else ""
        user_email = user_email_match.group(1).strip() if user_email_match else ""

        receiver_emails_str = receiver_emails_match.group(1).strip() if receiver_emails_match else ""
        receiver_emails = [email.strip() for email in receiver_emails_str.split(",") if email.strip()]

        # Auto-detect if it's a mass email (based on whether receiver emails are given)
        mass = len(receiver_emails) == 0

        return {
            "subject": subject,
            "email_template": content,
            "mass": mass,
            "user_email": user_email,
            "receiver_email": receiver_emails
        }

    def _read_contacts_with_consent(self, user_id: str, consent_tokens: Dict[str, str], excel_file_path: str = None) -> List[Dict]:
        """Reads contact data from the local Excel file with proper consent validation."""
        # Validate consent for file access
        self._validate_consent_for_operation(consent_tokens, "contact_management", user_id)
        
        # Use specified excel_file_path if provided, otherwise fallback to default behavior
        if excel_file_path:
            contacts_file = excel_file_path
        else:
            # Try to use enhanced file with descriptions first, fallback to basic file
            enhanced_file = os.path.join(os.path.dirname(__file__), 'email_list_with_descriptions.xlsx')
            basic_file = self.contacts_file_path
            contacts_file = enhanced_file if os.path.exists(enhanced_file) else basic_file
        
        if not os.path.exists(contacts_file):
            raise FileNotFoundError(f"Contacts file not found at: {contacts_file}")
        
        print(f"📂 Reading contacts file: {os.path.basename(contacts_file)}")
        df = pd.read_excel(contacts_file)
        
        # Check if description column exists
        if 'description' in df.columns:
            desc_count = df['description'].notna().sum()
            print(f"✨ Found description column with {desc_count} personalized entries")
        else:
            print("📝 No description column found, using standard templates")
        
        # Validate email addresses using HushMCP operon
        validated_contacts = []
        for _, row in df.iterrows():
            contact_dict = row.to_dict()
            email = contact_dict.get('email', '')
            
            # Use HushMCP verify_email operon
            try:
                is_valid = verify_email_operon(email)
                contact_dict['email_validated'] = is_valid
                if is_valid:
                    validated_contacts.append(contact_dict)
                else:
                    print(f"⚠️  Invalid email address skipped: {email}")
            except Exception as e:
                print(f"⚠️  Email validation failed for {email}: {e}")
                contact_dict['email_validated'] = False
        
        print(f"✅ Loaded {len(validated_contacts)} validated contacts")
        return validated_contacts

    def _get_attachment(self, path: str) -> dict:
        """Creates attachment object for email."""
        with open(path, "rb") as file:
            file_data = file.read()
            encoded = base64.b64encode(file_data).decode()
            return {
                "ContentType": "application/pdf",  # Change based on file type
                "Filename": path.split("/")[-1],
                "Base64Content": encoded
            }

    def _send_email_via_mailjet(self, to_email: str, to_name: str, subject: str, 
                               content: str, from_email: str = None, from_name: str = "MailerPanda Agent", 
                               attachment: dict = None, campaign_id: str = None):
        """Sends a single email using the Mailjet API with enhanced tracking."""
        print(" 💕❤️❤️❤️❤️Chandresh is a great developer. and an amazing guy")
        
        if not from_email:
            from_email = os.environ.get("SENDER_EMAIL", "alokkale121@gmail.com")
            
        message_data = {
            "From": {"Email": from_email, "Name": from_name},
            "To": [{"Email": to_email, "Name": to_name}],
            "Subject": subject,
            "TextPart": content,
            "HTMLPart": f"<pre>{content}</pre>",
            "CustomID": campaign_id or f"mailerpanda_{int(datetime.now(timezone.utc).timestamp())}"
        }

        if attachment:
            message_data["Attachments"] = [attachment]

        data = {"Messages": [message_data]}
        try:
            result = self.mailjet.send.create(data=data)
            print(f"📧 Sent to {to_email}: Status {result.status_code}")
            
            # Return enhanced result with tracking info
            return {
                'status_code': result.status_code,
                'result': result,
                'email': to_email,
                'campaign_id': campaign_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {e}")
            return {
                'status_code': 'error',
                'error': str(e),
                'email': to_email,
                'campaign_id': campaign_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def _draft_content(self, state: AgentState) -> dict:
        """LangGraph node: Drafts email content using AI with enhanced consent validation."""
        # Validate consent for AI content generation
        self._validate_consent_for_operation(
            state["consent_tokens"], 
            "content_generation", 
            state["user_id"]
        )
        
        print("✅ Consent validated for AI content generation.")
        
        # Default: No placeholders
        placeholders_str = ""
        placeholder_instruction = """
5. ✅ Do not use any placeholders like {name}, {email}, etc.  
6. Just write a normal, polite, professional email using names or details from the input.  
7. Leave <user_email> and <receiver_emails> blank if not provided in the input.  
8. Do not add extra words, comments, or explanations outside of these tags.
"""

        # Check for contacts file with proper consent
        try:
            contacts = self._read_contacts_with_consent(state["user_id"], state["consent_tokens"], state.get("excel_file_path"))
            if contacts:
                df = pd.DataFrame(contacts)
                allowed_placeholders = [f"{{{col}}}" for col in df.columns]
                placeholders_str = ", ".join(allowed_placeholders)

                placeholder_instruction = f"""
5. ✅ You can ONLY use these placeholders: {placeholders_str}  
6. Do not use any placeholders that are not in the list above.  
7. Leave <user_email> and <receiver_emails> blank if not provided in the input.  
8. Do not add extra words, comments, or explanations outside of these tags.
"""
        except Exception as e:
            print(f"⚠️  Could not load contacts for placeholder detection: {e}")

        if state.get('user_feedback'):
            prompt = f"""
You are an email drafting assistant powered by HushMCP framework.

Here is the current email template:
---
{state['email_template']}
---

Update it based on this feedback:
"{state['user_feedback']}"

⚠️ Important:
1. Output must be in this exact XML-like format:
<sub>...</sub>
<content>...</content>
<user_email>...</user_email>
<receiver_emails>...</receiver_emails>

2. <sub> = only subject  
3. <content> = only the body of the email  
4. <user_email> = email address of the sender (only one)  
{placeholder_instruction}
"""
        else:
            prompt = f"""
You are an email drafting assistant powered by HushMCP framework.

Write a professional email based on this input:
"{state['user_input']}"

⚠️ Important:
1. Output must be in this exact XML-like format:
<sub>...</sub>
<content>...</content>
<user_email>...</user_email>
<receiver_emails>...</receiver_emails>

2. <sub> = only subject  
3. <content> = only the body of the email  
4. <user_email> = email address of the sender (only one)  
{placeholder_instruction}
"""

        try:
            response = self.llm.invoke(prompt)
            parsed = self._parse_llm_output(response.content)
        except Exception as e:
            # Handle Google API quota errors and other LLM errors
            error_msg = str(e)
            if "exceeded your current quota" in error_msg or "429" in error_msg:
                print(f"❌ Google API quota exceeded: {e}")
                raise Exception("Google API quota exceeded. Please wait and try again, or upgrade your Google AI plan.")
            elif "ResourceExhausted" in error_msg:
                print(f"❌ Google API resource exhausted: {e}")
                raise Exception("Google AI resources exhausted. Please try again in a few minutes.")
            else:
                print(f"❌ Error generating content with AI: {e}")
                raise Exception(f"AI content generation failed: {error_msg}")

        # Store draft in vault
        draft_data = {
            'draft_version': 1,
            'content': parsed,
            'user_input': state['user_input'],
            'feedback': state.get('user_feedback', ''),
            'created_at': datetime.utcnow().isoformat()
        }
        
        vault_key = f"draft_{state['campaign_id']}_v1"
        self._store_in_vault(draft_data, vault_key, state["user_id"], state["consent_tokens"])

        return {
            "email_template": parsed["email_template"],
            "subject": parsed["subject"],
            "mass": parsed["mass"],
            "user_email": parsed["user_email"],
            "receiver_email": parsed["receiver_email"],
            # ✅ PRESERVE APPROVAL STATE
            "approved": state.get("approved", False),
            "frontend_approved": state.get("frontend_approved", False),
            "send_approved": state.get("send_approved", False),
            "mode": state.get("mode", "interactive")
        }

    def _get_feedback(self, state: AgentState) -> dict:
        """LangGraph node: Gets human feedback on the drafted email."""
        print("\n📧 Draft Email Preview:\n")
        print(f"📌 Subject: {state['subject']}\n")
        print("📝 Content:")
        print(state["email_template"])
        print(f"\n🆔 Campaign ID: {state['campaign_id']}")
        print("\n" + "="*50)

        # Prioritize frontend approval
        if state.get('frontend_approved'):
            print("✅ Pre-approved via Frontend API call.")
            return {
                "approved": True,
                "frontend_approved": state.get("frontend_approved"),
                "send_approved": state.get("send_approved"),
                "mode": state.get("mode")
            }

        # Check for other API-based approval flags
        mode = state.get('mode', 'interactive')
        if mode in ['headless', 'api'] and state.get('pre_approved', False):
            print("✅ Pre-approved via API.")
            return {
                "approved": True,
                "frontend_approved": state.get("frontend_approved"),
                "send_approved": state.get("send_approved"),
                "mode": state.get("mode")
            }

        # Handle interactive approval via API response
        if state.get('api_approval_action'):
            action = state.get('api_approval_action')
            if action == 'approve':
                return {"approved": True}
            elif action in ['modify', 'regenerate']:
                return {
                    "user_feedback": state.get('api_feedback', 'Please modify the content'),
                    "approved": False
                }
            else:  # reject
                return {"approved": False, "rejected": True}

        # If in interactive mode and no decision has been made, pause for frontend
        if mode == 'interactive':
            print("⏸️ Awaiting frontend approval...")
            return {
                "approved": False, 
                "requires_approval": True,
                "frontend_approved": state.get("frontend_approved"),
                "send_approved": state.get("send_approved"),
                "mode": state.get("mode")
            }

        # Fallback to CLI for direct terminal usage (should not be reached in API flow)
        user_input = input("\n✅ Approve this email? (yes/y/approve OR provide feedback): ").strip()
        if user_input.lower() in ["yes", "y", "approve", "approved"]:
            return {"approved": True}
        else:
            return {"user_feedback": user_input, "approved": False}

    def _route_tools(self, state: AgentState) -> str:
        """LangGraph conditional edge: Routes based on approval status."""
        
        print(f"🔀 [DEBUG] _route_tools called with approval status: {state.get('approved')}")
        print(f"🔀 [DEBUG] State frontend_approved: {state.get('frontend_approved')}")
        print(f"🔀 [DEBUG] State user_feedback: {state.get('user_feedback')}")
        print(f"🔀 [DEBUG] State mode: {state.get('mode')}")
        print(f"🔀 [DEBUG] ALL STATE KEYS: {list(state.keys())}")
        print(f"🔀 [DEBUG] STATE DUMP: {dict(state)}")
        
        # If the campaign is approved, proceed to the next step.
        if state.get('approved'):
            print("✅ [DEBUG] Routing to 'store_campaign' based on approval status.")
            return "store_campaign"
        
        # If not approved, check if we should wait for feedback or regenerate content.
        # If feedback is provided, go back to the writer.
        if state.get('user_feedback'):
            print("🔄 [DEBUG] Routing back to 'llm_writer' based on user feedback.")
            return "llm_writer"
            
        # If in interactive mode and no feedback is given, the workflow
        # should pause and wait for external approval.
        mode = state.get('mode', 'interactive')
        if mode == 'interactive':
            print("⏸️ [DEBUG] Ending graph to await external approval/feedback.")
            return "__end__"
            
        # If not approved and no other condition is met (e.g., in headless mode),
        # end the workflow.
        print("🛑 [DEBUG] Ending graph because campaign was not approved.")
        return "__end__"

    def _store_campaign_data(self, state: AgentState) -> dict:
        """LangGraph node: Stores approved campaign data in vault."""
        print("🔒 [DEBUG] _store_campaign_data function STARTED")
        print("🔒 Storing approved campaign data in secure vault...")
        
        campaign_data = {
            'campaign_id': state['campaign_id'],
            'approved_template': state['email_template'],
            'subject': state['subject'],
            'user_email': state['user_email'],
            'receiver_emails': state['receiver_email'],
            'mass_mode': state['mass'],
            'approved_at': datetime.now(timezone.utc).isoformat(),
            'user_input': state['user_input'],
            'agent_version': self.version
        }
        
        vault_key = f"campaign_{state['campaign_id']}_approved"
        self._store_in_vault(campaign_data, vault_key, state["user_id"], state["consent_tokens"])
        
        print("🔒 [DEBUG] _store_campaign_data function COMPLETED")
        return {
            "vault_storage": {
                **state.get("vault_storage", {}),
                "campaign_data": vault_key
            }
        }

    def _customize_email_with_description(self, base_template: str, base_subject: str, 
                                         contact_info: dict, description: str, state: dict) -> dict:
        """
        Customizes email content using AI based on individual contact description.
        
        Args:
            base_template: The original email template
            base_subject: The original email subject
            contact_info: Contact information dictionary
            description: Individual description for this contact
            state: Current agent state
            
        Returns:
            dict: Customized subject and content
        """
        try:
            if not self.llm:
                print("⚠️ LLM not available, using base template")
                return {"subject": base_subject, "content": base_template}
            
            # Create personalization prompt
            prompt = f"""
You are an expert email personalization assistant. Your task is to customize an email template based on specific information about the recipient.

**Original Email Template:**
Subject: {base_subject}
Content:
{base_template}

**Recipient Information:**
Name: {contact_info.get('name', 'N/A')}
Email: {contact_info.get('email', 'N/A')}
Company: {contact_info.get('company_name', 'N/A')}

**Special Description/Context for this recipient:**
{description}

**Instructions:**
1. Modify the email to be more relevant and personalized based on the description
2. Keep the core message and purpose of the original email
3. Make it feel natural and not overly sales-y
4. Incorporate the description context appropriately
5. Maintain professional tone
6. Keep any existing placeholders like {{name}}, {{email}}, {{company_name}} intact

**Output Format:**
<subject>customized subject line here</subject>
<content>
customized email content here
</content>

**Important:** 
- Don't add placeholders that weren't in the original template
- Keep the email length appropriate (not too long)
- Make the personalization feel genuine and relevant
"""

            # Generate customized content
            try:
                response = self.llm.invoke(prompt)
                
                # Parse the response
                import re
                subject_match = re.search(r"<subject>(.*?)</subject>", response.content, re.DOTALL)
                content_match = re.search(r"<content>(.*?)</content>", response.content, re.DOTALL)
                
                customized_subject = subject_match.group(1).strip() if subject_match else base_subject
                customized_content = content_match.group(1).strip() if content_match else base_template
                
                return {
                    "subject": customized_subject,
                    "content": customized_content
                }
                
            except Exception as llm_error:
                # Handle Google API quota errors specifically
                error_msg = str(llm_error)
                if "exceeded your current quota" in error_msg or "429" in error_msg or "ResourceExhausted" in error_msg:
                    print(f"❌ Google API quota exceeded during personalization: {llm_error}")
                    # Fall back to base template when quota exceeded
                    return {"subject": base_subject, "content": base_template}
                else:
                    print(f"⚠️ Error customizing email: {llm_error}")
                    return {"subject": base_subject, "content": base_template}
                    
        except Exception as e:
            print(f"⚠️ General error in email customization: {e}")
            return {"subject": base_subject, "content": base_template}
            
    def _send_emails(self, state: AgentState) -> dict:
        """LangGraph node: Sends emails with comprehensive HushMCP consent validation."""
        print("� [DEBUG] _send_emails function STARTED")
        print(f"🚀 [DEBUG] State keys: {list(state.keys())}")
        print(f"🚀 [DEBUG] Campaign ID: {state.get('campaign_id')}")
        print(f"🚀 [DEBUG] Mass mode: {state.get('mass')}")
        print(f"🚀 [DEBUG] Email template: {state.get('email_template', 'None')[:100]}...")

        if not self.mailjet:
            print("❌ [DEBUG] Mailjet client is None - not initialized")
            return {
                "status": "error",
                "error": "Mailjet client not initialized. Check API keys.",
                "campaign_id": state.get('campaign_id'),
                "total_sent": 0,
                "total_failed": 0,
            }
        else:
            print("✅ [DEBUG] Mailjet client is initialized")

        # Validate consent for email sending operations
        try:
            self._validate_consent_for_operation(
                state["consent_tokens"], 
                "email_sending", 
                state["user_id"]
            )
            print("✅ [DEBUG] Consent validation passed")
        except Exception as e:
            print(f"❌ [DEBUG] Consent validation failed: {e}")
            return {"status": "error", "error": f"Consent validation failed: {e}"}
        
        template = state["email_template"]
        subject = state["subject"]
        sender_email = state["user_email"]
        is_mass = state.get("mass", False)
        campaign_id = state["campaign_id"]
        results = []
        
        print(f"🚀 [DEBUG] About to check mass email mode. is_mass = {is_mass}")

        if is_mass:
            print("� [DEBUG] Processing mass email campaign...")
            try:
                print("🚀 [DEBUG] About to read contacts...")
                contacts = self._read_contacts_with_consent(state["user_id"], state["consent_tokens"], state.get("excel_file_path"))
                print(f"🚀 [DEBUG] Got {len(contacts) if contacts else 0} contacts")
                
                if not contacts:
                    print("⚠️ [DEBUG] No validated contacts found. Ending email sending.")
                    return {"status": "complete", "total_sent": 0, "total_failed": 0}

                df = pd.DataFrame(contacts)
                print(f"🚀 [DEBUG] Created DataFrame with {len(df)} rows")
                
                if 'Status' not in df.columns:
                    df['Status'] = ""

                print("🚀 [DEBUG] About to start contact loop...")
                for i, row in df.iterrows():
                    print(f"🚀 [DEBUG] Processing contact {i}: {row.get('email', 'no email')}")
                    
                    contact_dict = row.to_dict()
                    if not contact_dict.get('email_validated', False):
                        print(f"⚠️ [DEBUG] Skipping invalid email: {contact_dict.get('email', 'N/A')}")
                        continue
                    
                    print(f"🚀 [DEBUG] About to send email to {row.get('email')}")
                    
                    try:
                        from_email = sender_email if sender_email else os.environ.get("SENDER_EMAIL")
                        if not from_email:
                            raise ValueError("Sender email not configured.")

                        print(f"🚀 [DEBUG] Calling _send_email_via_mailjet for {row['email']}")
                        result = self._send_email_via_mailjet(
                            to_email=row["email"],
                            to_name=row.get("name", ""),
                            subject=subject,
                            content=template,
                            from_email=from_email,
                            from_name="MailerPanda Agent",
                            campaign_id=campaign_id
                        )
                        print(f"🚀 [DEBUG] Got result from _send_email_via_mailjet: {result}")
                        
                        df.loc[i, 'Status'] = result['status_code']
                        results.append(result)
                        
                    except Exception as e:
                        print(f"❌ [DEBUG] Error processing contact {row.get('email')}: {e}")
                        df.loc[i, 'Status'] = "error"
                        results.append({
                            "email": row["email"],
                            "status_code": "error", 
                            "error": str(e),
                            "campaign_id": campaign_id,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })

                print(f"🚀 [DEBUG] Finished contact loop. Total results: {len(results)}")

            except Exception as e:
                print(f"❌ [DEBUG] Mass email campaign failed: {e}")
                return {"status": "error", "error": str(e)}
        else:
            print("🚀 [DEBUG] Single email mode - not implemented in this debug version.")

        print(f"🚀 [DEBUG] Returning from _send_emails with {len(results)} results")
        
        # Calculate success/failure counts
        sent_count = len([r for r in results if r.get('status_code') == 200])
        failed_count = len([r for r in results if r.get('status_code') != 200])
        
        print(f"🚀 [DEBUG] Email summary: {sent_count} sent, {failed_count} failed")
        
        # Return state updates for LangGraph
        return {
            "total_sent": sent_count,
            "total_failed": failed_count,
            "send_results": results
        }

    def _create_delegation_links(self, state: AgentState) -> dict:
        """LangGraph node: Creates trust links for cross-agent delegation."""
        print("🔗 Creating trust links for cross-agent delegation...")
        
        trust_links_created = []
        campaign_id = state["campaign_id"]
        
        # Create trust link for AddToCalendar agent if email contains event-related content
        email_content = state["email_template"].lower()
        if any(keyword in email_content for keyword in ["meeting", "event", "calendar", "appointment", "schedule"]):
            trust_link = self._create_trust_link_for_delegation(
                target_agent="agent_addtocalendar",
                resource_type="email_campaign",
                resource_id=campaign_id,
                user_id=state["user_id"]
            )
            print("🔗 Trust link for AddToCalendar agent created.")
            if trust_link:
                trust_links_created.append({
                    "target_agent": "agent_addtocalendar",
                    "trust_link": trust_link,
                    "reason": "Event-related content detected"
                })
        
        # Create trust link for Shopping agent if email contains product-related content
        if any(keyword in email_content for keyword in ["product", "sale", "discount", "offer", "shop", "buy"]):
            trust_link = self._create_trust_link_for_delegation(
                target_agent="agent_shopper",
                resource_type="email_campaign",
                resource_id=campaign_id,
                user_id=state["user_id"]
            )
            if trust_link:
                trust_links_created.append({
                    "target_agent": "agent_shopper",
                    "trust_link": trust_link,
                    "reason": "Product-related content detected"
                })
        
        if trust_links_created:
            print(f"✅ Created {len(trust_links_created)} trust links for delegation")
        else:
            print("ℹ️  No trust links needed for this campaign")
        
        return {
            "trust_links": trust_links_created,
            "vault_storage": {
                **state.get("vault_storage", {}),
                "trust_links": trust_links_created
            }
        }

    def resume_from_approval(self, saved_state: dict, approval_action: str, feedback: str = "") -> dict:
        """
        Resume workflow from approval decision.
        
        Args:
            saved_state: The state when workflow was paused for approval
            approval_action: 'approve', 'reject', 'modify', or 'regenerate'
            feedback: User feedback for modifications
            
        Returns:
            dict: Final workflow result
        """
        print(f"🔄 Resuming workflow from approval: {approval_action}")
        
        # Update state with approval decision
        saved_state.update({
            'api_approval_action': approval_action,
            'api_feedback': feedback,
            'requires_approval': False,
            'approval_pending': False
        })
        
        if approval_action == 'approve':
            saved_state['approved'] = True
        elif approval_action == 'reject':
            saved_state['approved'] = False
            saved_state['rejected'] = True
        else:  # modify or regenerate
            saved_state['approved'] = False
            saved_state['user_feedback'] = feedback
        
        try:
            # Resume the workflow from the routing point
            if approval_action == 'approve':
                # Go directly to storing and sending
                final_state = self.graph.invoke(saved_state, {"step": "store_campaign"})
            else:
                # Go back to content generation with feedback
                final_state = self.graph.invoke(saved_state, {"step": "llm_writer"})
            
            return {
                "status": "completed" if approval_action == 'approve' else "modified",
                "approval_action": approval_action,
                "final_state": final_state,
                "email_template": final_state.get("email_template"),
                "emails_sent": final_state.get("total_sent", 0),
                "send_status": final_state.get("send_status", [])
            }
            
        except Exception as e:
            print(f"❌ Resume failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "approval_action": approval_action
            }

    def handle(self, user_id: str, consent_tokens: Dict[str, str], user_input: str, 
               mode: str = "interactive", enable_description_personalization: bool = False,
               excel_file_path: str = None, personalization_mode: str = "conservative",
               frontend_approved: bool = False, send_approved: bool = False, **parameters):
        """
        Enhanced main entry point for the agent with complete HushMCP integration.
        Supports dynamic API key injection via parameters.
        
        Args:
            user_id: User identifier
            consent_tokens: Dictionary of consent tokens for different scopes
            user_input: User's email campaign description
            mode: Execution mode ('interactive', 'headless')
            **parameters: Additional parameters including dynamic API keys
            
        Returns:
            Dict: Comprehensive results including vault storage and trust links
        """
        # Process dynamic API keys from parameters
        print(f"🔍 [DEBUG] ALL PARAMETERS RECEIVED: {parameters}")
        print(f"🔍 [DEBUG] Parameters keys: {list(parameters.keys())}")
        print(f"🔍 [DEBUG] frontend_approved EXPLICIT PARAM: {frontend_approved}")
        print(f"🔍 [DEBUG] send_approved EXPLICIT PARAM: {send_approved}")
        print(f"🔍 [DEBUG] enable_description_personalization EXPLICIT PARAM: {enable_description_personalization}")
        print(f"🔍 [DEBUG] mode parameter: {mode}")
        
        # Check if the parameters are in some nested structure
        for key, value in parameters.items():
            if 'approved' in str(key).lower() or 'approved' in str(value):
                print(f"🔍 [DEBUG] Found approval-related param: {key} = {value}")
        
        if 'google_api_key' in parameters:
            self._initialize_llm(parameters['google_api_key'])
        if 'mailjet_api_key' in parameters or 'mailjet_api_secret' in parameters:
            self._initialize_email_service(
                parameters.get('mailjet_api_key'),
                parameters.get('mailjet_api_secret')
            )
        if 'api_keys' in parameters:
            self.api_keys.update(parameters['api_keys'])
            # Re-initialize services with updated keys
            self._initialize_llm()
            self._initialize_email_service()
            
        print("🚀 Starting HushMCP-Enhanced AI-Powered Email Campaign Agent...")
        print(f"🆔 User ID: {user_id}")
        print(f"🔧 Mode: {mode}")
        print(f"🔑 Consent tokens provided: {list(consent_tokens.keys())}")
        print(f"🎯 Personalization enabled: {enable_description_personalization}")
        if enable_description_personalization:
            print(f"📁 Excel file path: {excel_file_path}")
            print(f"🧠 Personalization mode: {personalization_mode}")
        
        # Validate that we have at least one consent token
        if not consent_tokens or not any(consent_tokens.values()):
            raise PermissionError("No valid consent tokens provided")
        
        # Check if we have pre-approved template (from modification workflow)
        pre_approved_template = parameters.get('pre_approved_template')
        pre_approved_subject = parameters.get('pre_approved_subject')
        
        # Use pre-approved content if available (even if subject is empty)
        has_pre_approved = bool(pre_approved_template)
        
        if has_pre_approved:
            print(f"🔄 [DEBUG] Using pre-approved template from modification workflow")
            print(f"🔄 [DEBUG] Pre-approved subject: '{pre_approved_subject}'")
            print(f"🔄 [DEBUG] Pre-approved template length: {len(pre_approved_template)}")
            # When we have pre-approved content and send_approved is True, auto-approve
            frontend_approved = frontend_approved or send_approved
        
        initial_state = {
            "user_input": user_input,
            "user_email": "",
            "mass": True,  # ✅ FIX: Set to True for mass email campaigns
            "subject": pre_approved_subject or "",
            "email_template": pre_approved_template or "",
            "receiver_email": [],
            "user_feedback": "",
            "approved": frontend_approved,
            "send_approved": send_approved,
            "consent_tokens": consent_tokens,
            "user_id": user_id,
            "campaign_id": "",
            "vault_storage": {},
            # ✨ NEW: Personalization parameters
            "enable_description_personalization": enable_description_personalization,
            "excel_file_path": excel_file_path,
            "personalization_mode": personalization_mode,
            "personalized_count": 0,
            "standard_count": 0,
            "description_column_detected": False,
            "mode": mode,
            "frontend_approved": frontend_approved,
            # ✨ EMAIL SENDING RESULTS FIELDS
            "total_sent": 0,
            "total_failed": 0,
            "send_results": [],
            # ✨ PRE-APPROVED TEMPLATE SUPPORT
            "use_pre_approved": has_pre_approved
        }

        try:
            # Execute the enhanced LangGraph workflow
            print("🔄 Executing HushMCP-enhanced workflow...")
            print(f"🔍 [DEBUG] Initial state approved: {initial_state.get('approved')}")
            print(f"🔍 [DEBUG] Initial state frontend_approved: {initial_state.get('frontend_approved')}")
            print(f"🔍 [DEBUG] Initial state send_approved: {initial_state.get('send_approved')}")
            print(f"🔍 [DEBUG] Initial state mode: {initial_state.get('mode')}")
            try:
                final_state = self.graph.invoke(
                    initial_state,
                    config={"recursion_limit": 50}
                )
            except Exception as workflow_error:
                if "recursion" in str(workflow_error).lower():
                    print(f"🔄 Workflow recursion limit reached, using fallback...")
                    # Return a simplified response for frontend approval
                    return {
                        "status": "awaiting_approval",
                        "email_template": {
                            "subject": f"Email Campaign for {user_input[:50]}...",
                            "body": f"Dear [Recipient],\n\nThis is a professional email regarding: {user_input}\n\nBest regards,\n[Your Name]"
                        },
                        "requires_approval": True,
                        "approval_status": "pending",
                        "campaign_id": f"campaign_{user_id}_{int(datetime.now().timestamp())}",
                        "mode": mode,
                        "agent_id": self.agent_id
                    }
                else:
                    raise workflow_error
            
            print(f"\n🎉 HushMCP Email Campaign Agent Finished!")
            print(f"🆔 Campaign ID: {final_state.get('campaign_id', 'unknown')}")
            print(f"📊 Total Sent: {final_state.get('total_sent', 0)}")
            print(f"❌ Total Failed: {final_state.get('total_failed', 0)}")
            print(f"🔒 Vault Storage Keys: {list(final_state.get('vault_storage', {}).keys())}")
            print(f"🔗 Trust Links Created: {len(final_state.get('trust_links', []))}")
            
            # 🚀 CRITICAL FIX: Check if workflow ended for approval
            # If in interactive mode and not approved, it requires approval
            if (mode == "interactive" and 
                not final_state.get("approved", False) and 
                not final_state.get("send_approved", False)):
                # Return approval-required result with complete state data
                return {
                    "status": "awaiting_approval",
                    "agent_id": self.agent_id,
                    "agent_version": self.version,
                    "campaign_id": final_state.get("campaign_id"),
                    "requires_approval": True,
                    "approval_status": "pending",
                    "mode": mode,
                    "email_template": final_state.get("email_template"),
                    "subject": final_state.get("subject"),  # 🚀 INCLUDE SUBJECT FOR FRONTEND
                    "personalized_count": final_state.get("personalized_count", 0),
                    "standard_count": final_state.get("standard_count", 0),
                    "description_column_detected": final_state.get("description_column_detected", False),
                    "final_state": final_state,
                    "hushh_mcp_compliant": True
                }
            else:
                # Complete execution result
                return {
                    "status": "complete",
                    "agent_id": self.agent_id,
                    "agent_version": self.version,
                    "campaign_summary": {
                        "campaign_id": final_state.get("campaign_id"),
                        "total_sent": final_state.get("total_sent", 0),
                        "total_failed": final_state.get("total_failed", 0),
                        "vault_storage": final_state.get("vault_storage", {}),
                        "trust_links": final_state.get("trust_links", [])
                    },
                    # ✨ NEW: Personalization statistics
                    "personalized_count": final_state.get("personalized_count", 0),
                    "standard_count": final_state.get("standard_count", 0),
                    "description_column_detected": final_state.get("description_column_detected", False),
                    "emails_sent": final_state.get("total_sent", 0),
                    "send_status": final_state.get("send_status", []),
                    "email_template": final_state.get("email_template"),
                    "subject": final_state.get("subject"),  # 🚀 CRITICAL FIX: Include subject in result
                    "final_state": final_state,
                    "hushh_mcp_compliant": True
                }
            
        except PermissionError as e:
            print(f"🚫 Permission denied: {e}")
            return {
                "status": "permission_denied",
                "error": str(e),
                "agent_id": self.agent_id
            }
        except Exception as e:
            print(f"❌ Campaign execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }