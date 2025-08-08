# hushh_mcp/operons/verify_email.py

import re
from typing import List, Dict, Optional

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

def verify_user_email(email: str) -> bool:
    """
    Checks whether the provided email address is valid in format.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not email or not isinstance(email, str):
        return False

    return EMAIL_REGEX.match(email) is not None


def verify_email_operon(email: str, check_advanced: bool = False) -> bool:
    """
    Enhanced email verification operon for HushMCP agents.
    
    This is a reusable operon that can be called by any agent needing email validation.
    
    Args:
        email: Email address to validate
        check_advanced: Whether to perform additional validation checks
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    
    if not email or not isinstance(email, str):
        return False
    
    # Use the existing regex validation
    if not EMAIL_REGEX.match(email):
        return False
    
    if check_advanced:
        # Additional validation checks
        if email.count('@') != 1:
            return False
        
        local_part, domain = email.split('@')
        
        # Check local part length (max 64 characters)
        if len(local_part) > 64 or len(local_part) == 0:
            return False
        
        # Check domain length (max 253 characters)
        if len(domain) > 253 or len(domain) == 0:
            return False
        
        # Check for consecutive dots
        if '..' in email:
            return False
        
        # Check if starts or ends with dot
        if local_part.startswith('.') or local_part.endswith('.'):
            return False
    
    return True


def validate_email_list_operon(emails: List[str], check_advanced: bool = False) -> Dict:
    """
    Operon: Validates a list of email addresses with detailed results.
    
    Args:
        emails: List of email addresses to validate
        check_advanced: Whether to perform advanced validation
        
    Returns:
        dict: Validation results with counts and details
    """
    
    if not emails or not isinstance(emails, list):
        return {
            'valid_emails': [],
            'invalid_emails': [],
            'total_checked': 0,
            'valid_count': 0,
            'invalid_count': 0,
            'validation_rate': 0.0
        }
    
    valid_emails = []
    invalid_emails = []
    
    for email in emails:
        if verify_email_operon(email, check_advanced):
            valid_emails.append(email)
        else:
            invalid_emails.append(email)
    
    validation_rate = (len(valid_emails) / len(emails)) * 100 if emails else 0.0
    
    return {
        'valid_emails': valid_emails,
        'invalid_emails': invalid_emails,
        'total_checked': len(emails),
        'valid_count': len(valid_emails),
        'invalid_count': len(invalid_emails),
        'validation_rate': round(validation_rate, 2)
    }
