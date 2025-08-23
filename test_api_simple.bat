@echo off
echo Testing MailerPanda API Personalization Features
echo ================================================

echo.
echo 1. Testing Agent Info Endpoint...
curl -s http://127.0.0.1:8000/agents | python -m json.tool

echo.
echo 2. Testing MailerPanda Agent Info Specifically...
curl -s "http://127.0.0.1:8000/agents" | python -c "
import sys, json
data = json.load(sys.stdin)
mailerpanda = data.get('agent_mailerpanda', {})
print('MailerPanda Agent Details:')
print(f'  Name: {mailerpanda.get(\"name\", \"N/A\")}')
print(f'  Version: {mailerpanda.get(\"version\", \"N/A\")}')
print(f'  Description: {mailerpanda.get(\"description\", \"N/A\")}')
features = mailerpanda.get('features', [])
if features:
    print('  Features:')
    for feature in features:
        indicator = '✨' if 'Personalization' in feature else '📌'
        print(f'    {indicator} {feature}')
"

echo.
echo 3. Testing MailerPanda Request Schema...
curl -s "http://127.0.0.1:8000/openapi.json" | python -c "
import sys, json
data = json.load(sys.stdin)
components = data.get('components', {})
schemas = components.get('schemas', {})
mailerpanda_request = schemas.get('MailerPandaRequest', {})
properties = mailerpanda_request.get('properties', {})

print('MailerPandaRequest Schema Properties:')
personalization_fields = [
    'enable_description_personalization',
    'excel_file_path', 
    'personalization_mode'
]

for field in personalization_fields:
    if field in properties:
        field_info = properties[field]
        print(f'  ✅ {field}: {field_info.get(\"type\", \"unknown\")} - {field_info.get(\"description\", \"no description\")}')
    else:
        print(f'  ❌ {field}: Missing')
"

echo.
echo Test completed! ✅
pause
