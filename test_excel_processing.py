#!/usr/bin/env python3
"""
Test to specifically check the Excel processing part.
"""

import base64
import tempfile
import pandas as pd
import os

def test_excel_processing():
    """Test if Excel processing works correctly."""
    print("📊 Testing Excel Processing")
    print("=" * 40)
    
    # Create test Excel file
    data = {
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'Email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
        'Description': ['Test user 1', 'Test user 2', 'Test user 3']
    }
    df = pd.DataFrame(data)
    
    # Create temporary Excel file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        excel_path = tmp_file.name
    
    print(f"✅ Created test Excel file: {excel_path}")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    
    # Read it back to verify
    df_read = pd.read_excel(excel_path)
    print(f"✅ Read back Excel file:")
    print(f"   Rows: {len(df_read)}")
    print(f"   Columns: {list(df_read.columns)}")
    print(f"   Sample data:")
    print(df_read.head())
    
    # Encode to base64 like the API does
    with open(excel_path, 'rb') as f:
        file_data = base64.b64encode(f.read()).decode('utf-8')
    
    print(f"✅ Base64 encoded length: {len(file_data)}")
    print(f"   First 100 chars: {file_data[:100]}...")
    
    # Test decoding
    decoded_data = base64.b64decode(file_data)
    with tempfile.NamedTemporaryFile(delete=False, suffix='_decoded.xlsx') as tmp_file:
        tmp_file.write(decoded_data)
        decoded_path = tmp_file.name
    
    # Read decoded file
    df_decoded = pd.read_excel(decoded_path)
    print(f"✅ Decoded Excel file:")
    print(f"   Rows: {len(df_decoded)}")
    print(f"   Columns: {list(df_decoded.columns)}")
    
    # Cleanup
    os.unlink(excel_path)
    os.unlink(decoded_path)
    
    return file_data

if __name__ == "__main__":
    excel_data = test_excel_processing()
    print(f"\n📊 Excel data ready for API: {len(excel_data)} characters")
