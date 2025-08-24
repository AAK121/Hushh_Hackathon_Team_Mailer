#!/usr/bin/env python3
"""
Script to fix the chronological order of AI Responses notes.
This will reorder existing notes so the first conversation appears at the top.
"""

import requests
import json
import re
from datetime import datetime

def fix_ai_responses_order():
    """Fix the chronological order of AI Responses notes."""
    
    print("🔄 Fixing AI Responses Notes Chronological Order...")
    print("=" * 50)
    
    try:
        # Get current AI Responses notes
        url = "http://localhost:8001/research/notes/AI Responses"
        response = requests.get(url)
        
        if response.status_code == 200:
            current_notes = response.text
            print(f"📄 Loaded current notes ({len(current_notes)} characters)")
            
            # Split notes by the separator "---"
            sections = current_notes.split('---')
            
            # Filter out empty sections and the header
            conversation_sections = []
            header_section = ""
            
            for section in sections:
                section = section.strip()
                if section and '##' in section:
                    # Check if this is the header or a conversation
                    if 'AI Responses' in section and 'automatically stores' in section:
                        header_section = section
                    else:
                        conversation_sections.append(section)
            
            print(f"🔍 Found {len(conversation_sections)} conversation sections")
            
            if conversation_sections:
                # Parse timestamps and sort chronologically
                def extract_timestamp(section):
                    # Look for timestamp pattern like "8/25/2025, 12:45:49 AM"
                    timestamp_match = re.search(r'## (\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2} [AP]M)', section)
                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1)
                        try:
                            # Parse the timestamp
                            return datetime.strptime(timestamp_str, "%m/%d/%Y, %I:%M:%S %p")
                        except:
                            return datetime.min
                    return datetime.min
                
                # Sort sections by timestamp (oldest first)
                sorted_sections = sorted(conversation_sections, key=extract_timestamp)
                
                # Rebuild the notes file in chronological order
                if header_section:
                    reordered_notes = header_section + "\n\n---\n\n"
                else:
                    reordered_notes = "# AI Responses\n\nThis file automatically stores all AI responses from your research conversations.\n\n---\n\n"
                
                # Add conversations in chronological order
                for section in sorted_sections:
                    reordered_notes += section + "\n\n---\n\n"
                
                # Update the notes via API
                update_url = "http://localhost:8001/research/notes/AI Responses"
                update_response = requests.put(update_url, json={"content": reordered_notes})
                
                if update_response.status_code == 200:
                    print("✅ Successfully reordered AI Responses notes!")
                    print("📅 Conversations are now in chronological order (first to last)")
                    print(f"📝 Total conversations: {len(sorted_sections)}")
                    
                    # Show the first few timestamps for verification
                    print("\n🕐 First few conversation timestamps:")
                    for i, section in enumerate(sorted_sections[:3]):
                        timestamp_match = re.search(r'## (\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2} [AP]M)', section)
                        if timestamp_match:
                            print(f"  {i+1}. {timestamp_match.group(1)}")
                    
                    return True
                else:
                    print(f"❌ Failed to update notes: {update_response.status_code}")
                    return False
            else:
                print("📝 No conversation sections found to reorder")
                return True
                
        else:
            print(f"❌ Failed to load notes: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting AI Responses Notes Reordering...")
    print("This script will:")
    print("1. Load the current AI Responses notes")
    print("2. Parse individual conversation sections") 
    print("3. Sort them by timestamp (oldest first)")
    print("4. Save the reordered notes back")
    print()
    
    success = fix_ai_responses_order()
    
    if success:
        print("\n🎯 Reordering complete!")
        print("New conversations will now be added to the end in chronological order.")
    else:
        print("\n💔 Reordering failed. Please check the backend server.")
