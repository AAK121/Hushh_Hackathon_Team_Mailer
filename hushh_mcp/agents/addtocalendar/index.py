# hushh_mcp/agents/addtocalendar/index.py
import os
import json
import base64
from typing import List, Dict
from bs4 import BeautifulSoup
import openai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# HushMCP framework imports
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.addtocalendar.manifest import manifest

class AddToCalendarAgent:
    """
    Translates the functionality of the addtocalendar.ipynb notebook
    into a structured, consent-driven agent.
    """
    def __init__(self):
        self.agent_id = manifest["id"]
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        # Correctly defines the path to credentials.json inside the agent's directory
        self.creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        self.token_dir = os.path.dirname(__file__)


    def _get_google_service(self, api_name: str, api_version: str, scopes: List[str], user_id: str):
        """Authenticates with Google APIs and returns a service client."""
        creds = None
        token_file = os.path.join(self.token_dir, f'token_{api_name}_{user_id}.json')


        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.creds_path):
                    raise FileNotFoundError(f"Google credentials not found at {self.creds_path}")
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, scopes)
                creds = flow.run_local_server(port=0)

            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        return build(api_name, api_version, credentials=creds)

    def _read_emails(self, gmail_service) -> List[Dict]:
        """Fetches and processes unread emails."""
        results = gmail_service.users().messages().list(
            userId='me', labelIds=['INBOX', 'UNREAD'], q='is:unread', maxResults=5
        ).execute()
        messages = results.get('messages', [])
        emails = []

        for msg_info in messages:
            msg = gmail_service.users().messages().get(userId='me', id=msg_info['id']).execute()
            payload = msg.get('payload', {})
            body_data = ""
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        body_data = part['body'].get('data', '')
                        break
            elif 'body' in payload:
                body_data = payload['body'].get('data', '')

            if body_data:
                decoded_content = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                clean_text = BeautifulSoup(decoded_content, 'html.parser').get_text(separator='\n', strip=True)
                emails.append({'content': clean_text})
        print(f"📧 Found {len(emails)} unread emails to process.")
        return emails

    def _extract_events_with_ai(self, emails: List[Dict]) -> List[Dict]:
        """Uses OpenAI to extract event details from email content."""
        if not emails:
            return []
            
        email_summaries = "\n---\n".join([e['content'][:1500] for e in emails])
        prompt = f"""
        From the following emails, extract any events. Return a JSON object with an "events" key, 
        which is an array of objects. Each object must have 'summary', 'start_time', and 'end_time' 
        in ISO 8601 format (YYYY-MM-DDTHH:MM:SS). If no events are found, return an empty array.
        Emails:
        {email_summaries}
        """
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        schedule_data = json.loads(response.choices[0].message.content)
        extracted_events = schedule_data.get('events', [])
        print(f"🤖 AI extracted {len(extracted_events)} potential events.")
        return extracted_events

    def _add_events_to_calendar(self, calendar_service, events: List[Dict]):
        """Adds a list of extracted events to the user's primary calendar."""
        created_links = []
        for event in events:
            event_body = {
                'summary': event.get('summary'),
                'start': {'dateTime': event.get('start_time'), 'timeZone': 'UTC'},
                'end': {'dateTime': event.get('end_time'), 'timeZone': 'UTC'},
                'description': f"Created by {self.agent_id} with user consent."
            }
            try:
                created_event = calendar_service.events().insert(calendarId='primary', body=event_body).execute()
                created_links.append(created_event.get('htmlLink'))
                print(f"✅ Successfully created event: '{event.get('summary')}'")
            except Exception as e:
                print(f"❌ Failed to create event '{event.get('summary')}': {e}")
        return created_links

    def handle(self, user_id: str, email_token_str: str, calendar_token_str: str):
        """Main entry point for the agent, gated by HushhMCP consent checks."""
        is_valid_email, reason_email, _ = validate_token(email_token_str, expected_scope=ConsentScope.VAULT_READ_EMAIL)
        if not is_valid_email:
            raise PermissionError(f"Email Access Denied: {reason_email}")
        print("✅ Consent validated for email access.") 


        gmail_service = self._get_google_service('gmail', 'v1', ['https://www.googleapis.com/auth/gmail.readonly'], user_id)
        emails = self._read_emails(gmail_service)
        if not emails:
            return {"status": "complete", "message": "No new emails to process."}
    
        events = self._extract_events_with_ai(emails)
        if not events:
            return {"status": "complete", "message": "No events found in emails."}

        is_valid_cal, reason_cal, _ = validate_token(calendar_token_str, expected_scope=ConsentScope.VAULT_WRITE_CALENDAR)
        if not is_valid_cal:
            raise PermissionError(f"Calendar Access Denied: {reason_cal}")
        print("✅ Consent validated for calendar creation.")
        
        calendar_service = self._get_google_service('calendar', 'v3', ['https://www.googleapis.com/auth/calendar.events'], user_id)
        created_event_links = self._add_events_to_calendar(calendar_service, events)

        return {
            "status": "complete",
            "events_created": len(created_event_links),
            "links": created_event_links
        }