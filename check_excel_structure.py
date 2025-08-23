#!/usr/bin/env python3
"""
Check the Excel file structure before running the approval workflow test
"""

import pandas as pd
from pathlib import Path

def check_excel_file():
    """Check if the Excel file has the correct structure."""
    
    excel_path = Path("hushh_mcp/agents/mailerpanda/email_list_with_descriptions.xlsx")
    
    print("📊 Checking Excel File Structure")
    print("=" * 40)
    
    if not excel_path.exists():
        print(f"❌ Excel file not found at: {excel_path}")
        return False
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        
        print(f"📁 File: {excel_path}")
        print(f"📏 Rows: {len(df)}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Check required columns
        required_columns = ['email']
        optional_columns = ['name', 'description', 'first_name', 'last_name']
        
        print(f"\n🔍 Column Analysis:")
        
        # Check for email column
        email_found = False
        for col in df.columns:
            if 'email' in col.lower():
                email_found = True
                print(f"✅ Email column found: '{col}'")
                break
        
        if not email_found:
            print(f"❌ No email column found!")
            return False
        
        # Check for description column (key for personalization)
        description_found = False
        description_col = None
        for col in df.columns:
            if 'description' in col.lower():
                description_found = True
                description_col = col
                print(f"✅ Description column found: '{col}' (PERSONALIZATION ENABLED)")
                break
        
        if not description_found:
            print(f"⚠️  No description column found (basic emails only)")
        
        # Check for name columns
        name_cols = []
        for col in df.columns:
            if any(name_part in col.lower() for name_part in ['name', 'first', 'last']):
                name_cols.append(col)
        
        if name_cols:
            print(f"✅ Name columns found: {name_cols}")
        else:
            print(f"⚠️  No name columns found")
        
        # Show data preview
        print(f"\n📋 Data Preview:")
        print(df.head(3).to_string(index=False, max_cols=5))
        
        if description_found:
            print(f"\n🎯 Description Samples:")
            descriptions = df[description_col].dropna().head(3)
            for i, desc in enumerate(descriptions, 1):
                print(f"  {i}. {str(desc)[:100]}...")
        
        print(f"\n✅ Excel file structure looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False

if __name__ == "__main__":
    check_excel_file()
