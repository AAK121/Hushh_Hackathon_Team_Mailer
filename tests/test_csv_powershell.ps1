$csv_data = "name,email,description`nJohn Doe,john@test.com,Test user for demo`nJane Smith,jane@test.com,Another test user"
$csv_base64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($csv_data))

$payload = @{
    user_id = "frontend_user_123"
    user_input = "Send a test email to our users"
    excel_file_data = $csv_base64
    excel_file_name = "test.csv"
    mode = "demo"
    consent_tokens = @{
        "vault.read.email" = "demo_token_123"
        "vault.write.email" = "demo_token_456"
        "vault.read.file" = "demo_token_789"
        "vault.write.file" = "demo_token_101"
        "custom.temporary" = "demo_token_202"
    }
} | ConvertTo-Json -Depth 3

Write-Host "Testing MailerPanda API with CSV file..."
Write-Host "CSV Data: $csv_data"

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/agents/mailerpanda/mass-email" -Method POST -Body $payload -ContentType "application/json"
    Write-Host "Success! Campaign ID: $($response.campaign_id)"
    Write-Host "Excel Analysis:"
    $response.excel_analysis | Format-List
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host "Response: $($_.Exception.Response)"
}
