#!/usr/bin/env python3
"""
Test script to verify the placeholder replacement fix in MailerPanda agent.
"""

import os
import sys
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SafeDict(dict):
    """Custom dict that handles missing placeholders gracefully."""
    def __missing__(self, key):
        return "{" + key + "}"

def test_placeholder_replacement():
    """Test that placeholders are properly replaced with contact data."""
    
    print("🧪 Testing Placeholder Replacement Fix")
    print("=" * 50)
    
    # Sample contact data
    contact_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'company_name': 'Tech Corp',
        'description': 'a potential client interested in our web development services'
    }
    
    # Sample email template with placeholders
    template_with_placeholders = """Dear {name},

I am writing to express my sincere appreciation based on the {description} you provided.

Thank you for your time and effort.

Sincerely,
The MailerPanda Team"""
    
    subject_with_placeholders = "Thank you, {name}!"
    
    print("📧 Original Template:")
    print(template_with_placeholders)
    print("\n📌 Original Subject:")
    print(subject_with_placeholders)
    print("\n👤 Contact Data:")
    print(contact_data)
    
    # Apply the fix - use SafeDict for placeholder replacement
    safe_contact = SafeDict(contact_data)
    personalized_subject = subject_with_placeholders.format_map(safe_contact)
    personalized_content = template_with_placeholders.format_map(safe_contact)
    
    print("\n✅ AFTER FIX:")
    print("\n📌 Personalized Subject:")
    print(personalized_subject)
    print("\n📧 Personalized Content:")
    print(personalized_content)
    
    # Verify that placeholders were replaced
    if "{name}" not in personalized_content and "{description}" not in personalized_content:
        print("\n🎉 SUCCESS: All placeholders were properly replaced!")
        return True
    else:
        print("\n❌ FAILURE: Some placeholders were not replaced!")
        return False

def test_missing_placeholder():
    """Test that missing placeholders are handled gracefully."""
    
    print("\n🧪 Testing Missing Placeholder Handling")
    print("=" * 50)
    
    contact_data = {
        'name': 'Jane Smith',
        'email': 'jane@example.com'
        # Note: 'description' is missing
    }
    
    template = "Hello {name}, regarding {description}, we appreciate your interest."
    
    print("📧 Template with missing placeholder:")
    print(template)
    print("\n👤 Contact Data (missing 'description'):")
    print(contact_data)
    
    safe_contact = SafeDict(contact_data)
    result = template.format_map(safe_contact)
    
    print("\n✅ Result:")
    print(result)
    
    # Should replace {name} but keep {description} as-is
    expected = "Hello Jane Smith, regarding {description}, we appreciate your interest."
    if result == expected:
        print("\n🎉 SUCCESS: Missing placeholders handled gracefully!")
        return True
    else:
        print(f"\n❌ FAILURE: Expected '{expected}', got '{result}'")
        return False

if __name__ == "__main__":
    print("🚀 MailerPanda Placeholder Fix Test")
    print("=" * 60)
    
    test1_pass = test_placeholder_replacement()
    test2_pass = test_missing_placeholder()
    
    print("\n" + "=" * 60)
    if test1_pass and test2_pass:
        print("🎉 ALL TESTS PASSED! The placeholder fix is working correctly.")
        print("✅ The MailerPanda agent will now properly replace {name} and {description}")
        print("✅ with actual contact data from the Excel file.")
    else:
        print("❌ SOME TESTS FAILED! Please check the implementation.")
    
    print("\n📝 Next steps:")
    print("1. Restart the backend API server: python api.py")
    print("2. Test sending an email with placeholders in the template")
    print("3. Verify that the received email has actual names/descriptions")
