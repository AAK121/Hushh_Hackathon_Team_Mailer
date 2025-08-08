"""
Email Prioritization Operon for HushMCP
Small, reusable function for AI-powered email prioritization
"""

import json
import google.generativeai as genai
from typing import List, Dict, Optional
from datetime import datetime

from ..consent.token import validate_token
from ..types import ConsentScope


def prioritize_emails_operon(emails: List[Dict], user_id: str, consent_token: str, 
                           ai_model: str = "gemini-1.5-flash") -> List[Dict]:
    """
    Operon: AI-powered email prioritization with scoring (1-10 scale).
    
    This is a reusable operon that can be called by any agent needing email prioritization.
    
    Args:
        emails: List of email dictionaries with basic fields
        user_id: User identifier for consent validation
        consent_token: Valid consent token for email access
        ai_model: Gemini model to use for prioritization
        
    Returns:
        List of emails with added priority_score field
        
    Raises:
        PermissionError: If consent token is invalid
        ValueError: If emails format is invalid
    """
    
    # Configure Gemini AI
    import os
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if google_api_key:
        genai.configure(api_key=google_api_key)
    
    # Validate consent before processing
    is_valid, reason, _ = validate_token(consent_token, expected_scope=ConsentScope.VAULT_READ_EMAIL)
    if not is_valid:
        raise PermissionError(f"Email Prioritization Access Denied: {reason}")
    
    if not emails:
        return []
    
    if not isinstance(emails, list):
        raise ValueError("emails must be a list of dictionaries")
    
    print(f"🎯 Prioritizing {len(emails)} emails using {ai_model}...")
    
    # Prepare email summaries for AI analysis
    email_summaries = []
    for i, email in enumerate(emails):
        # Validate email structure
        required_fields = ['subject', 'sender', 'date']
        if not all(field in email for field in required_fields):
            print(f"   ⚠️  Skipping email {i}: missing required fields")
            continue
            
        summary = {
            'id': i,
            'subject': email['subject'][:200],  # Limit subject length
            'sender': email['sender'],
            'date': email['date'],
            'snippet': email.get('content', '')[:300] if email.get('content') else ''
        }
        email_summaries.append(summary)
    
    if not email_summaries:
        print("   ⚠️  No valid emails to prioritize")
        return emails
    
    # Create AI prompt for prioritization
    prompt = f"""
    Analyze these emails and assign a priority score from 1-10 for each email.
    
    Priority Guidelines:
    - 10: Critical/urgent (deadlines, important meetings, emergencies)
    - 8-9: High priority (work tasks, important communications)
    - 6-7: Medium priority (regular work, social events)
    - 4-5: Low priority (newsletters, promotions, non-urgent)
    - 1-3: Very low priority (spam, automated messages, old threads)
    
    Consider:
    - Sender importance (boss, clients, family vs automated systems)
    - Subject urgency (deadlines, "urgent", "ASAP", meeting invites)
    - Time sensitivity (today's meetings vs general information)
    - Content relevance (work tasks vs promotional emails)
    
    Return JSON with priority scores:
    {{
        "priorities": [
            {{"email_id": 0, "priority_score": 8, "reasoning": "Meeting invite from manager"}},
            {{"email_id": 1, "priority_score": 3, "reasoning": "Newsletter subscription"}}
        ]
    }}
    
    Emails to analyze:
    {json.dumps(email_summaries, indent=2)}
    """
    
    try:
        model = genai.GenerativeModel(ai_model)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        
        priority_data = json.loads(response.text)
        priorities = priority_data.get('priorities', [])
        
        # Apply priority scores to emails
        prioritized_emails = []
        for email in emails:
            email_copy = email.copy()
            
            # Find matching priority score
            email_index = emails.index(email)
            priority_info = next(
                (p for p in priorities if p.get('email_id') == email_index), 
                None
            )
            
            if priority_info:
                email_copy['priority_score'] = priority_info.get('priority_score', 5)
                email_copy['priority_reasoning'] = priority_info.get('reasoning', 'AI analysis')
                print(f"   📧 Email {email_index}: {email['subject'][:50]}... → Priority: {email_copy['priority_score']}")
            else:
                email_copy['priority_score'] = 5  # Default medium priority
                email_copy['priority_reasoning'] = 'Default priority (AI analysis failed)'
                print(f"   ⚠️  Email {email_index}: No priority assigned, using default")
            
            prioritized_emails.append(email_copy)
        
        # Sort by priority score (descending)
        prioritized_emails.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        high_priority_count = len([e for e in prioritized_emails if e.get('priority_score', 0) >= 8])
        medium_priority_count = len([e for e in prioritized_emails if e.get('priority_score', 0) >= 6])
        
        print(f"✅ Prioritization complete: {high_priority_count} high priority, {medium_priority_count} medium+ priority")
        return prioritized_emails
        
    except Exception as e:
        print(f"❌ Email prioritization failed: {e}")
        # Return original emails with default priority scores
        fallback_emails = []
        for email in emails:
            email_copy = email.copy()
            email_copy['priority_score'] = 5
            email_copy['priority_reasoning'] = f'Fallback priority (AI failed: {str(e)})'
            fallback_emails.append(email_copy)
        return fallback_emails


