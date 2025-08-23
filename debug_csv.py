import base64

# The same test data from our API call
csv_base64 = "bmFtZSxlbWFpbCxkZXNjcmlwdGlvbgpKb2huIERvZSxqb2huQHRlc3QuY29tLFRlc3QgdXNlciBmb3IgZGVtbwpKYW5lIFNtaXRoLGphbmVAdGVzdC5jb20sQW5vdGhlciB0ZXN0IHVzZXI="

# Decode and check content
file_data = base64.b64decode(csv_base64)
file_content = file_data.decode('utf-8', errors='ignore')

print("Decoded content:")
print(repr(file_content))
print("\nActual content:")
print(file_content)

# Check our detection logic
is_csv = ',' in file_content and '\n' in file_content and not file_content.startswith('PK')
print(f"\nCSV detection result: {is_csv}")
print(f"Has comma: {',' in file_content}")
print(f"Has newline: {chr(10) in file_content}")
print(f"Starts with PK: {file_content.startswith('PK')}")
