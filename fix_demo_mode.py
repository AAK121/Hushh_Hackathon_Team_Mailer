#!/usr/bin/env python3
"""
Script to update all test files to use 'interactive' instead of 'demo' mode
"""

import os
import re
import glob

def fix_demo_mode_in_files():
    """Fix demo mode references in test files."""
    print("🔧 Fixing demo mode references in test files...")
    
    # Find all test files
    test_files = glob.glob("test_*.py")
    
    files_updated = []
    
    for file_path in test_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace various patterns of demo mode
            patterns = [
                (r'"mode":\s*"demo"', '"mode": "interactive"'),
                (r"'mode':\s*'demo'", "'mode': 'interactive'"),
                (r'mode\s*=\s*"demo"', 'mode="interactive"'),
                (r"mode\s*=\s*'demo'", "mode='interactive'"),
                (r'"demo"(\s*#.*Use demo mode)', '"interactive"\\1'),
                (r"'demo'(\s*#.*Use demo mode)", "'interactive'\\1")
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            # Only write if content changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_updated.append(file_path)
                print(f"  ✅ Updated: {file_path}")
        
        except Exception as e:
            print(f"  ⚠️  Error updating {file_path}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"  Files checked: {len(test_files)}")
    print(f"  Files updated: {len(files_updated)}")
    
    if files_updated:
        print(f"  Updated files:")
        for file in files_updated:
            print(f"    - {file}")
    
    return files_updated

if __name__ == "__main__":
    print("🚀 Demo Mode Fix Script")
    print("=" * 50)
    
    updated_files = fix_demo_mode_in_files()
    
    if updated_files:
        print(f"\n✅ Successfully updated {len(updated_files)} test files")
        print("🎯 All test files now use 'interactive' mode instead of 'demo'")
    else:
        print(f"\n✅ No files needed updating")
    
    print("\n💡 Test files are now compatible with the updated MailerPanda agent")