def categorize_emails_operon(emails: List[Dict], user_id: str, consent_token: str,
                           ai_model: str = "gemini-1.5-flash") -> List[Dict]:
    """
    Operon: AI-powered email categorization into semantic categories.
    
    This is a reusable operon that can be called by any agent needing email categorization.
    
    Args:
        emails: List of email dictionaries (ideally pre-prioritized)
        user_id: User identifier for consent validation
        consent_token: Valid consent token for email access
        ai_model: Gemini model to use for categorization
        
    Returns:
        List of emails with added category field
        
    Raises:
        PermissionError: If consent token is invalid
    """
    
    # Configure Gemini AI
    import os
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if google_api_key:
        genai.configure(api_key=google_api_key)
    
    # Validate consent
    is_valid, reason, _ = validate_token(consent_token, expected_scope=ConsentScope.VAULT_READ_EMAIL)
    if not is_valid:
        raise PermissionError(f"Email Categorization Access Denied: {reason}")
    
    if not emails:
        return []
    
    print(f"🏷️  Categorizing {len(emails)} emails using {ai_model}...")
    
    # Prepare email data for categorization
    email_data = []
    for i, email in enumerate(emails):
        data = {
            'id': i,
            'subject': email.get('subject', '')[:200],
            'sender': email.get('sender', ''),
            'content_snippet': email.get('content', '')[:400] if email.get('content') else '',
            'priority_score': email.get('priority_score', 5)
        }
        email_data.append(data)
    
    prompt = f"""
    Categorize these emails into relevant categories. Choose the most appropriate category for each email.
    
    Available Categories:
    - work: Job-related emails, meetings, projects, professional communications
    - personal: Friends, family, personal matters, social communications
    - finance: Banking, bills, investments, purchases, financial services
    - travel: Flights, hotels, bookings, travel confirmations, itineraries
    - events: Invitations, event announcements, calendar-related items
    - shopping: E-commerce, orders, shipping, product updates, retail
    - health: Medical appointments, health services, wellness, insurance
    - education: School, courses, learning, academic communications
    - news: Newsletters, news updates, industry updates, subscriptions
    - spam: Unwanted emails, promotional spam, suspicious messages
    - other: Anything that doesn't fit the above categories
    
    Return JSON:
    {{
        "categories": [
            {{"email_id": 0, "category": "work", "confidence": 0.9}},
            {{"email_id": 1, "category": "shopping", "confidence": 0.8}}
        ]
    }}
    
    Emails to categorize:
    {json.dumps(email_data, indent=2)}
    """
    
    try:
        model = genai.GenerativeModel(ai_model)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        
        category_data = json.loads(response.text)
        categories = category_data.get('categories', [])
        
        # Apply categories to emails
        categorized_emails = []
        category_counts = {}
        
        for email in emails:
            email_copy = email.copy()
            email_index = emails.index(email)
            
            # Find matching category
            category_info = next(
                (c for c in categories if c.get('email_id') == email_index),
                None
            )
            
            if category_info:
                category = category_info.get('category', 'other')
                confidence = category_info.get('confidence', 0.5)
                
                email_copy['category'] = category
                email_copy['category_confidence'] = confidence
                
                category_counts[category] = category_counts.get(category, 0) + 1
                print(f"   📂 Email {email_index}: {category} (confidence: {confidence:.2f})")
            else:
                email_copy['category'] = 'other'
                email_copy['category_confidence'] = 0.5
                category_counts['other'] = category_counts.get('other', 0) + 1
                print(f"   ⚠️  Email {email_index}: No category assigned, using 'other'")
            
            categorized_emails.append(email_copy)
        
        print(f"✅ Categorization complete:")
        for category, count in sorted(category_counts.items()):
            print(f"   📂 {category}: {count} emails")
        
        return categorized_emails
        
    except Exception as e:
        print(f"❌ Email categorization failed: {e}")
        # Return emails with default 'other' category
        fallback_emails = []
        for email in emails:
            email_copy = email.copy()
            email_copy['category'] = 'other'
            email_copy['category_confidence'] = 0.5
            fallback_emails.append(email_copy)
        return fallback_emails
