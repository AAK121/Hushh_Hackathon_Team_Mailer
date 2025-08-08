
import os
import pandas as pd
import re
import base64
from mailjet_rest import Client
from typing import List, Dict, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI

# HushMCP framework imports
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope

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
    consent_token: Annotated[str, lambda old, new: new]
    user_id: Annotated[str, lambda old, new: new]

class SafeDict(dict):
    """Custom dict that handles missing placeholders gracefully."""
    def __missing__(self, key):
        return "{" + key + "}"

class MassMailerAgent:
    """
    Advanced AI-powered mass mailer agent with human-in-the-loop approval,
    LangGraph workflow, and consent-driven operations.
    """
    def __init__(self):
        self.agent_id = manifest["id"]
        
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

    def _build_workflow(self) -> StateGraph:
        """Builds the LangGraph workflow for the email agent."""
        graph_builder = StateGraph(AgentState)
        
        # Add nodes
        graph_builder.add_node("llm_writer", self._draft_content)
        graph_builder.add_node("get_feedback", self._get_feedback)
        graph_builder.add_node("send_emails", self._send_emails)
        
        # Add edges
        graph_builder.add_edge(START, "llm_writer")
        graph_builder.add_edge("llm_writer", "get_feedback")
        graph_builder.add_conditional_edges("get_feedback", self._route_tools)
        graph_builder.add_edge("send_emails", END)
        
        return graph_builder.compile()

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

    def _read_contacts(self) -> List[Dict]:
        """Reads contact data from the local Excel file."""
        if not os.path.exists(self.contacts_file_path):
            raise FileNotFoundError(f"Contacts file not found at: {self.contacts_file_path}")
        
        df = pd.read_excel(self.contacts_file_path)
        return df.to_dict('records')

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
                               attachment: dict = None):
        """Sends a single email using the Mailjet API."""
        
        if not from_email:
            from_email = os.environ.get("SENDER_EMAIL", "default@sender.com")
            
        message_data = {
            "From": {"Email": from_email, "Name": from_name},
            "To": [{"Email": to_email, "Name": to_name}],
            "Subject": subject,
            "TextPart": content,
            "HTMLPart": f"<pre>{content}</pre>"
        }

        if attachment:
            message_data["Attachments"] = [attachment]

        data = {"Messages": [message_data]}
        try:
            result = self.mailjet.send.create(data=data)
            print(f"📧 Sent to {to_email}: Status {result.status_code}")
            return result
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {e}")
            raise

    def _draft_content(self, state: AgentState) -> dict:
        """LangGraph node: Drafts email content using AI."""
        # Validate consent for AI content generation
        is_valid, reason, _ = validate_token(
            state["consent_token"], 
            expected_scope=ConsentScope.CUSTOM_TEMPORARY
        )
        if not is_valid:
            raise PermissionError(f"AI Content Generation Access Denied: {reason}")
        
        print("✅ Consent validated for AI content generation.")
        
        # Default: No placeholders
        placeholders_str = ""
        placeholder_instruction = """
5. ✅ Do not use any placeholders like {name}, {email}, etc.  
6. Just write a normal, polite, professional email using names or details from the input.  
7. Leave <user_email> and <receiver_emails> blank if not provided in the input.  
8. Do not add extra words, comments, or explanations outside of these tags.
"""

        if os.path.exists(self.contacts_file_path):
            df = pd.read_excel(self.contacts_file_path)
            allowed_placeholders = [f"{{{col}}}" for col in df.columns]
            placeholders_str = ", ".join(allowed_placeholders)

            placeholder_instruction = f"""
5. ✅ You can ONLY use these placeholders: {placeholders_str}  
6. Do not use any placeholders that are not in the list above.  
7. Leave <user_email> and <receiver_emails> blank if not provided in the input.  
8. Do not add extra words, comments, or explanations outside of these tags.
"""

        if state.get('user_feedback'):
            prompt = f"""
You are an email drafting assistant.

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
You are an email drafting assistant.

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
            return "send_emails"
        else:
            return "llm_writer"

    def _send_emails(self, state: AgentState) -> dict:
        """LangGraph node: Sends emails with consent validation."""
        print("📤 [DEBUG] send_emails() function is running...")
        print(f"👤 User Email: {state['user_email']}")
        print(f"📧 Receiver Emails: {state['receiver_email']}")
        print(f"📊 Mass Email Mode: {state['mass']}")
        
        # Final confirmation
        user_confirmation = input("\n🚨 Are you sure you want to send the emails? (Y/N): ").strip()
        if user_confirmation.upper() != "Y":
            print("❌ Email sending cancelled.")
            return {"status": "cancelled", "message": "User cancelled email sending"}

        # Validate consent for email sending
        is_valid, reason, _ = validate_token(
            state["consent_token"], 
            expected_scope=ConsentScope.CUSTOM_TEMPORARY
        )
        if not is_valid:
            raise PermissionError(f"Email Sending Access Denied: {reason}")
        
        print("✅ Consent validated for email sending.")

        template = state["email_template"]
        subject = state["subject"]
        sender_email = state["user_email"]
        is_mass = state.get("mass", False)
        results = []

        if is_mass:
            # MASS EMAIL MODE using Excel
            print("📊 Processing mass email campaign...")
            contacts = self._read_contacts()
            df = pd.DataFrame(contacts)
            
            if 'Status' not in df.columns:
                df['Status'] = ""

            for i, row in df.iterrows():
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
                        from_name="MailerPanda Agent"
                    )
                    
                    df.loc[i, 'Status'] = result.status_code
                    results.append({
                        "email": row["email"],
                        "status_code": result.status_code,
                        "response": "success" if result.status_code == 200 else "failed"
                    })
                    
                except Exception as e:
                    df.loc[i, 'Status'] = "error"
                    results.append({
                        "email": row["email"],
                        "status_code": "error",
                        "response": str(e)
                    })

            # Save status to Excel
            status_file = os.path.join(os.path.dirname(__file__), "email_status.xlsx")
            df.to_excel(status_file, index=False)
            print(f"📊 Mass emails sent and status saved to '{status_file}'.")

        else:
            # SINGLE EMAIL MODE (no Excel)
            print("📧 Processing individual email(s)...")
            to_emails = state["receiver_email"]
            if isinstance(to_emails, str):
                to_emails = [to_emails]

            for email in to_emails:
                try:
                    from_email = sender_email if sender_email else os.environ.get("SENDER_EMAIL")
                    result = self._send_email_via_mailjet(
                        to_email=email,
                        to_name="",
                        subject=subject,
                        content=template,
                        from_email=from_email,
                        from_name="MailerPanda Agent"
                    )
                    
                    results.append({
                        "email": email,
                        "status_code": result.status_code,
                        "response": "success" if result.status_code == 200 else "failed"
                    })
                    
                except Exception as e:
                    results.append({
                        "email": email,
                        "status_code": "error",
                        "response": str(e)
                    })

        return {
            "status": "complete",
            "total_sent": len(results),
            "send_results": results
        }

    def handle(self, user_id: str, consent_token: str, user_input: str):
        """
        Main entry point for the agent with interactive LangGraph workflow.
        """
        print("🚀 Starting AI-Powered Email Campaign Agent...")
        
        initial_state = {
            "user_input": user_input,
            "user_email": "",
            "mass": False,
            "subject": "",
            "email_template": "",
            "receiver_email": [],
            "user_feedback": "",
            "approved": False,
            "consent_token": consent_token,
            "user_id": user_id
        }

        # Execute the LangGraph workflow
        final_state = self.graph.invoke(initial_state)
        
        print("\n🎉 Email Campaign Agent Finished!")
        return {
            "status": "complete",
            "final_state": final_state
        }