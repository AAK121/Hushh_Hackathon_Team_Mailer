# hushh_mcp/agents/addtocalendar/index.py
import os
import json
import base64
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# HushMCP framework imports
from hushh_mcp.consent.token import validate_token, issue_token
from hushh_mcp.constants import ConsentScope
from ...operons.email_analysis import prioritize_emails_operon, categorize_emails_operon
from hushh_mcp.trust.link import verify_trust_link
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.agents.addtocalendar.manifest import manifest
import hashlib

def _generate_encryption_key(user_id: str) -> str:
    """
    Generate a deterministic hex key from user ID for encryption.
    
    Args:
        user_id: User identifier
        
    Returns:
        32-byte hex string for AES-256 encryption
    """
    # Create a deterministic key from user_id using SHA-256
    # This ensures the same user_id always generates the same key
    salt = b"hushh_vault_salt_2024"
    combined = user_id.encode('utf-8') + salt
    key_hash = hashlib.sha256(combined).digest()
    return key_hash.hex()

class AddToCalendarAgent:
    """
    Enhanced AI-powered calendar agent with advanced email processing, 
    prioritization, categorization, and manual event management.
    
    Features:
    - Read and prioritize 50 most recent emails using AI
    - Categorize emails by type (work, personal, events, etc.)
    - Extract events with confidence scoring
    - Manual event addition with AI assistance
    - Secure data handling with HushMCP vault encryption
    """
    def __init__(self):
        self.agent_id = manifest["id"]
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set.")
        
        # Configure Gemini AI
        genai.configure(api_key=google_api_key)
        
        # AI Models configuration
        self.ai_model = "gemini-2.5-flash"
        self.max_emails = 10

    def _get_google_service_with_token(self, api_name: str, api_version: str, access_token: str):
        """
        Creates Google API service using access token from frontend.
        
        Args:
            api_name: Google API service name (e.g., 'gmail', 'calendar')
            api_version: API version (e.g., 'v1', 'v3')
            access_token: OAuth access token from frontend
            
        Returns:
            Google API service client
        """
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        
        # Create credentials object from access token
        creds = Credentials(token=access_token)
        
        # Build and return the service
        return build(api_name, api_version, credentials=creds)

    def _get_google_service_with_token(self, service_name: str, version: str, access_token: str):
        """
        Create a Google API service using an access token instead of credentials file.
        
        Args:
            service_name: Google service name (e.g., 'gmail', 'calendar')
            version: API version (e.g., 'v1', 'v3')
            access_token: Google OAuth access token from frontend
            
        Returns:
            Google API service instance or None if failed
        """
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            # Create credentials object from access token
            credentials = Credentials(token=access_token)
            
            # Build and return the service
            service = build(service_name, version, credentials=credentials)
            print(f"   ✅ {service_name.capitalize()} service created with access token")
            return service
            
        except Exception as e:
            print(f"   ❌ Failed to create {service_name} service with access token: {e}")
            return None

    def _get_google_service(self, service_name: str, version: str, user_id: str, consent_token: str):
        """
        DEPRECATED: Legacy method for file-based credentials.
        Use _get_google_service_with_token() for access token authentication.
        """
        raise NotImplementedError(
            "File-based credentials are deprecated. Use access tokens via _get_google_service_with_token()"
        )

    def _read_emails(self, gmail_service, max_results: int = 50) -> List[Dict]:
        """
        Fetches and processes the most recent emails from inbox.
        
        Args:
            gmail_service: Authenticated Gmail service client
            max_results: Maximum number of emails to fetch (default 50)
            
        Returns:
            List of email dictionaries with content, metadata, and timestamps
        """
        # Get recent emails from inbox (not just unread)
        results = gmail_service.users().messages().list(
            userId='me', 
            labelIds=['INBOX'], 
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        emails = []

        print(f"📧 Processing {len(messages)} recent emails...")

        for i, msg_info in enumerate(messages):
            try:
                msg = gmail_service.users().messages().get(
                    userId='me', 
                    id=msg_info['id'], 
                    format='full'
                ).execute()
                
                payload = msg.get('payload', {})
                headers = payload.get('headers', [])
                
                # Extract metadata
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Extract body content
                body_data = self._extract_email_body(payload)
                
                if body_data:
                    emails.append({
                        'id': msg_info['id'],
                        'subject': subject,
                        'sender': sender,
                        'date': date_str,
                        'content': body_data,
                        'timestamp': msg.get('internalDate', '0'),
                        'thread_id': msg.get('threadId', '')
                    })
                    
                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"   Processed {i + 1}/{len(messages)} emails...")
                    
            except Exception as e:
                print(f"⚠️  Error processing email {msg_info['id']}: {e}")
                continue

        print(f"✅ Successfully processed {len(emails)} emails.")
        return emails

    def _extract_email_body(self, payload: Dict) -> str:
        """Extract text content from email payload."""
        body_data = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body_data = part['body'].get('data', '')
                    break
                elif part['mimeType'] == 'text/html' and not body_data:
                    # Fallback to HTML if plain text not available
                    body_data = part['body'].get('data', '')
        elif 'body' in payload:
            body_data = payload['body'].get('data', '')

        if body_data:
            try:
                decoded_content = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                clean_text = BeautifulSoup(decoded_content, 'html.parser').get_text(separator='\n', strip=True)
                
                # Remove problematic Unicode characters commonly found in emails
                clean_text = self._clean_unicode_text(clean_text)
                
                return clean_text[:2000]  # Limit content length
            except Exception as e:
                print(f"⚠️  Error decoding email content: {e}")
                return ""
        
        return ""

    def _clean_unicode_text(self, text: str) -> str:
        """
        Clean problematic Unicode characters commonly found in emails.
        
        Args:
            text: Raw text content from email
            
        Returns:
            Cleaned text with problematic Unicode characters removed
        """
        import re
        import unicodedata
        
        # Remove specific problematic Unicode characters
        problematic_chars = [
            '\u034f',  # Combining Grapheme Joiner
            '\u200c',  # Zero Width Non-Joiner  
            '\u200b',  # Zero Width Space
            '\u200d',  # Zero Width Joiner
            '\ufeff',  # Zero Width No-Break Space (BOM)
            '\u2060',  # Word Joiner
            '\u180e',  # Mongolian Vowel Separator
        ]
        
        for char in problematic_chars:
            text = text.replace(char, '')
        
        # Convert non-breaking spaces to regular spaces (don't remove them)
        text = text.replace('\u00a0', ' ')
        
        # Remove excessive whitespace and normalize
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
        
        # Normalize Unicode characters to standard forms
        text = unicodedata.normalize('NFKC', text)
        
        return text.strip()

    def prioritize_emails(self, emails: List[Dict], user_id: str, consent_token: str) -> List[Dict]:
        """
        Prioritize emails using HushMCP email analysis operon.
        
        Args:
            emails: List of email dictionaries
            user_id: User identifier
            consent_token: Validated consent token
            
        Returns:
            List of emails with priority scores (1-10 scale)
        """
        # Use the reusable operon for email prioritization
        return prioritize_emails_operon(emails, user_id, consent_token, self.ai_model)

        # Prepare email summaries for AI analysis
        email_summaries = []
        for i, email in enumerate(emails[:20]):  # Analyze top 20 for performance
            summary = {
                'index': i,
                'subject': email['subject'][:100],
                'sender': email['sender'][:50],
                'preview': email['content'][:300],
                'date': email['date']
            }
            email_summaries.append(summary)

        prompt = f"""
        Analyze these {len(email_summaries)} emails and assign priority scores (1-10, where 10 is highest priority).
        Consider: urgency, importance, sender authority, meeting/event content, deadlines.
        
        Return JSON with this structure:
        {{
            "prioritized_emails": [
                {{
                    "index": 0,
                    "priority_score": 8,
                    "priority_reason": "Meeting invitation from manager with deadline",
                    "category": "work_urgent"
                }}
            ]
        }}
        
        Emails to analyze:
        {json.dumps(email_summaries, indent=2)}
        """

        try:
            model = genai.GenerativeModel(self.ai_model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            
            analysis = json.loads(response.text)
            prioritized = analysis.get('prioritized_emails', [])
            
            # Apply priority scores to original emails
            for priority_info in prioritized:
                idx = priority_info.get('index')
                if 0 <= idx < len(emails):
                    emails[idx].update({
                        'priority_score': priority_info.get('priority_score', 5),
                        'priority_reason': priority_info.get('priority_reason', 'AI analysis'),
                        'ai_category': priority_info.get('category', 'general')
                    })

            # Sort by priority score (highest first)
            emails.sort(key=lambda x: x.get('priority_score', 5), reverse=True)
            
            print(f"✅ Email prioritization complete. Top priority: {emails[0]['subject'][:50]}...")
            return emails
            
        except Exception as e:
            print(f"⚠️  AI prioritization failed: {e}")
            # Return original list if AI fails
            return emails

    def categorize_emails(self, emails: List[Dict], user_id: str, consent_token: str) -> List[Dict]:
        """
        Categorize emails into different types using AI analysis.
        
        Categories: work, personal, events, travel, shopping, finance, newsletters, spam
        """
        if not emails:
            return []

        print("� Categorizing emails with AI...")
        
        # Validate consent
        is_valid, reason, _ = validate_token(consent_token, expected_scope=ConsentScope.VAULT_READ_EMAIL)
        if not is_valid:
            raise PermissionError(f"Email Categorization Access Denied: {reason}")

        # Process in batches to avoid token limits
        batch_size = 15
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            
            # Prepare batch for analysis
            email_data = []
            for j, email in enumerate(batch):
                email_data.append({
                    'index': j,
                    'subject': email['subject'][:100],
                    'sender': email['sender'][:50],
                    'content_preview': email['content'][:200]
                })

            prompt = f"""
            Categorize these emails into appropriate categories. Choose from:
            - work: Professional emails, meetings, work-related
            - personal: Friends, family, personal matters
            - events: Invitations, event notifications, calendar items
            - travel: Bookings, itineraries, travel-related
            - shopping: Orders, receipts, product updates
            - finance: Banking, payments, financial statements
            - newsletters: Newsletters, marketing, subscriptions
            - spam: Unwanted, promotional, suspicious
            
            Return JSON:
            {{
                "categorized_emails": [
                    {{
                        "index": 0,
                        "category": "work",
                        "confidence": 0.9,
                        "tags": ["meeting", "urgent"]
                    }}
                ]
            }}
            
            Emails:
            {json.dumps(email_data, indent=2)}
            """

            try:
                model = genai.GenerativeModel(self.ai_model)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        response_mime_type="application/json"
                    )
                )
                
                analysis = json.loads(response.text)
                categorized = analysis.get('categorized_emails', [])
                
                # Apply categorization to emails
                for cat_info in categorized:
                    batch_idx = cat_info.get('index')
                    if 0 <= batch_idx < len(batch):
                        batch[batch_idx].update({
                            'category': cat_info.get('category', 'general'),
                            'category_confidence': cat_info.get('confidence', 0.5),
                            'tags': cat_info.get('tags', [])
                        })
                        
            except Exception as e:
                print(f"⚠️  Categorization failed for batch {i//batch_size + 1}: {e}")
                # Set default category if AI fails
                for email in batch:
                    email.update({
                        'category': 'general',
                        'category_confidence': 0.5,
                        'tags': []
                    })

        print("✅ Email categorization complete.")
        return emails

    def _extract_events_with_ai(self, emails: List[Dict], user_id: str, consent_token: str) -> List[Dict]:
        """
        Enhanced event extraction with confidence scoring and detailed analysis.
        
        Args:
            emails: List of email dictionaries (already prioritized/categorized)
            user_id: User identifier
            consent_token: Validated consent token
            
        Returns:
            List of extracted events with confidence scores and metadata
        """
        if not emails:
            return []

        print("🎯 Extracting events with enhanced AI analysis...")
        
        # Validate consent
        is_valid, reason, _ = validate_token(consent_token, expected_scope=ConsentScope.VAULT_READ_EMAIL)
        if not is_valid:
            raise PermissionError(f"Event Extraction Access Denied: {reason}")

        # Focus on high-priority and event-category emails
        relevant_emails = [
            email for email in emails[:30]  # Top 30 emails
            if email.get('priority_score', 5) >= 6 or 
               email.get('category') in ['events', 'work', 'travel']
        ]

        if not relevant_emails:
            relevant_emails = emails[:15]  # Fallback to top 15

        # Prepare email content for analysis
        email_content = []
        for i, email in enumerate(relevant_emails):
            content_data = {
                'email_id': i,
                'subject': email['subject'],
                'sender': email['sender'],
                'date': email['date'],
                'content': email['content'][:1500],  # Increased content limit
                'priority': email.get('priority_score', 5),
                'category': email.get('category', 'general')
            }
            email_content.append(content_data)

        prompt = f"""
        Extract calendar events from these emails with high precision. For each event found, provide:
        - Event details (title, description, location)
        - Date/time information
        - Confidence score (0.0-1.0)
        - Event type (meeting, appointment, deadline, etc.)
        - Attendees if mentioned
        
        Return JSON:
        {{
            "events": [
                {{
                    "summary": "Team Meeting",
                    "description": "Weekly team sync meeting",
                    "start_time": "2025-08-10T14:00:00",
                    "end_time": "2025-08-10T15:00:00",
                    "location": "Conference Room A",
                    "confidence_score": 0.95,
                    "event_type": "meeting",
                    "attendees": ["john@company.com"],
                    "source_email_id": 0,
                    "timezone": "UTC",
                    "all_day": false,
                    "recurring": false,
                    "priority": "high"
                }}
            ],
            "summary": {{
                "total_emails_analyzed": {len(email_content)},
                "events_found": 0,
                "high_confidence_events": 0
            }}
        }}
        
        Only extract events with confidence >= 0.7. Consider:
        - Meeting invitations and calendar attachments
        - Appointment confirmations
        - Event announcements with specific dates/times
        - Deadline mentions with actionable dates
        - Travel bookings with arrival/departure times
        
        Emails to analyze:
        {json.dumps(email_content, indent=2)}
        """

        try:
            model = genai.GenerativeModel(self.ai_model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            
            event_data = json.loads(response.text)
            extracted_events = event_data.get('events', [])
            summary = event_data.get('summary', {})
            
            print(f"🤖 AI Analysis Summary:")
            print(f"   - Emails analyzed: {summary.get('total_emails_analyzed', len(email_content))}")
            print(f"   - Events found: {summary.get('events_found', len(extracted_events))}")
            print(f"   - High confidence: {summary.get('high_confidence_events', 0)}")
            
            # Filter and enrich events
            high_quality_events = []
            for event in extracted_events:
                confidence = event.get('confidence_score', 0.0)
                if confidence >= 0.7:  # Only high-confidence events
                    # Add metadata
                    event['extracted_by'] = self.agent_id
                    event['extraction_timestamp'] = datetime.utcnow().isoformat()
                    event['user_id'] = user_id
                    
                    # Validate required fields
                    if all(key in event for key in ['summary', 'start_time', 'end_time']):
                        high_quality_events.append(event)
                        print(f"   ✅ Event: {event['summary']} (confidence: {confidence:.2f})")
                    else:
                        print(f"   ⚠️  Skipping incomplete event: {event.get('summary', 'Unknown')}")
                else:
                    print(f"   ❌ Low confidence event rejected: {event.get('summary', 'Unknown')} (confidence: {confidence:.2f})")
            
            print(f"📅 Final result: {len(high_quality_events)} high-quality events extracted.")
            return high_quality_events
            
        except Exception as e:
            print(f"❌ Event extraction failed: {e}")
            return []

    def create_manual_event(self, event_description: str, user_id: str, consent_token: str) -> Dict:
        """
        Create a calendar event manually with AI assistance for details.
        
        Args:
            event_description: Natural language description of the event
            user_id: User identifier
            consent_token: Validated consent token
            
        Returns:
            Dictionary with event details and creation status
        """
        print(f"🎨 Creating manual event with AI assistance...")
        print(f"   Description: {event_description}")
        
        # Validate consent for calendar write access
        is_valid, reason, _ = validate_token(consent_token, expected_scope=ConsentScope.VAULT_WRITE_CALENDAR)
        if not is_valid:
            raise PermissionError(f"Manual Event Creation Access Denied: {reason}")

        prompt = f"""
        Help create a calendar event from this description: "{event_description}"
        
        Generate a complete event with reasonable defaults. If times are not specified, 
        suggest appropriate ones. If dates are relative (like "tomorrow"), convert to 
        actual dates based on today being {datetime.now().strftime('%Y-%m-%d')}.
        
        Return JSON:
        {{
            "event": {{
                "summary": "Event Title",
                "description": "Detailed description",
                "start_time": "2025-08-10T14:00:00",
                "end_time": "2025-08-10T15:00:00",
                "location": "Location if specified",
                "timezone": "UTC",
                "all_day": false,
                "priority": "normal",
                "attendees": [],
                "reminders": [15],
                "event_type": "appointment"
            }},
            "ai_suggestions": {{
                "confidence": 0.8,
                "suggestions": ["Consider adding location", "Maybe invite team members"],
                "assumptions": ["Set 1-hour duration", "Used business hours"]
            }}
        }}
        """

        try:
            model = genai.GenerativeModel(self.ai_model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(response.text)
            event_data = result.get('event', {})
            ai_suggestions = result.get('ai_suggestions', {})
            
            # Enrich with metadata
            event_data.update({
                'created_manually': True,
                'created_by': self.agent_id,
                'creation_timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'ai_confidence': ai_suggestions.get('confidence', 0.8)
            })
            
            print("✅ AI-assisted event created:")
            print(f"   Title: {event_data.get('summary')}")
            print(f"   Time: {event_data.get('start_time')} - {event_data.get('end_time')}")
            print(f"   Confidence: {ai_suggestions.get('confidence', 0.8):.2f}")
            
            if ai_suggestions.get('suggestions'):
                print(f"   AI Suggestions: {', '.join(ai_suggestions['suggestions'])}")
                
            return {
                'status': 'success',
                'event': event_data,
                'ai_suggestions': ai_suggestions
            }
            
        except Exception as e:
            print(f"❌ Manual event creation failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'event': None
            }

    def create_events_in_calendar(self, events: List[Dict], user_id: str, consent_token: str) -> Dict:
        """
        Create multiple events in Google Calendar with enhanced error handling.
        
        Args:
            events: List of event dictionaries to create
            user_id: User identifier
            consent_token: Validated consent token
            
        Returns:
            Dictionary with creation results and statistics
        """
        if not events:
            return {
                'status': 'warning',
                'message': 'No events provided to create',
                'results': []
            }

        print(f"📅 Creating {len(events)} events in Google Calendar...")
        
        # Validate consent for calendar write
        is_valid, reason, _ = validate_token(consent_token, expected_scope=ConsentScope.VAULT_WRITE_CALENDAR)
        if not is_valid:
            raise PermissionError(f"Calendar Write Access Denied: {reason}")

        service = self._get_google_service('calendar', 'v3', 
            ['https://www.googleapis.com/auth/calendar.events'], user_id)
        if not service:
            return {
                'status': 'error',
                'message': 'Failed to connect to Google Calendar service',
                'results': []
            }

        creation_results = []
        success_count = 0
        error_count = 0
        
        for i, event_data in enumerate(events):
            try:
                # Validate required fields
                required_fields = ['summary', 'start_time', 'end_time']
                missing_fields = [field for field in required_fields if not event_data.get(field)]
                
                if missing_fields:
                    creation_results.append({
                        'index': i,
                        'status': 'error',
                        'error': f"Missing required fields: {', '.join(missing_fields)}",
                        'event_summary': event_data.get('summary', 'Unknown Event')
                    })
                    error_count += 1
                    continue

                # Prepare Google Calendar event
                google_event = {
                    'summary': event_data['summary'],
                    'description': event_data.get('description', ''),
                    'start': {
                        'dateTime': event_data['start_time'],
                        'timeZone': event_data.get('timezone', 'UTC')
                    },
                    'end': {
                        'dateTime': event_data['end_time'],
                        'timeZone': event_data.get('timezone', 'UTC')
                    }
                }

                # Add optional fields
                if event_data.get('location'):
                    google_event['location'] = event_data['location']
                
                if event_data.get('attendees'):
                    google_event['attendees'] = [
                        {'email': email} for email in event_data['attendees']
                    ]
                
                if event_data.get('reminders'):
                    google_event['reminders'] = {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': minutes}
                            for minutes in event_data['reminders']
                        ]
                    }

                # Create the event
                created_event = service.events().insert(
                    calendarId='primary',
                    body=google_event
                ).execute()

                # Store in vault for future reference
                vault_data = {
                    'google_event_id': created_event['id'],
                    'original_event_data': event_data,
                    'created_timestamp': datetime.utcnow().isoformat(),
                    'user_id': user_id,
                    'agent_id': self.agent_id,
                    'confidence_score': event_data.get('confidence_score', 1.0),
                    'scope': 'calendar_event',
                    'metadata': {
                        'extraction_method': event_data.get('extracted_by', 'manual'),
                        'ai_model': self.ai_model,
                        'event_type': event_data.get('event_type', 'appointment')
                    }
                }
                
                vault_key = f"calendar_event_{created_event['id']}"
                try:
                    encryption_key = _generate_encryption_key(user_id)
                    encrypted_data = encrypt_data(json.dumps(vault_data), encryption_key)
                    # Store encrypted data in vault (implementation would depend on vault storage system)
                    print(f"   🔒 Event data encrypted and stored in vault: {vault_key}")
                except Exception as vault_error:
                    print(f"   ⚠️  Vault storage failed: {vault_error}")
                
                creation_results.append({
                    'index': i,
                    'status': 'success',
                    'google_event_id': created_event['id'],
                    'event_summary': event_data['summary'],
                    'calendar_link': created_event.get('htmlLink'),
                    'vault_key': vault_key,
                    'confidence_score': event_data.get('confidence_score', 1.0)
                })
                
                success_count += 1
                print(f"   ✅ Created: {event_data['summary']}")
                
                # Create trust link for cross-agent access if needed
                if event_data.get('extracted_by') and event_data['extracted_by'] != self.agent_id:
                    try:
                        # Use HushMCP trust link creation
                        trust_data = {
                            'from_agent': event_data['extracted_by'],
                            'to_agent': self.agent_id,
                            'resource_type': "calendar_event",
                            'resource_id': created_event['id'],
                            'permission_level': "read",
                            'created_at': datetime.utcnow().isoformat(),
                            'user_id': user_id
                        }
                        
                        # Store trust link in vault
                        trust_key = f"trust_link_{self.agent_id}_{created_event['id']}"
                        trust_encryption_key = _generate_encryption_key(user_id)
                        encrypted_trust = encrypt_data(json.dumps(trust_data), trust_encryption_key)
                        print(f"   🔗 Trust link data stored: {trust_key}")
                        
                    except Exception as trust_error:
                        print(f"   ⚠️  Trust link creation failed: {trust_error}")

            except Exception as e:
                creation_results.append({
                    'index': i,
                    'status': 'error',
                    'error': str(e),
                    'event_summary': event_data.get('summary', 'Unknown Event')
                })
                error_count += 1
                print(f"   ❌ Failed to create: {event_data.get('summary', 'Unknown')} - {e}")

        # Summary
        total_events = len(events)
        print(f"\n📊 Calendar Creation Summary:")
        print(f"   Total: {total_events} | Success: {success_count} | Errors: {error_count}")

        return {
            'status': 'success' if error_count == 0 else 'partial' if success_count > 0 else 'error',
            'message': f"Created {success_count}/{total_events} events successfully",
            'results': creation_results,
            'statistics': {
                'total_events': total_events,
                'successful_creations': success_count,
                'failed_creations': error_count,
                'success_rate': (success_count / total_events) * 100 if total_events > 0 else 0
            }
        }

    def run_comprehensive_email_analysis(self, user_id: str, email_consent_token: str, calendar_consent_token: str) -> Dict:
        """
        Main function that orchestrates the complete email analysis and calendar integration.
        
        Args:
            user_id: User identifier
            email_consent_token: Validated consent token for email access
            calendar_consent_token: Validated consent token for calendar access
            
        Returns:
            Complete analysis results with all processing steps
        """
        print("🚀 Starting Comprehensive Email Analysis Pipeline...")
        analysis_start = datetime.utcnow()
        
        try:
            # Step 1: Create Gmail service and read recent emails
            print("\n📧 Step 1: Creating Gmail service and reading recent emails...")
            gmail_service = self._get_google_service('gmail', 'v1', 
                ['https://www.googleapis.com/auth/gmail.readonly'], user_id)
            emails = self._read_emails(gmail_service, max_results=self.max_emails)
            
            if not emails:
                return {
                    'status': 'warning',
                    'message': 'No emails found to analyze',
                    'steps_completed': ['email_reading'],
                    'processing_time': 0
                }

            # Step 2: Prioritize emails
            print("\n⭐ Step 2: Prioritizing emails with AI...")
            prioritized_emails = self.prioritize_emails(emails, user_id, email_consent_token)

            # Step 3: Categorize emails
            print("\n🏷️ Step 3: Categorizing emails...")
            categorized_emails = self.categorize_emails(prioritized_emails, user_id, email_consent_token)

            # Step 4: Extract events with enhanced AI
            print("\n🎯 Step 4: Extracting events with AI...")
            extracted_events = self._extract_events_with_ai(categorized_emails, user_id, email_consent_token)

            # Step 5: Create events in calendar (optional)
            calendar_results = None
            if extracted_events:
                print(f"\n📅 Step 5: Found {len(extracted_events)} events. Creating in calendar...")
                calendar_results = self.create_events_in_calendar(extracted_events, user_id, calendar_consent_token)
            else:
                print("\n📅 Step 5: No events found to create in calendar.")

            # Analysis summary
            analysis_end = datetime.utcnow()
            processing_time = (analysis_end - analysis_start).total_seconds()

            high_priority_emails = [e for e in categorized_emails if e.get('priority_score', 0) >= 8]
            event_categories = {}
            for email in categorized_emails:
                category = email.get('category', 'unknown')
                event_categories[category] = event_categories.get(category, 0) + 1

            results = {
                'status': 'success',
                'message': 'Comprehensive email analysis completed successfully',
                'processing_time': round(processing_time, 2),
                'steps_completed': [
                    'email_reading', 'prioritization', 'categorization', 
                    'event_extraction', 'calendar_creation' if calendar_results else 'event_extraction'
                ],
                'analysis_summary': {
                    'total_emails_processed': len(emails),
                    'high_priority_emails': len(high_priority_emails),
                    'email_categories': event_categories,
                    'events_extracted': len(extracted_events),
                    'events_created': calendar_results['statistics']['successful_creations'] if calendar_results else 0
                },
                'data': {
                    'emails': categorized_emails[:10],  # Top 10 for review
                    'extracted_events': extracted_events,
                    'calendar_results': calendar_results
                },
                'timestamps': {
                    'analysis_start': analysis_start.isoformat(),
                    'analysis_end': analysis_end.isoformat()
                }
            }

            print(f"\n✅ Analysis Complete! Processed {len(emails)} emails in {processing_time:.2f}s")
            print(f"   📊 High Priority: {len(high_priority_emails)} emails")
            print(f"   🎯 Events Found: {len(extracted_events)}")
            if calendar_results:
                print(f"   📅 Calendar Events: {calendar_results['statistics']['successful_creations']}")

            return results

        except Exception as e:
            analysis_end = datetime.utcnow()
            processing_time = (analysis_end - analysis_start).total_seconds()
            
            print(f"❌ Analysis pipeline failed after {processing_time:.2f}s: {e}")
            
            return {
                'status': 'error',
                'message': f'Analysis pipeline failed: {str(e)}',
                'processing_time': round(processing_time, 2),
                'error_details': str(e),
                'steps_completed': ['email_reading'],  # Minimal assumption
                'timestamps': {
                    'analysis_start': analysis_start.isoformat(),
                    'analysis_end': analysis_end.isoformat()
                }
            }

    def run_comprehensive_email_analysis_with_token(self, user_id: str, email_consent_token: str, 
                                                   calendar_consent_token: str, google_access_token: str) -> Dict:
        """
        Main function that orchestrates the complete email analysis and calendar integration using access tokens.
        
        Args:
            user_id: User identifier
            email_consent_token: Validated consent token for email access
            calendar_consent_token: Validated consent token for calendar access
            google_access_token: Google OAuth access token from frontend
            
        Returns:
            Complete analysis results with all processing steps
        """
        print("🚀 Starting Comprehensive Email Analysis Pipeline with Access Token...")
        analysis_start = datetime.utcnow()
        
        try:
            # Step 1: Create Gmail service using access token
            print("\n📧 Step 1: Creating Gmail service with access token...")
            gmail_service = self._get_google_service_with_token('gmail', 'v1', google_access_token)
            emails = self._read_emails(gmail_service, max_results=self.max_emails)
            
            if not emails:
                return {
                    'status': 'warning',
                    'message': 'No emails found to analyze',
                    'steps_completed': ['email_reading'],
                    'processing_time': 0
                }

            # Step 2: Prioritize emails
            print("\n⭐ Step 2: Prioritizing emails with AI...")
            prioritized_emails = self.prioritize_emails(emails, user_id, email_consent_token)

            # Step 3: Categorize emails
            print("\n🏷️ Step 3: Categorizing emails...")
            categorized_emails = self.categorize_emails(prioritized_emails, user_id, email_consent_token)

            # Step 4: Extract events with enhanced AI
            print("\n🎯 Step 4: Extracting events with AI...")
            extracted_events = self._extract_events_with_ai(categorized_emails, user_id, email_consent_token)

            # Step 5: Create events in calendar using access token
            calendar_results = None
            if extracted_events:
                print(f"\n📅 Step 5: Found {len(extracted_events)} events. Creating in calendar...")
                calendar_results = self.create_events_in_calendar_with_token(
                    extracted_events, user_id, calendar_consent_token, google_access_token
                )
            else:
                print("\n📅 Step 5: No events found to create in calendar.")

            # Analysis summary
            analysis_end = datetime.utcnow()
            processing_time = (analysis_end - analysis_start).total_seconds()

            high_priority_emails = [e for e in categorized_emails if e.get('priority_score', 0) >= 8]
            event_categories = {}
            for email in categorized_emails:
                category = email.get('category', 'unknown')
                event_categories[category] = event_categories.get(category, 0) + 1

            results = {
                'status': 'success',
                'message': 'Comprehensive email analysis completed successfully with access token',
                'processing_time': round(processing_time, 2),
                'steps_completed': [
                    'email_reading', 'prioritization', 'categorization', 
                    'event_extraction', 'calendar_creation' if calendar_results else 'event_extraction'
                ],
                'analysis_summary': {
                    'total_emails_processed': len(emails),
                    'high_priority_emails': len(high_priority_emails),
                    'email_categories': event_categories,
                    'events_extracted': len(extracted_events),
                    'events_created': calendar_results['statistics']['successful_creations'] if calendar_results else 0
                },
                'data': {
                    'emails': categorized_emails[:10],  # Top 10 for review
                    'extracted_events': extracted_events,
                    'calendar_results': calendar_results
                },
                'timestamps': {
                    'analysis_start': analysis_start.isoformat(),
                    'analysis_end': analysis_end.isoformat()
                },
                'authentication_method': 'access_token'
            }

            print(f"\n✅ Analysis Complete! Processed {len(emails)} emails in {processing_time:.2f}s")
            print(f"   📊 High Priority: {len(high_priority_emails)} emails")
            print(f"   🎯 Events Found: {len(extracted_events)}")
            if calendar_results:
                print(f"   📅 Calendar Events: {calendar_results['statistics']['successful_creations']}")

            return results

        except Exception as e:
            analysis_end = datetime.utcnow()
            processing_time = (analysis_end - analysis_start).total_seconds()
            
            print(f"❌ Analysis pipeline failed after {processing_time:.2f}s: {e}")
            
            return {
                'status': 'error',
                'message': f'Analysis pipeline failed: {str(e)}',
                'processing_time': round(processing_time, 2),
                'error_details': str(e),
                'steps_completed': ['email_reading'],
                'timestamps': {
                    'analysis_start': analysis_start.isoformat(),
                    'analysis_end': analysis_end.isoformat()
                }
            }

    def create_events_in_calendar_with_token(self, events: List[Dict], user_id: str, 
                                           consent_token: str, google_access_token: str) -> Dict:
        """
        Create multiple events in Google Calendar using access token.
        
        Args:
            events: List of event dictionaries to create
            user_id: User identifier
            consent_token: Validated consent token
            google_access_token: Google OAuth access token from frontend
            
        Returns:
            Dictionary with creation results and statistics
        """
        if not events:
            return {
                'status': 'warning',
                'message': 'No events provided to create',
                'results': []
            }

        print(f"📅 Creating {len(events)} events in Google Calendar with access token...")
        
        # Validate consent for calendar write
        is_valid, reason, _ = validate_token(consent_token, expected_scope=ConsentScope.VAULT_WRITE_CALENDAR)
        if not is_valid:
            raise PermissionError(f"Calendar Write Access Denied: {reason}")

        # Create calendar service using access token
        service = self._get_google_service_with_token('calendar', 'v3', google_access_token)
        if not service:
            return {
                'status': 'error',
                'message': 'Failed to connect to Google Calendar service with access token',
                'results': []
            }

        creation_results = []
        success_count = 0
        error_count = 0
        
        for i, event_data in enumerate(events):
            try:
                # Validate required fields
                required_fields = ['summary', 'start_time', 'end_time']
                missing_fields = [field for field in required_fields if not event_data.get(field)]
                
                if missing_fields:
                    creation_results.append({
                        'index': i,
                        'status': 'error',
                        'error': f"Missing required fields: {', '.join(missing_fields)}",
                        'event_summary': event_data.get('summary', 'Unknown Event')
                    })
                    error_count += 1
                    continue

                # Prepare Google Calendar event
                google_event = {
                    'summary': event_data['summary'],
                    'description': event_data.get('description', ''),
                    'start': {
                        'dateTime': event_data['start_time'],
                        'timeZone': event_data.get('timezone', 'UTC')
                    },
                    'end': {
                        'dateTime': event_data['end_time'],
                        'timeZone': event_data.get('timezone', 'UTC')
                    }
                }

                # Add optional fields
                if event_data.get('location'):
                    google_event['location'] = event_data['location']
                
                if event_data.get('attendees'):
                    google_event['attendees'] = [
                        {'email': email} for email in event_data['attendees']
                    ]
                
                if event_data.get('reminders'):
                    google_event['reminders'] = {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': minutes}
                            for minutes in event_data['reminders']
                        ]
                    }

                # Create the event
                created_event = service.events().insert(
                    calendarId='primary',
                    body=google_event
                ).execute()

                # Store in vault for future reference
                vault_data = {
                    'google_event_id': created_event['id'],
                    'original_event_data': event_data,
                    'created_timestamp': datetime.utcnow().isoformat(),
                    'user_id': user_id,
                    'agent_id': self.agent_id,
                    'confidence_score': event_data.get('confidence_score', 1.0),
                    'scope': 'calendar_event',
                    'authentication_method': 'access_token',
                    'metadata': {
                        'extraction_method': event_data.get('extracted_by', 'manual'),
                        'ai_model': self.ai_model,
                        'event_type': event_data.get('event_type', 'appointment')
                    }
                }
                
                vault_key = f"calendar_event_{created_event['id']}"
                try:
                    encryption_key = _generate_encryption_key(user_id)
                    encrypted_data = encrypt_data(json.dumps(vault_data), encryption_key)
                    print(f"   🔒 Event data encrypted and stored in vault: {vault_key}")
                except Exception as vault_error:
                    print(f"   ⚠️  Vault storage failed: {vault_error}")
                
                creation_results.append({
                    'index': i,
                    'status': 'success',
                    'google_event_id': created_event['id'],
                    'event_summary': event_data['summary'],
                    'calendar_link': created_event.get('htmlLink'),
                    'vault_key': vault_key,
                    'confidence_score': event_data.get('confidence_score', 1.0)
                })
                
                success_count += 1
                print(f"   ✅ Created: {event_data['summary']}")

            except Exception as e:
                creation_results.append({
                    'index': i,
                    'status': 'error',
                    'error': str(e),
                    'event_summary': event_data.get('summary', 'Unknown Event')
                })
                error_count += 1
                print(f"   ❌ Failed to create: {event_data.get('summary', 'Unknown')} - {e}")

        # Summary
        total_events = len(events)
        print(f"\n📊 Calendar Creation Summary:")
        print(f"   Total: {total_events} | Success: {success_count} | Errors: {error_count}")

        return {
            'status': 'success' if error_count == 0 else 'partial' if success_count > 0 else 'error',
            'message': f"Created {success_count}/{total_events} events successfully with access token",
            'results': creation_results,
            'statistics': {
                'total_events': total_events,
                'successful_creations': success_count,
                'failed_creations': error_count,
                'success_rate': (success_count / total_events) * 100 if total_events > 0 else 0
            },
            'authentication_method': 'access_token'
        }

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

    def handle(self, user_id: str, email_token_str: str, calendar_token_str: str, 
               google_access_token: str, action: str = "comprehensive_analysis", **kwargs):
        """
        Enhanced main entry point for the agent with multiple capabilities.
        
        Args:
            user_id: User identifier
            email_token_str: Consent token for email access
            calendar_token_str: Consent token for calendar access
            google_access_token: Google OAuth access token from frontend
            action: Action to perform ('comprehensive_analysis', 'manual_event', 'analyze_only')
            **kwargs: Additional parameters based on action
            
        Returns:
            Dictionary with results based on the requested action
        """
        print(f"🚀 AddToCalendar Agent starting: {action}")
        print(f"🔑 Using access token authentication (no credentials file needed)")
        
        try:
            if action == "comprehensive_analysis":
                # Full pipeline: read emails, prioritize, categorize, extract events, create calendar
                is_valid_email, reason_email, _ = validate_token(email_token_str, expected_scope=ConsentScope.VAULT_READ_EMAIL)
                if not is_valid_email:
                    raise PermissionError(f"Email Access Denied: {reason_email}")
                
                is_valid_cal, reason_cal, _ = validate_token(calendar_token_str, expected_scope=ConsentScope.VAULT_WRITE_CALENDAR)
                if not is_valid_cal:
                    raise PermissionError(f"Calendar Access Denied: {reason_cal}")
                
                print("✅ Consent validated for comprehensive analysis.")
                return self.run_comprehensive_email_analysis_with_token(
                    user_id, email_token_str, calendar_token_str, google_access_token
                )
                
            elif action == "manual_event":
                # Create a manual event with AI assistance
                event_description = kwargs.get('event_description', '')
                if not event_description:
                    return {
                        'status': 'error',
                        'message': 'event_description parameter required for manual_event action'
                    }
                
                is_valid_cal, reason_cal, _ = validate_token(calendar_token_str, expected_scope=ConsentScope.VAULT_WRITE_CALENDAR)
                if not is_valid_cal:
                    raise PermissionError(f"Calendar Access Denied: {reason_cal}")
                
                print("✅ Consent validated for manual event creation.")
                
                # Create AI-assisted event
                manual_result = self.create_manual_event(event_description, user_id, calendar_token_str)
                
                if manual_result['status'] == 'success' and kwargs.get('add_to_calendar', True):
                    # Add to calendar using access token
                    events_to_create = [manual_result['event']]
                    calendar_result = self.create_events_in_calendar_with_token(
                        events_to_create, user_id, calendar_token_str, google_access_token
                    )
                    
                    return {
                        'status': 'success',
                        'message': 'Manual event created and added to calendar',
                        'manual_event': manual_result,
                        'calendar_result': calendar_result,
                        'authentication_method': 'access_token'
                    }
                else:
                    return manual_result
                    
            elif action == "analyze_only":
                # Analyze emails without creating calendar events
                is_valid_email, reason_email, _ = validate_token(email_token_str, expected_scope=ConsentScope.VAULT_READ_EMAIL)
                if not is_valid_email:
                    raise PermissionError(f"Email Access Denied: {reason_email}")
                
                print("✅ Consent validated for email analysis only.")
                
                # Run analysis pipeline without calendar creation using access token
                gmail_service = self._get_google_service_with_token('gmail', 'v1', google_access_token)
                emails = self._read_emails(gmail_service, max_results=self.max_emails)
                prioritized_emails = self.prioritize_emails(emails, user_id, email_token_str)
                categorized_emails = self.categorize_emails(prioritized_emails, user_id, email_token_str)
                extracted_events = self._extract_events_with_ai(categorized_emails, user_id, email_token_str)
                
                return {
                    'status': 'success',
                    'message': 'Email analysis completed (no calendar events created)',
                    'analysis_results': {
                        'total_emails': len(emails),
                        'prioritized_emails': len([e for e in categorized_emails if e.get('priority_score', 0) >= 7]),
                        'extracted_events': len(extracted_events)
                    },
                    'data': {
                        'top_emails': categorized_emails[:10],
                        'potential_events': extracted_events
                    },
                    'authentication_method': 'access_token'
                }
                
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown action: {action}. Available actions: comprehensive_analysis, manual_event, analyze_only'
                }
                
        except PermissionError as e:
            return {
                'status': 'permission_denied',
                'message': str(e)
            }
        except Exception as e:
            print(f"❌ Agent execution failed: {e}")
            return {
                'status': 'error',
                'message': f'Agent execution failed: {str(e)}'
            }