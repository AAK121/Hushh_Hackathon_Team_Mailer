import requests
import json
import base64

# Create a simple test CSV
csv_content = """name,email,description
John Doe,john@test.com,Test user for demo
Jane Smith,jane@test.com,Another test user"""

# Convert to base64
csv_base64 = base64.b64encode(csv_content.encode()).decode()

# Test payload matching our frontend
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

print("Testing MailerPanda API directly...")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        "http://127.0.0.1:8001/agents/mailerpanda/mass-email",
        json=payload,
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Campaign ID: {result.get('campaign_id')}")
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"Error Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
