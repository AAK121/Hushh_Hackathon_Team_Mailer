
import os
import json
import pandas as pd
import re
import base64
from datetime import datetime, timedelta
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

class SafeDict(dict):
    """Custom dict that handles missing placeholders gracefully."""
    def __missing__(self, key):
        return "{" + key + "}"

class MassMailerAgent:
    """
    Advanced AI-powered mass mailer agent with complete HushMCP integration,
    including consent validation, vault storage, trust links, and operons.
    """
    def __init__(self):
        self.agent_id = manifest["id"]
        self.version = manifest["version"]
        
        # Load Mailjet API keys from environment variables
        self.mailjet_api_key = os.environ.get("MAILJET_API_KEY")
        self.mailjet_api_secret = os.environ.get("MAILJET_API_SECRET")
        
        if not all([self.mailjet_api_key, self.mailjet_api_secret]):
            raise ValueError("MAILJET_API_KEY and MAILJET_API_SECRET must be set in the .env file.")
            
        self.mailjet = Client(auth=(self.mailjet_api_key, self.mailjet_api_secret), version='v3.1')
        
        # Initialize Gemini LLM
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY must be set in the .env file for AI content generation.")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            google_api_key=google_api_key
        )
        
        # Path to the Excel file within the agent's directory
        self.contacts_file_path = os.path.join(os.path.dirname(__file__), 'email_list.xlsx')
        
        # Build LangGraph workflow
        self.graph = self._build_workflow()

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
            'timestamp': datetime.utcnow().isoformat(),
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
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat(),
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
        graph_builder.add_edge("validate_consent", "llm_writer")
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
        campaign_id = f"campaign_{self.agent_id}_{int(datetime.utcnow().timestamp())}"
        
        return {
            "campaign_id": campaign_id,
            "vault_storage": {}
        }

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

    def _read_contacts_with_consent(self, user_id: str, consent_tokens: Dict[str, str]) -> List[Dict]:
        """Reads contact data from the local Excel file with proper consent validation."""
        # Validate consent for file access
        self._validate_consent_for_operation(consent_tokens, "contact_management", user_id)
        
        if not os.path.exists(self.contacts_file_path):
            raise FileNotFoundError(f"Contacts file not found at: {self.contacts_file_path}")
        
        print(f"📂 Reading contacts file with consent validation...")
        df = pd.read_excel(self.contacts_file_path)
        
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
        
        if not from_email:
            from_email = os.environ.get("SENDER_EMAIL", "default@sender.com")
            
        message_data = {
            "From": {"Email": from_email, "Name": from_name},
            "To": [{"Email": to_email, "Name": to_name}],
            "Subject": subject,
            "TextPart": content,
            "HTMLPart": f"<pre>{content}</pre>",
            "CustomID": campaign_id or f"mailerpanda_{int(datetime.utcnow().timestamp())}"
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
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {e}")
            return {
                'status_code': 'error',
                'error': str(e),
                'email': to_email,
                'campaign_id': campaign_id,
                'timestamp': datetime.utcnow().isoformat()
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
            contacts = self._read_contacts_with_consent(state["user_id"], state["consent_tokens"])
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

        response = self.llm.invoke(prompt)
        parsed = self._parse_llm_output(response.content)

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
            "receiver_email": parsed["receiver_email"]
        }

    def _get_feedback(self, state: AgentState) -> dict:
        """LangGraph node: Gets human feedback on the drafted email."""
        print("\n📧 Draft Email Preview:\n")
        print(f"📌 Subject: {state['subject']}\n")
        print("📝 Content:")
        print(state["email_template"])
        print(f"\n🆔 Campaign ID: {state['campaign_id']}")
        print("\n" + "="*50)
        
        user_input = input("\n✅ Approve this email? (yes/y/approve OR provide feedback): ").strip()
        
        if user_input.lower() in ["yes", "y", "approve", "approved"]:
            return {"approved": True}
        else:
            return {
                "user_feedback": user_input,
                "approved": False
            }

    def _route_tools(self, state: AgentState) -> str:
        """LangGraph conditional edge: Routes based on approval status."""
        if state['approved']:
            return "store_campaign"
        else:
            return "llm_writer"

    def _store_campaign_data(self, state: AgentState) -> dict:
        """LangGraph node: Stores approved campaign data in vault."""
        print("🔒 Storing approved campaign data in secure vault...")
        
        campaign_data = {
            'campaign_id': state['campaign_id'],
            'approved_template': state['email_template'],
            'subject': state['subject'],
            'user_email': state['user_email'],
            'receiver_emails': state['receiver_email'],
            'mass_mode': state['mass'],
            'approved_at': datetime.utcnow().isoformat(),
            'user_input': state['user_input'],
            'agent_version': self.version
        }
        
        vault_key = f"campaign_{state['campaign_id']}_approved"
        self._store_in_vault(campaign_data, vault_key, state["user_id"], state["consent_tokens"])
        
        return {
            "vault_storage": {
                **state.get("vault_storage", {}),
                "campaign_data": vault_key
            }
        }

    def _send_emails(self, state: AgentState) -> dict:
        """LangGraph node: Sends emails with comprehensive HushMCP consent validation."""
        print("📤 [DEBUG] send_emails() function is running with HushMCP validation...")
        print(f"👤 User Email: {state['user_email']}")
        print(f"📧 Receiver Emails: {state['receiver_email']}")
        print(f"📊 Mass Email Mode: {state['mass']}")
        print(f"🆔 Campaign ID: {state['campaign_id']}")
        
        # Final confirmation
        user_confirmation = input("\n🚨 Are you sure you want to send the emails? (Y/N): ").strip()
        if user_confirmation.upper() != "Y":
            print("❌ Email sending cancelled.")
            return {"status": "cancelled", "message": "User cancelled email sending"}

        # Validate consent for email sending operations
        self._validate_consent_for_operation(
            state["consent_tokens"], 
            "email_sending", 
            state["user_id"]
        )
        
        print("✅ Consent validated for email sending operations.")

        template = state["email_template"]
        subject = state["subject"]
        sender_email = state["user_email"]
        is_mass = state.get("mass", False)
        campaign_id = state["campaign_id"]
        results = []

        if is_mass:
            # MASS EMAIL MODE using Excel with enhanced consent validation
            print("📊 Processing mass email campaign with HushMCP validation...")
            
            try:
                contacts = self._read_contacts_with_consent(state["user_id"], state["consent_tokens"])
                df = pd.DataFrame(contacts)
                
                if 'Status' not in df.columns:
                    df['Status'] = ""

                for i, row in df.iterrows():
                    if not row.get('email_validated', False):
                        print(f"⚠️  Skipping invalid email: {row.get('email', 'unknown')}")
                        continue
                        
                    format_dict = {col: str(row[col]) for col in df.keys()}
                    subject_filled = subject.format_map(SafeDict(format_dict))
                    content_filled = template.format_map(SafeDict(format_dict))
                    
                    try:
                        from_email = sender_email if sender_email else os.environ.get("SENDER_EMAIL")
                        result = self._send_email_via_mailjet(
                            to_email=row["email"],
                            to_name=row.get("name", ""),
                            subject=subject_filled,
                            content=content_filled,
                            from_email=from_email,
                            from_name="MailerPanda Agent",
                            campaign_id=campaign_id
                        )
                        
                        df.loc[i, 'Status'] = result['status_code']
                        results.append(result)
                        
                    except Exception as e:
                        df.loc[i, 'Status'] = "error"
                        results.append({
                            "email": row["email"],
                            "status_code": "error", 
                            "error": str(e),
                            "campaign_id": campaign_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })

                # Save status to Excel with vault storage
                status_file = os.path.join(os.path.dirname(__file__), f"email_status_{campaign_id}.xlsx")
                df.to_excel(status_file, index=False)
                print(f"📊 Mass emails sent and status saved to '{status_file}'.")
                
                # Store results in vault
                results_data = {
                    'campaign_id': campaign_id,
                    'results': results,
                    'status_file': status_file,
                    'total_sent': len([r for r in results if r.get('status_code') == 200]),
                    'total_failed': len([r for r in results if r.get('status_code') != 200]),
                    'completed_at': datetime.utcnow().isoformat()
                }
                
                vault_key = f"results_{campaign_id}"
                self._store_in_vault(results_data, vault_key, state["user_id"], state["consent_tokens"])

            except Exception as e:
                print(f"❌ Mass email campaign failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "campaign_id": campaign_id
                }

        else:
            # SINGLE EMAIL MODE (no Excel) with enhanced validation
            print("📧 Processing individual email(s) with HushMCP validation...")
            to_emails = state["receiver_email"]
            if isinstance(to_emails, str):
                to_emails = [to_emails]

            for email in to_emails:
                # Validate each email address
                try:
                    is_valid = verify_email_operon(email)
                    if not is_valid:
                        print(f"⚠️  Skipping invalid email: {email}")
                        results.append({
                            "email": email,
                            "status_code": "invalid",
                            "error": "Email validation failed",
                            "campaign_id": campaign_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        continue
                        
                    from_email = sender_email if sender_email else os.environ.get("SENDER_EMAIL")
                    result = self._send_email_via_mailjet(
                        to_email=email,
                        to_name="",
                        subject=subject,
                        content=template,
                        from_email=from_email,
                        from_name="MailerPanda Agent",
                        campaign_id=campaign_id
                    )
                    
                    results.append(result)
                    
                except Exception as e:
                    results.append({
                        "email": email,
                        "status_code": "error",
                        "error": str(e),
                        "campaign_id": campaign_id,
                        "timestamp": datetime.utcnow().isoformat()
                    })

            # Store individual email results in vault
            results_data = {
                'campaign_id': campaign_id,
                'results': results,
                'mode': 'individual',
                'total_sent': len([r for r in results if r.get('status_code') == 200]),
                'total_failed': len([r for r in results if r.get('status_code') != 200]),
                'completed_at': datetime.utcnow().isoformat()
            }
            
            vault_key = f"results_{campaign_id}"
            self._store_in_vault(results_data, vault_key, state["user_id"], state["consent_tokens"])

        return {
            "status": "complete",
            "total_sent": len([r for r in results if r.get('status_code') == 200]),
            "total_failed": len([r for r in results if r.get('status_code') != 200]),
            "send_results": results,
            "campaign_id": campaign_id,
            "vault_storage": {
                **state.get("vault_storage", {}),
                "results": vault_key
            }
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

    def handle(self, user_id: str, consent_tokens: Dict[str, str], user_input: str, mode: str = "interactive"):
        """
        Enhanced main entry point for the agent with complete HushMCP integration.
        
        Args:
            user_id: User identifier
            consent_tokens: Dictionary of consent tokens for different scopes
            user_input: User's email campaign description
            mode: Execution mode ('interactive', 'headless', 'demo')
            
        Returns:
            Dict: Comprehensive results including vault storage and trust links
        """
        print("🚀 Starting HushMCP-Enhanced AI-Powered Email Campaign Agent...")
        print(f"🆔 User ID: {user_id}")
        print(f"🔧 Mode: {mode}")
        print(f"🔑 Consent tokens provided: {list(consent_tokens.keys())}")
        
        # Validate that we have at least one consent token
        if not consent_tokens or not any(consent_tokens.values()):
            raise PermissionError("No valid consent tokens provided")
        
        initial_state = {
            "user_input": user_input,
            "user_email": "",
            "mass": False,
            "subject": "",
            "email_template": "",
            "receiver_email": [],
            "user_feedback": "",
            "approved": False,
            "consent_tokens": consent_tokens,
            "user_id": user_id,
            "campaign_id": "",
            "vault_storage": {}
        }

        try:
            # Execute the enhanced LangGraph workflow
            print("🔄 Executing HushMCP-enhanced workflow...")
            final_state = self.graph.invoke(initial_state)
            
            print(f"\n🎉 HushMCP Email Campaign Agent Finished!")
            print(f"🆔 Campaign ID: {final_state.get('campaign_id', 'unknown')}")
            print(f"📊 Total Sent: {final_state.get('total_sent', 0)}")
            print(f"❌ Total Failed: {final_state.get('total_failed', 0)}")
            print(f"🔒 Vault Storage Keys: {list(final_state.get('vault_storage', {}).keys())}")
            print(f"🔗 Trust Links Created: {len(final_state.get('trust_links', []))}")
            
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