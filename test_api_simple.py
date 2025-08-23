import base64
import requests
import json

# Read the Excel file we just created
with open('test_proper.xlsx', 'rb') as f:
    excel_data = base64.b64encode(f.read()).decode('utf-8')

url = 'http://127.0.0.1:8001/agents/mailerpanda/mass-email'
payload = {
    'user_id': 'test_proper_excel',
    'user_input': 'Send personalized emails about our development platform',
    'consent_tokens': {
        'vault.read.email': 'test_token_vault_read_email',
        'vault.write.email': 'test_token_vault_write_email',
        'vault.read.file': 'test_token_vault_read_file',
        'vault.write.file': 'test_token_vault_write_file',
        'custom.temporary': 'test_token_custom_temporary'
    },
    'excel_file_data': excel_data,
    'use_context_personalization': True,
    'mode': 'interactive'
}

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f'API Status: {response.status_code}')
    result = response.json()
    print(f'Response status: {result.get("status")}')
    print(f'Campaign ID: {result.get("campaign_id")}')
    print(f'Context enabled: {result.get("context_personalization_enabled")}')
    if result.get("errors"):
        print(f'Errors: {result.get("errors")}')
    else:
        print('Success: No errors reported')
    
    # Print the full response for debugging
    print(f'\nFull response:')
    print(json.dumps(result, indent=2))
        
except Exception as e:
    print(f'Error: {e}')
