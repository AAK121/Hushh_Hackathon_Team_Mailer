#!/usr/bin/env python3
"""
Simple framework test for HushMCP components.
"""

import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_hushh_framework():
    """Test basic HushMCP framework components."""
    
    print("Testing HushMCP Framework Components")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Constants
    try:
        from hushh_mcp.constants import ConsentScope
        print("1. ConsentScope import: OK")
        print(f"   Available scopes: {len(list(ConsentScope))}")
        test_results.append(True)
    except Exception as e:
        print(f"1. ConsentScope import: FAILED - {e}")
        test_results.append(False)
    
    # Test 2: Token operations
    try:
        from hushh_mcp.consent.token import issue_token, validate_token
        print("2. Token operations import: OK")
        test_results.append(True)
    except Exception as e:
        print(f"2. Token operations import: FAILED - {e}")
        test_results.append(False)
    
    # Test 3: Vault operations
    try:
        from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
        print("3. Vault operations import: OK")
        test_results.append(True)
    except Exception as e:
        print(f"3. Vault operations import: FAILED - {e}")
        test_results.append(False)
    
    # Test 4: Trust links
    try:
        from hushh_mcp.trust.link import create_trust_link, verify_trust_link
        print("4. Trust link operations import: OK")
        test_results.append(True)
    except Exception as e:
        print(f"4. Trust link operations import: FAILED - {e}")
        test_results.append(False)
    
    # Test 5: Configuration
    try:
        from hushh_mcp.config import SECRET_KEY, VAULT_ENCRYPTION_KEY
        if SECRET_KEY and VAULT_ENCRYPTION_KEY:
            print("5. Configuration: OK")
            test_results.append(True)
        else:
            print("5. Configuration: FAILED - Missing keys")
            test_results.append(False)
    except Exception as e:
        print(f"5. Configuration: FAILED - {e}")
        test_results.append(False)
    
    # Test 6: Operons
    try:
        from hushh_mcp.operons.verify_email import verify_email_operon
        print("6. Email verification operon: OK")
        test_results.append(True)
    except Exception as e:
        print(f"6. Email verification operon: FAILED - {e}")
        test_results.append(False)
    
    # Summary
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\nFramework Test Results: {passed}/{total} passed")
    
    return passed == total


if __name__ == "__main__":
    success = test_hushh_framework()
    sys.exit(0 if success else 1)
