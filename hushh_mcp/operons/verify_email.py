# hushh_mcp/operons/verify_email.py

import re
from typing import List, Dict, Any
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope

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

def verify_email_operon(email_addresses: List[str], user_id: str, consent_token: str) -> Dict[str, Any]:
    """
    Operon: Verify multiple email addresses for validity.
    
    This is a reusable operon that can be called by any agent needing email verification.
    
    Args:
        email_addresses: List of email addresses to verify
        user_id: User identifier for consent validation
        consent_token: Valid consent token for email verification
        
    Returns:
        Dictionary with verification results for each email
        
    Raises:
        PermissionError: If consent token is invalid
        ValueError: If input format is invalid
    """
    # Validate consent before processing
    is_valid, reason, _ = validate_token(consent_token, expected_scope=ConsentScope.VAULT_READ_EMAIL)
    if not is_valid:
        raise PermissionError(f"Email Verification Access Denied: {reason}")
    
    if not isinstance(email_addresses, list):
        raise ValueError("email_addresses must be a list of strings")
    
    print(f"🔍 Verifying {len(email_addresses)} email addresses...")
    
    results = {
        "total_emails": len(email_addresses),
        "valid_emails": [],
        "invalid_emails": [],
        "verification_results": []
    }
    
    for i, email in enumerate(email_addresses):
        is_valid_email = verify_user_email(email)
        
        result = {
            "index": i,
            "email": email,
            "is_valid": is_valid_email,
            "format_check": "passed" if is_valid_email else "failed"
        }
        
        if is_valid_email:
            results["valid_emails"].append(email)
            print(f"   ✅ {email}: Valid")
        else:
            results["invalid_emails"].append(email)
            print(f"   ❌ {email}: Invalid format")
            
        results["verification_results"].append(result)
    
    results["valid_count"] = len(results["valid_emails"])
    results["invalid_count"] = len(results["invalid_emails"])
    results["success_rate"] = (results["valid_count"] / results["total_emails"]) * 100 if results["total_emails"] > 0 else 0
    
    print(f"✅ Verification complete: {results['valid_count']}/{results['total_emails']} valid emails ({results['success_rate']:.1f}%)")
    
    return results
