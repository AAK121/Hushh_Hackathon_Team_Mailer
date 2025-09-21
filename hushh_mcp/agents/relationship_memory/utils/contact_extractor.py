"""
Robust Contact Information Extractor for Relationship Memory Agent
Extracts contact information from natural language text using multiple strategies
"""

import re
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class ExtractedContact:
    """Structured contact information extracted from text"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    relationship: str = "Professional"
    confidence: float = 0.0


class ContactExtractor:
    """
    Comprehensive contact information extractor from natural language text.
    Uses multiple extraction strategies for maximum reliability.
    """
    
    def __init__(self):
        # Comprehensive email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )
        
        # Phone number patterns (various formats)
        self.phone_patterns = [
            re.compile(r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'),  # US format
            re.compile(r'\+?(\d{1,3})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})[-.\s]?(\d{3,4})'),    # International
            re.compile(r'(\d{3})[-.\s]?(\d{3})[-.\s]?(\d{4})'),                              # Simple format
        ]
        
        # Enhanced name extraction patterns
        self.name_patterns = [
            # Direct patterns for "add contact named X"
            re.compile(r'(?:add|create|new)\s+(?:a\s+)?contact\s+(?:named?\s+)?([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+with\s+email|\s+email|\s*$)', re.IGNORECASE),
            # Pattern for "contact name X"
            re.compile(r'contact\s+name\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+with\s+email|\s+email|\s*$)', re.IGNORECASE),
            # Pattern for "I met X" or "met X"
            re.compile(r'(?:met|meet)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+with\s+email|\s+email|\s+from|\s*$)', re.IGNORECASE),
            # Pattern for "X with email" (name before email context) - be more careful
            re.compile(r'\b([A-Za-z]+(?:\s+[A-Za-z]+)*?)\s+with\s+email', re.IGNORECASE),
            # Pattern for "contact X"
            re.compile(r'contact\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+with\s+email|\s+email|\s+from|\s*$)', re.IGNORECASE),
            # Fallback: capitalized words that could be names
            re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'),
        ]
        
        # Company extraction patterns
        self.company_patterns = [
            re.compile(r'from\s+([A-Z][A-Za-z\s&]+(?:Corp|Inc|LLC|Ltd|Company|Co\.|Technologies|Tech|Solutions))', re.IGNORECASE),
            re.compile(r'at\s+([A-Z][A-Za-z\s&]+(?:Corp|Inc|LLC|Ltd|Company|Co\.|Technologies|Tech|Solutions))', re.IGNORECASE),
            re.compile(r'works?\s+(?:at|for)\s+([A-Z][A-Za-z\s&]+)', re.IGNORECASE),
        ]
        
        # Role/title patterns
        self.role_patterns = [
            re.compile(r'(?:is\s+a|works?\s+as\s+a?|title\s+is)\s+([A-Z][A-Za-z\s]+(?:Manager|Director|Developer|Engineer|Analyst|Specialist|Lead|Senior|Junior))', re.IGNORECASE),
            re.compile(r'([A-Z][A-Za-z\s]*(?:Manager|Director|Developer|Engineer|Analyst|Specialist|Lead|CEO|CTO|CFO))', re.IGNORECASE),
        ]
        
        # Contact trigger words for detection
        self.contact_triggers = [
            'add contact', 'new contact', 'create contact', 'contact name', 'contact named',
            'met', 'meet', 'introduce', 'person', 'colleague', 'friend',
            'client', 'customer', 'vendor', 'partner', 'email', '@'
        ]

    def extract_contact_from_text(self, text: str) -> Optional[ExtractedContact]:
        """
        Main extraction method that uses multiple strategies to extract contact info.
        
        Args:
            text: Natural language text containing contact information
            
        Returns:
            ExtractedContact object or None if no contact found
        """
        print(f"🔍 [ContactExtractor] Processing: '{text}'")
        
        try:
            # Check if text contains contact-related content
            if not self._is_contact_related(text):
                print("❌ [ContactExtractor] Not contact-related")
                return None
            
            print("✅ [ContactExtractor] Detected contact-related input")
            
            # Extract individual components
            name = self._extract_name(text)
            email = self._extract_email(text)
            phone = self._extract_phone(text)
            company = self._extract_company(text)
            role = self._extract_role(text)
            relationship = self._determine_relationship(text)
            
            print(f"📋 [ContactExtractor] Extracted components:")
            print(f"   Name: {name}")
            print(f"   Email: {email}")
            print(f"   Phone: {phone}")
            print(f"   Company: {company}")
            print(f"   Role: {role}")
            
            # Calculate confidence based on extracted information
            confidence = self._calculate_confidence(name, email, phone, company, role)
            
            # Must have at least a name to be considered a valid contact
            if not name:
                print("❌ [ContactExtractor] No valid name found")
                return None
            
            contact = ExtractedContact(
                name=name,
                email=email,
                phone=phone,
                company=company,
                role=role,
                relationship=relationship,
                confidence=confidence
            )
            
            print(f"✅ [ContactExtractor] Successfully extracted contact with confidence {confidence:.2f}")
            return contact
            
        except Exception as e:
            print(f"❌ [ContactExtractor] Error: {e}")
            return None

    def _is_contact_related(self, text: str) -> bool:
        """Check if text contains contact-related keywords"""
        text_lower = text.lower()
        return any(trigger in text_lower for trigger in self.contact_triggers)

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract person's name using multiple patterns"""
        print(f"🔍 [ContactExtractor] Extracting name from: '{text}'")
        
        # Try specific contact patterns first
        for i, pattern in enumerate(self.name_patterns):
            match = pattern.search(text)
            if match:
                potential_name = match.group(1).strip()
                print(f"   Pattern {i+1} matched: '{potential_name}'")
                
                if self._is_valid_name(potential_name):
                    formatted_name = self._format_name(potential_name)
                    print(f"   ✅ Valid name found: '{formatted_name}'")
                    return formatted_name
                else:
                    print(f"   ❌ Invalid name: '{potential_name}'")
        
        print("❌ [ContactExtractor] No valid name found with patterns")
        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        match = self.email_pattern.search(text)
        if match:
            email = match.group().lower()
            print(f"✅ [ContactExtractor] Email found: {email}")
            return email
        print("❌ [ContactExtractor] No email found")
        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        for pattern in self.phone_patterns:
            match = pattern.search(text)
            if match:
                # Format phone number consistently
                digits = ''.join(filter(str.isdigit, match.group()))
                if len(digits) >= 10:
                    if len(digits) == 10:
                        formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                        print(f"✅ [ContactExtractor] Phone found: {formatted}")
                        return formatted
                    elif len(digits) == 11 and digits[0] == '1':
                        formatted = f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
                        print(f"✅ [ContactExtractor] Phone found: {formatted}")
                        return formatted
        print("❌ [ContactExtractor] No phone found")
        return None

    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name from text"""
        for pattern in self.company_patterns:
            match = pattern.search(text)
            if match:
                company = match.group(1).strip()
                if len(company) > 1:
                    formatted = self._format_company(company)
                    print(f"✅ [ContactExtractor] Company found: {formatted}")
                    return formatted
        print("❌ [ContactExtractor] No company found")
        return None

    def _extract_role(self, text: str) -> Optional[str]:
        """Extract job role/title from text"""
        for pattern in self.role_patterns:
            match = pattern.search(text)
            if match:
                role = match.group(1).strip()
                if len(role) > 2:
                    formatted = self._format_role(role)
                    print(f"✅ [ContactExtractor] Role found: {formatted}")
                    return formatted
        print("❌ [ContactExtractor] No role found")
        return None

    def _determine_relationship(self, text: str) -> str:
        """Determine relationship type based on context"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['friend', 'buddy', 'pal']):
            return "Friend"
        elif any(word in text_lower for word in ['family', 'relative', 'cousin', 'uncle', 'aunt']):
            return "Family"
        elif any(word in text_lower for word in ['client', 'customer']):
            return "Client"
        elif any(word in text_lower for word in ['vendor', 'supplier']):
            return "Vendor"
        elif any(word in text_lower for word in ['colleague', 'coworker', 'teammate']):
            return "Colleague"
        else:
            return "Professional"

    def _is_valid_name(self, name: str) -> bool:
        """Validate if extracted text is likely a person's name"""
        if not name or len(name) < 2:
            return False
        
        # Exclude common non-name words
        excluded_words = {
            'email', 'phone', 'contact', 'from', 'with', 'named', 'called',
            'person', 'client', 'customer', 'company', 'corp', 'inc', 'llc',
            'add', 'create', 'new', 'name', 'information', 'details'
        }
        
        name_lower = name.lower().strip()
        
        # Check if it's an excluded word
        if name_lower in excluded_words:
            return False
        
        # Check if it contains digits (names shouldn't have numbers)
        if any(char.isdigit() for char in name):
            return False
        
        # Check if it's all uppercase (likely not a name)
        if name.isupper() and len(name) > 3:
            return False
        
        # Must contain at least one letter
        if not any(char.isalpha() for char in name):
            return False
        
        return True

    def _format_name(self, name: str) -> str:
        """Format name to proper case"""
        return ' '.join(word.capitalize() for word in name.split())

    def _format_company(self, company: str) -> str:
        """Format company name"""
        return company.strip().title()

    def _format_role(self, role: str) -> str:
        """Format job role/title"""
        return role.strip().title()

    def _calculate_confidence(self, name: str, email: str, phone: str, 
                            company: str, role: str) -> float:
        """Calculate confidence score based on extracted information"""
        score = 0.0
        
        if name:
            score += 0.4  # Name is most important
        if email:
            score += 0.3  # Email is strong indicator
        if phone:
            score += 0.2  # Phone adds confidence
        if company:
            score += 0.1  # Company context helps
        if role:
            score += 0.1  # Role context helps
        
        # Bonus for having multiple fields
        field_count = sum(1 for field in [name, email, phone, company, role] if field)
        if field_count >= 3:
            score += 0.1
        
        return min(score, 1.0)


# Test the contact extractor
if __name__ == "__main__":
    extractor = ContactExtractor()
    
    test_cases = [
        "add a contact name alook with email 343434@gmail.com",
        "add a contact named alok with email akdjfa@gmail.com",
        "I met John Smith from TechCorp, his email is john@techcorp.com",
        "Create contact Sarah Johnson, sarah@company.com, works as Product Manager",
        "New contact: Mike Davis, mike.davis@startup.io, phone (555) 123-4567",
        "Contact named Lisa Chen from ABC Inc, she's a Senior Developer"
    ]
    
    print("🧪 Testing Contact Extractor:")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{test_text}'")
        contact = extractor.extract_contact_from_text(test_text)
        
        if contact:
            print(f"   ✅ Extracted Contact:")
            print(f"      Name: {contact.name}")
            print(f"      Email: {contact.email}")
            print(f"      Phone: {contact.phone}")
            print(f"      Company: {contact.company}")
            print(f"      Role: {contact.role}")
            print(f"      Relationship: {contact.relationship}")
            print(f"      Confidence: {contact.confidence:.2f}")
        else:
            print(f"   ❌ No contact extracted")