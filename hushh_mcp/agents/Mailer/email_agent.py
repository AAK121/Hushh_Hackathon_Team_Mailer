"""
Email Agent - Automated email drafting and sending system
Converted from agent.ipynb for frontend integration
"""

import re
import base64
import pandas as pd
from typing import Annotated, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from mailjet_rest import Client
import os
from pathlib import Path


class AgentState(TypedDict):
    user_input: Annotated[str, lambda old, new: new]
    email_template: Annotated[str, lambda old, new: new]
    subject: Annotated[str, lambda old, new: new]
    mass: Annotated[bool, lambda old, new: new]
    user_feedback: Annotated[str, lambda old, new: new]
    approved: Annotated[bool, lambda old, new: new]
    excel_file_path: Annotated[str, lambda old, new: new]


class EmailAgent:
    def __init__(self, google_api_key: str, mailjet_api_key: str, mailjet_secret_key: str):
        """Initialize the Email Agent with API credentials"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,
            google_api_key=google_api_key
        )
        self.mailjet_api_key = mailjet_api_key
        self.mailjet_secret_key = mailjet_secret_key
        self.graph = self._build_graph()
        
    def _build_graph(self):
        """Build the LangGraph workflow"""
        graph_builder = StateGraph(AgentState)
        
        graph_builder.add_node("llm_writer", self.draft_content)
        graph_builder.add_node("get_feedback", self.get_feedback)
        graph_builder.add_node("send_emails", self.send_emails)
        
        graph_builder.add_edge(START, "llm_writer")
        graph_builder.add_edge("llm_writer", "get_feedback")
        graph_builder.add_conditional_edges("get_feedback", self.route_tools)
        graph_builder.add_edge("send_emails", END)
        
        return graph_builder.compile()

    def parse_llm_output(self, raw_output: str) -> Dict[str, Any]:
        """Parse LLM output to extract subject, content, and mass flag"""
        subject_match = re.search(r"<sub>(.*?)</sub>", raw_output, re.DOTALL)
        content_match = re.search(r"<content>(.*?)</content>", raw_output, re.DOTALL)
        mass_match = re.search(r"<mass>(.*?)</mass>", raw_output, re.DOTALL)

        subject = subject_match.group(1).strip() if subject_match else ""
        content = content_match.group(1).strip() if content_match else ""
        mass_str = mass_match.group(1).strip() if mass_match else "false"
        mass = True if mass_str.lower() == "true" else False

        return {
            "subject": subject,
            "email_template": content,
            "mass": mass
        }

    def get_excel_placeholders(self, excel_path: str) -> list:
        """Get available placeholders from Excel file headers"""
        try:
            df = pd.read_excel(excel_path)
            return [f"{{{col}}}" for col in df.columns]
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return ["{name}", "{email}"]

    def draft_content(self, state: AgentState) -> Dict[str, Any]:
        """Draft email content using LLM"""
        excel_path = state.get('excel_file_path', '')
        allowed_placeholders = self.get_excel_placeholders(excel_path)
        placeholders_str = ", ".join(allowed_placeholders)

        if state['user_feedback']:
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
<mass>...</mass>

2. <sub> = only subject
3. <content> = only the body of the email
4. <mass> = "true" if this is for multiple recipients (mass email), "false" otherwise
5. ✅ You can ONLY use these placeholders: {placeholders_str}
6. Do not use any placeholders that are not in the list above.
7. Do not add extra words, comments, or explanations outside of these tags.
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
<mass>...</mass>

2. <sub> = only subject
3. <content> = only the body of the email
4. <mass> = "true" if this is for multiple recipients (mass email), "false" otherwise
5. ✅ You can ONLY use these placeholders: {placeholders_str}.
6. Do not use any placeholders that are not in the list above.
7. Do not add extra words, comments, or explanations outside of these tags.
"""

        response = self.llm.invoke(prompt)
        parsed = self.parse_llm_output(response.content)

        return {
            "email_template": parsed["email_template"],
            "subject": parsed["subject"],
            "mass": parsed["mass"]
        }

    def get_feedback(self, state: AgentState) -> Dict[str, Any]:
        """Get user feedback on the drafted email (for CLI mode)"""
        print("\n📨 Draft Email:\n")
        print(f"Subject: {state['subject']}")
        print(f"Content:\n{state['email_template']}")
        print("\n---")
        user_input = input("Approve this email? (yes or give feedback): ")
        if user_input.lower() in ["yes", "y", "approve", "approved"]:
            return {"approved": True}
        else:
            return {
                "user_feedback": user_input,
                "approved": False
            }

    def get_attachment(self, path: str) -> Dict[str, str]:
        """Encode file as base64 for email attachment"""
        try:
            with open(path, "rb") as file:
                file_data = file.read()
                encoded = base64.b64encode(file_data).decode()
                
                # Determine content type based on file extension
                extension = Path(path).suffix.lower()
                content_type_map = {
                    '.pdf': 'application/pdf',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    '.doc': 'application/msword',
                    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    '.xls': 'application/vnd.ms-excel',
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.txt': 'text/plain'
                }
                content_type = content_type_map.get(extension, 'application/octet-stream')
                
                return {
                    "ContentType": content_type,
                    "Filename": os.path.basename(path),
                    "Base64Content": encoded
                }
        except Exception as e:
            print(f"Error processing attachment: {e}")
            return None

    def send_email_via_mailjet(self, to_email: str, to_name: str, subject: str, 
                              content: str, from_email: str = "dragnoid121@gmail.com", 
                              from_name: str = "Hushh Team", attachment=None):
        """Send email via Mailjet API"""
        mailjet = Client(auth=(self.mailjet_api_key, self.mailjet_secret_key), version='v3.1')
        
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
            result = mailjet.send.create(data=data)
            return result
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return None

    class SafeDict(dict):
        """Safe dictionary for string formatting that leaves missing keys as-is"""
        def __missing__(self, key):
            return "{" + key + "}"

    def send_emails(self, state: AgentState) -> Dict[str, Any]:
        """Send emails to all recipients in Excel file"""
        template = state["email_template"]
        subject = state["subject"]
        excel_path = state.get('excel_file_path', '')
        
        if not excel_path or not os.path.exists(excel_path):
            print("❌ Excel file not found!")
            return {}
        
        try:
            df = pd.read_excel(excel_path)
            df = df.reset_index(drop=True)
            
            if 'Status' not in df.columns:
                df['Status'] = ""
            
            success_count = 0
            total_count = len(df)
            
            for i, row in df.iterrows():
                format_dict = {col: str(row[col]) for col in df.columns}
                subject_filled = subject.format_map(self.SafeDict(format_dict))
                content_filled = template.format_map(self.SafeDict(format_dict))

                result = self.send_email_via_mailjet(
                    to_email=row.get("email", ""),
                    to_name=row.get("name", ""),
                    subject=subject_filled,
                    content=content_filled
                )

                if result and result.status_code == 200:
                    df.loc[i, 'Status'] = "Sent"
                    success_count += 1
                else:
                    df.loc[i, 'Status'] = "Failed"

            # Save status to new file
            status_file = excel_path.replace('.xlsx', '_status.xlsx')
            df.to_excel(status_file, index=False)
            
            print(f"✅ Sent {success_count}/{total_count} emails successfully")
            print(f"📊 Status saved to: {status_file}")
            
            return {"emails_sent": success_count, "total_emails": total_count}
            
        except Exception as e:
            print(f"❌ Error sending emails: {e}")
            return {}

    def route_tools(self, state: AgentState) -> str:
        """Route to next tool based on approval status"""
        if state['approved']:
            return "send_emails"
        else:
            return "llm_writer"

    def run_agent(self, user_input: str, excel_file_path: str = "", auto_approve: bool = False) -> Dict[str, Any]:
        """Run the email agent workflow"""
        initial_state = {
            "user_input": user_input,
            "email_template": "",
            "subject": "",
            "mass": False,
            "user_feedback": "",
            "approved": auto_approve,
            "excel_file_path": excel_file_path
        }

        try:
            final_state = self.graph.invoke(initial_state)
            return final_state
        except Exception as e:
            print(f"❌ Error running agent: {e}")
            return {}

    def draft_email_only(self, user_input: str, excel_file_path: str = "") -> Dict[str, Any]:
        """Draft email without sending - for frontend preview"""
        state = {
            "user_input": user_input,
            "email_template": "",
            "subject": "",
            "mass": False,
            "user_feedback": "",
            "approved": False,
            "excel_file_path": excel_file_path
        }
        
        try:
            result = self.draft_content(state)
            return result
        except Exception as e:
            print(f"❌ Error drafting email: {e}")
            return {}


if __name__ == "__main__":
    # Example usage
    agent = EmailAgent(
        google_api_key="AIzaSyAYIuaAQJxmuspF5tyDEpJ3iYm6gVVQZOo",
        mailjet_api_key="cca56ed08f5272f813370d7fc5a34a24",
        mailjet_secret_key="60fb43675233e2ac775f1c6cb8fe455c"
    )
    
    # Run the agent
    result = agent.run_agent(
        "I want to send a welcome email to all the interns joining next week, emails are mentioned in the excel.",
        excel_file_path="email.xlsx"
    )
    print("Agent finished:", result)
