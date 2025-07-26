import os
import pandas as pd
import base64
from typing import Dict, List, Any, Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from mailjet_rest import Client
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from django.conf import settings

# Load environment variables
load_dotenv()

class AgentState(TypedDict):
    user_input: Annotated[str, lambda old, new: new]
    email_template: Annotated[str, lambda old, new: new]
    email_subject: Annotated[str, lambda old, new: new]
    user_feedback: Annotated[str, lambda old, new: new]
    approved: Annotated[bool, lambda old, new: new]
    placeholders: Annotated[List[str], lambda old, new: new]
    conversation_history: Annotated[List[Dict], lambda old, new: old + [new] if isinstance(new, dict) else old]

class MailerService:
    def __init__(self):
        try:
            self.llm = ChatOllama(model="llama3-groq-tool-use")
            self.ollama_available = True
        except Exception as e:
            print(f"Ollama not available: {e}")
            self.ollama_available = False
        
        self.graph_builder = StateGraph(AgentState)
        self._build_graph()
        
    def _build_graph(self):
        """Build the LangGraph workflow"""
        self.graph_builder.add_node("draft_content", self._draft_content)
        self.graph_builder.add_node("get_feedback", self._get_feedback)
        self.graph_builder.add_node("send_emails", self._send_emails)
        
        self.graph_builder.add_edge(START, "draft_content")
        self.graph_builder.add_edge("draft_content", "get_feedback")
        self.graph_builder.add_conditional_edges("get_feedback", self._route_tools)
        self.graph_builder.add_edge("send_emails", END)
        
        self.graph = self.graph_builder.compile()
    
    def _draft_content(self, state: AgentState) -> Dict[str, Any]:
        """Generate email content using LLM"""
        if not self.ollama_available:
            # Fallback template if Ollama is not available
            template = self._generate_fallback_template(state['user_input'])
            subject = self._generate_fallback_subject(state['user_input'])
            placeholders = ['name', 'email', 'company_name']
        else:
            if state.get('user_feedback'):
                prompt = f"""
                Here is the current email template:
                ---
                {state['email_template']}
                ---
                Update it based on this feedback:
                "{state['user_feedback']}"
                
                Requirements:
                1. Only write the email message content
                2. Use placeholders like {{name}}, {{email}}, {{company_name}} where needed
                3. Don't add any comments or explanations
                4. Make it professional and engaging
                """
            else:
                prompt = f"""
                Write a professional email based on this input:
                "{state['user_input']}"

                Requirements:
                1. Only write the email message content (no subject line)
                2. Use placeholders like {{name}}, {{email}}, {{company_name}} where needed
                3. Don't add any comments or explanations
                4. Make it professional and engaging
                5. Keep it concise but informative
                """
            
            try:
                response = self.llm.invoke(prompt)
                template = response.content
                
                # Generate subject
                subject_prompt = f"""
                Based on this email content, write a compelling email subject line:
                "{template}"
                
                Requirements:
                1. Only write the subject line (no quotes or explanations)
                2. Keep it under 50 characters
                3. Make it engaging and professional
                """
                subject_response = self.llm.invoke(subject_prompt)
                subject = subject_response.content.strip().strip('"').strip("'")
                
                # Extract placeholders
                placeholders = self._extract_placeholders(template)
                
            except Exception as e:
                print(f"Error generating content: {e}")
                template = self._generate_fallback_template(state['user_input'])
                subject = self._generate_fallback_subject(state['user_input'])
                placeholders = ['name', 'email', 'company_name']
        
        return {
            "email_template": template,
            "email_subject": subject,
            "placeholders": placeholders
        }
    
    def _extract_placeholders(self, template: str) -> List[str]:
        """Extract placeholder names from template"""
        import re
        placeholders = re.findall(r'\{(\w+)\}', template)
        return list(set(placeholders))
    
    def _generate_fallback_template(self, user_input: str) -> str:
        """Generate a fallback template when LLM is not available"""
        if "welcome" in user_input.lower():
            return """Dear {name},

Welcome to our team! We're excited to have you join {company_name}.

We'll be sending you more information shortly to {email}.

Best regards,
The Team"""
        elif "newsletter" in user_input.lower():
            return """Hi {name},

Thank you for subscribing to our newsletter! We're excited to keep you updated with the latest news and updates.

You can always reach us at {email} if you have any questions.

Best regards,
{company_name} Team"""
        else:
            return """Dear {name},

Thank you for your interest in {company_name}. We appreciate your time and look forward to connecting with you.

If you have any questions, please don't hesitate to reach out to us at {email}.

Best regards,
The Team"""
    
    def _generate_fallback_subject(self, user_input: str) -> str:
        """Generate a fallback subject when LLM is not available"""
        if "welcome" in user_input.lower():
            return "Welcome to the Team!"
        elif "newsletter" in user_input.lower():
            return "Welcome to Our Newsletter"
        else:
            return "Thank You for Your Interest"
    
    def _get_feedback(self, state: AgentState) -> Dict[str, Any]:
        """This would be handled by the web interface"""
        # In the web version, this is handled by the frontend
        return {"approved": True}  # Auto-approve for now
    
    def _route_tools(self, state: AgentState) -> str:
        """Route to appropriate next step"""
        if state['approved']:
            return "send_emails"
        else:
            return "draft_content"
    
    def _send_emails(self, state: AgentState) -> Dict[str, Any]:
        """This will be handled separately by the email campaign system"""
        return {}
    
    def generate_email_template(self, user_input: str, feedback: str = None) -> Dict[str, Any]:
        """Generate email template based on user input"""
        initial_state = {
            "user_input": user_input,
            "email_template": "",
            "email_subject": "",
            "user_feedback": feedback or "",
            "approved": False,
            "placeholders": [],
            "conversation_history": []
        }
        
        # Run only the draft_content step
        result = self._draft_content(initial_state)
        
        return {
            "template": result["email_template"],
            "subject": result["email_subject"],
            "placeholders": result["placeholders"]
        }
    
    def send_email_via_mailjet(self, to_email: str, to_name: str, subject: str, 
                             content: str, from_email: str = "dragnoid121@gmail.com", 
                             from_name: str = "AAK", attachment=None) -> Dict[str, Any]:
        """Send email using Mailjet API"""
        try:
            api_key = os.getenv("MJ_APIKEY_PUBLIC", "cca56ed08f5272f813370d7fc5a34a24")
            secret_key = os.getenv("MJ_APIKEY_PRIVATE", "60fb43675233e2ac775f1c6cb8fe455c")
            
            mailjet = Client(auth=(api_key, secret_key), version='v3.1')
            
            message_data = {
                "From": {"Email": from_email, "Name": from_name},
                "To": [{"Email": to_email, "Name": to_name}],
                "Subject": subject,
                "TextPart": content,
                "HTMLPart": f"<pre style='font-family: Arial, sans-serif; white-space: pre-wrap;'>{content}</pre>"
            }
            
            if attachment:
                message_data["Attachments"] = [attachment]
            
            data = {"Messages": [message_data]}
            result = mailjet.send.create(data=data)
            
            return {
                "success": result.status_code == 200,
                "status_code": result.status_code,
                "response": result.json()
            }
            
        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "error": str(e)
            }
    
    def process_excel_file(self, file_path: str) -> List[Dict[str, str]]:
        """Process Excel file and return list of contacts"""
        try:
            df = pd.read_excel(file_path)
            
            # Standardize column names
            df.columns = df.columns.str.lower().str.strip()
            
            contacts = []
            for _, row in df.iterrows():
                contact = {}
                
                # Map common column variations
                name_cols = ['name', 'full_name', 'first_name', 'firstname', 'fname']
                email_cols = ['email', 'email_address', 'e_mail']
                company_cols = ['company', 'company_name', 'organization', 'org']
                
                for col in name_cols:
                    if col in df.columns:
                        contact['name'] = str(row[col]) if pd.notna(row[col]) else ''
                        break
                
                for col in email_cols:
                    if col in df.columns:
                        contact['email'] = str(row[col]) if pd.notna(row[col]) else ''
                        break
                
                for col in company_cols:
                    if col in df.columns:
                        contact['company_name'] = str(row[col]) if pd.notna(row[col]) else ''
                        break
                
                # Add any other columns as placeholders
                for col in df.columns:
                    if col not in ['name', 'email', 'company_name'] and col not in name_cols + email_cols + company_cols:
                        key = col.replace(' ', '_').replace('-', '_')
                        contact[key] = str(row[col]) if pd.notna(row[col]) else ''
                
                if contact.get('email'):  # Only add if email exists
                    contacts.append(contact)
            
            return contacts
            
        except Exception as e:
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    def get_attachment(self, file_path: str) -> Dict[str, str]:
        """Convert file to base64 attachment format"""
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()
                encoded = base64.b64encode(file_data).decode()
                
                # Determine content type based on file extension
                extension = file_path.split('.')[-1].lower()
                content_type_map = {
                    'pdf': 'application/pdf',
                    'doc': 'application/msword',
                    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'txt': 'text/plain',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png'
                }
                
                return {
                    "ContentType": content_type_map.get(extension, "application/octet-stream"),
                    "Filename": file_path.split("/")[-1],
                    "Base64Content": encoded
                }
        except Exception as e:
            raise Exception(f"Error processing attachment: {str(e)}")
