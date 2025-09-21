"""
LLM-Based Contact Extractor for Relationship Memory Agent
Uses Google Gemini API for intelligent contact information parsing from natural language
"""

import os
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Google Generative AI not available. Install with: pip install google-generativeai")


class LLMContactExtractor:
    """
    AI-powered contact information extractor using Google Gemini API.
    
    This class replaces regex-based parsing with intelligent LLM understanding
    of natural language contact information input.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM Contact Extractor.
        
        Args:
            api_key: Google Gemini API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.model = None
        self.is_configured = False
        
        if not GEMINI_AVAILABLE:
            print("❌ Google Generative AI library not available")
            return
        
        if not self.api_key:
            print("⚠️ No Gemini API key provided. Contact extraction will use fallback regex parsing.")
            return
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.is_configured = True
            print("✅ LLM Contact Extractor initialized with Gemini API")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini API: {e}")
            self.is_configured = False
    
    def extract_contact_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract contact information from natural language text using LLM.
        
        Args:
            text: Natural language input containing contact information
            
        Returns:
            Dictionary containing extracted contact information and confidence score
        """
        if not self.is_configured or not self.model:
            print("⚠️ LLM not available, falling back to regex extraction")
            return self._fallback_regex_extraction(text)
        
        try:
            # Create a detailed prompt for contact extraction
            prompt = f"""
You are an expert contact information extractor. Extract contact details from the following natural language text and return them in a specific JSON format.

INPUT TEXT: "{text}"

Extract the following information if available:
- name: Full name of the person
- email: Email address
- phone: Phone number (any format)
- company: Company or workplace
- location: Address or location
- notes: Any additional context or notes
- title: Job title or role
- website: Website or social media profiles

IMPORTANT RULES:
1. Return ONLY a valid JSON object, no additional text or explanations
2. If information is not found, use null for that field
3. For the name field, extract the full name as mentioned
4. For emails, extract any valid email addresses
5. For phone numbers, extract any number that looks like a phone number
6. For notes, include any additional context or relationship information
7. Be case-sensitive for names and emails
8. Include a "confidence" field (0.0 to 1.0) indicating how confident you are about the extraction

EXAMPLE OUTPUT FORMAT:
{{
    "name": "John Smith",
    "email": "john.smith@company.com", 
    "phone": "+1-555-123-4567",
    "company": "Tech Corp",
    "location": "New York",
    "title": "Software Engineer",
    "website": null,
    "notes": "Met at tech conference, interested in our product",
    "confidence": 0.95
}}

Now extract the contact information from the input text:
"""

            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                print("❌ Empty response from Gemini API")
                return self._fallback_regex_extraction(text)
            
            # Parse the JSON response
            try:
                # Clean the response text (remove any markdown formatting)
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                contact_data = json.loads(response_text)
                
                # Validate required fields
                if not contact_data.get('name'):
                    print("⚠️ No name extracted from LLM response")
                    return self._fallback_regex_extraction(text)
                
                # Add metadata
                contact_data['extraction_method'] = 'llm'
                contact_data['extracted_at'] = datetime.now().isoformat()
                contact_data['original_text'] = text
                
                # Ensure confidence is set
                if 'confidence' not in contact_data:
                    contact_data['confidence'] = 0.8
                
                print(f"✅ LLM extracted contact: {contact_data.get('name')} (confidence: {contact_data.get('confidence')})")
                return contact_data
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse LLM JSON response: {e}")
                print(f"Raw response: {response.text}")
                return self._fallback_regex_extraction(text)
            
        except Exception as e:
            print(f"❌ LLM contact extraction failed: {e}")
            return self._fallback_regex_extraction(text)
    
    def _fallback_regex_extraction(self, text: str) -> Dict[str, Any]:
        """
        Fallback regex-based contact extraction when LLM is not available.
        
        Args:
            text: Input text to extract contact information from
            
        Returns:
            Dictionary with extracted contact information
        """
        import re
        
        print("🔄 Using fallback regex extraction")
        
        contact_data = {
            'name': None,
            'email': None,
            'phone': None,
            'company': None,
            'location': None,
            'title': None,
            'website': None,
            'notes': None,
            'confidence': 0.6,  # Lower confidence for regex
            'extraction_method': 'regex',
            'extracted_at': datetime.now().isoformat(),
            'original_text': text
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_data['email'] = email_match.group()
        
        # Extract phone number
        phone_patterns = [
            r'\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',  # US format
            r'\+?(\d{1,4})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})',  # International
            r'(\d{3,4})[-.\s]?(\d{3,4})[-.\s]?(\d{4})'  # Simple format
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact_data['phone'] = phone_match.group()
                break
        
        # Extract name (more sophisticated patterns)
        name_patterns = [
            r'(?:add|contact|name|person|friend|colleague)\s+(?:named?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:with|called|name)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Name at start
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:with|has|from)'  # Name before descriptors
        ]
        
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.IGNORECASE)
            if name_match:
                potential_name = name_match.group(1)
                # Validate it's not an email or obviously not a name
                if '@' not in potential_name and len(potential_name.split()) <= 4:
                    contact_data['name'] = potential_name.title()
                    break
        
        # Extract company
        company_patterns = [
            r'(?:works?\s+at|from|company|corporation|corp)\s+([A-Z][A-Za-z\s&,.-]+?)(?:\s|$|,|\.|with|and)',
            r'(?:at|@)\s+([A-Z][A-Za-z\s&,.-]+?)(?:\s|$|,|\.|with)'
        ]
        
        for pattern in company_patterns:
            company_match = re.search(pattern, text, re.IGNORECASE)
            if company_match:
                contact_data['company'] = company_match.group(1).strip()
                break
        
        # If we found at least name or email, consider it a successful extraction
        if contact_data['name'] or contact_data['email']:
            contact_data['confidence'] = 0.7
            print(f"✅ Regex extracted contact: {contact_data.get('name') or 'No name'}")
        else:
            contact_data['confidence'] = 0.3
            contact_data['notes'] = f"Could not extract clear contact information from: {text}"
            print("⚠️ Regex extraction found minimal contact information")
        
        return contact_data

    def validate_extraction(self, contact_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate extracted contact information.
        
        Args:
            contact_data: Extracted contact information
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if not contact_data:
            return False, "No contact data provided"
        
        # Must have at least a name or email
        if not contact_data.get('name') and not contact_data.get('email'):
            return False, "Contact must have at least a name or email address"
        
        # Check confidence threshold
        confidence = contact_data.get('confidence', 0)
        if confidence < 0.3:
            return False, f"Extraction confidence too low: {confidence}"
        
        # Validate email format if present
        if contact_data.get('email'):
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not re.match(email_pattern, contact_data['email']):
                return False, "Invalid email format"
        
        return True, "Contact validation passed"

    def enhance_contact_data(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance contact data with additional fields for the relationship memory system.
        
        Args:
            contact_data: Basic contact information
            
        Returns:
            Enhanced contact data with relationship memory fields
        """
        enhanced_data = contact_data.copy()
        
        # Add relationship memory specific fields
        enhanced_data.update({
            'id': contact_data.get('name', 'unknown').lower().replace(' ', '_'),
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'interaction_count': 0,
            'last_interaction': None,
            'relationship_strength': 0.5,  # Default neutral strength
            'tags': [],
            'dates': {},  # For birthdays, anniversaries, etc.
            'preferences': {},
            'interaction_history': []
        })
        
        # Generate meaningful notes if none exist
        if not enhanced_data.get('notes') and enhanced_data.get('extraction_method') == 'llm':
            notes_parts = []
            if enhanced_data.get('company'):
                notes_parts.append(f"Works at {enhanced_data['company']}")
            if enhanced_data.get('title'):
                notes_parts.append(f"Role: {enhanced_data['title']}")
            if enhanced_data.get('location'):
                notes_parts.append(f"Location: {enhanced_data['location']}")
            
            if notes_parts:
                enhanced_data['notes'] = "; ".join(notes_parts)
        
        return enhanced_data


# Export the main class
__all__ = ['LLMContactExtractor']

# Test function for development
def test_extraction():
    """Test the LLM contact extractor with sample inputs."""
    extractor = LLMContactExtractor()
    
    test_cases = [
        "add a contact name alook with email 343434@gmail.com",
        "John Smith works at Microsoft, email john.smith@microsoft.com, phone 555-123-4567",
        "Meet Sarah Johnson from Google next week, her email is sarah.j@google.com",
        "Contact: Mike Chen, Software Engineer at OpenAI, mike@openai.com, based in San Francisco"
    ]
    
    for test_input in test_cases:
        print(f"\n🧪 Testing: {test_input}")
        result = extractor.extract_contact_from_text(test_input)
        print(f"Result: {result}")
        
        is_valid, reason = extractor.validate_extraction(result)
        print(f"Valid: {is_valid} - {reason}")

if __name__ == "__main__":
    test_extraction()