import requests
import json
import base64

# Test CSV data (same as before)
csv_data = "name,email,description\nJohn Doe,john@test.com,Test user for demo\nJane Smith,jane@test.com,Another test user"
csv_base64 = base64.b64encode(csv_data.encode()).decode()

url = "http://localhost:8001/agents/mailerpanda/mass-email"
payload = {
    "user_id": "frontend_user_123",
    "user_input": "Send a test email to our users", 
    "excel_file_data": csv_base64,
    "excel_file_name": "test.csv",
    "mode": "interactive",
    "consent_tokens": {
        "vault.read.email": "demo_token_123",
        "vault.write.email": "demo_token_456", 
        "vault.read.file": "demo_token_789",
        "vault.write.file": "demo_token_101",
        "custom.temporary": "demo_token_202"
    }
}

try:
    print("Testing MailerPanda API with CSV file...")
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Campaign ID: {result.get('campaign_id')}")
        print("Excel Analysis:")
        if 'excel_analysis' in result:
            for key, value in result['excel_analysis'].items():
                print(f"  {key}: {value}")
    else:
        print(f"Error Response: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")
