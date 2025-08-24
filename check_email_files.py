#!/usr/bin/env python3
"""
Check the contents of the email list files to debug the placeholder issue.
"""

import pandas as pd
import os

def check_email_files():
    """Check the structure and content of email list files."""
    
    print("🔍 Checking Email List Files")
    print("=" * 50)
    
    base_path = r"c:\Users\Asus\Desktop\Pda_mailer\hushh_mcp\agents\mailerpanda"
    
    files_to_check = [
        "email_list.xlsx",
        "email_list_with_descriptions.xlsx"
    ]
    
    for filename in files_to_check:
        filepath = os.path.join(base_path, filename)
        
        print(f"\n📂 Checking: {filename}")
        print("-" * 40)
        
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            continue
            
        try:
            df = pd.read_excel(filepath)
            print(f"✅ File loaded successfully")
            print(f"📊 Rows: {len(df)}")
            print(f"📋 Columns: {list(df.columns)}")
            print(f"\n📝 First 3 rows:")
            print(df.head(3).to_string())
            
            # Check for placeholders we care about
            if 'name' in df.columns:
                print(f"\n👤 Sample names: {df['name'].head(3).tolist()}")
            if 'description' in df.columns:
                print(f"\n📝 Sample descriptions: {df['description'].head(3).tolist()}")
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    check_email_files()
