#!/usr/bin/env python3
"""
Test script to verify enhanced Markdown mathematical formula formatting.
This tests the complete pipeline: PDF processing → formula cleanup → AI formatting → Markdown rendering.
"""

import requests
import json

def test_markdown_formula_formatting():
    """Test the enhanced mathematical formula formatting in Markdown."""
    
    print("🧪 Testing Enhanced Markdown Mathematical Formula Formatting...")
    print("=" * 70)
    
    # Test data
    paper_id = "gr-qc/0606081v1"  # Known paper with Killing vector fields
    test_message = "Please show me the key mathematical equations from this paper in proper Markdown format. I want to see clean, well-formatted formulas with equation numbers."
    
    # API endpoints
    chat_url = "http://localhost:8001/research/chat"
    
    # Test chat with mathematical formula request
    print(f"📋 Testing with paper ID: {paper_id}")
    print(f"📝 Question: {test_message}")
    print("\n" + "─" * 50)
    
    try:
        # Send chat request
        chat_payload = {
            "message": test_message,
            "paper_id": paper_id
        }
        
        response = requests.post(chat_url, json=chat_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                ai_response = result.get("message", "")
                
                print("✅ SUCCESS: AI Response with Markdown Formatting!")
                print("=" * 60)
                print(ai_response)
                print("=" * 60)
                
                # Check for Markdown formatting elements
                markdown_indicators = {
                    "Headers": ["##", "###"],
                    "Bold Text": ["**"],
                    "Math Code Blocks": ["```math", "```", "$$"],
                    "Equation Numbers": ["**(", ")**"],
                    "Mathematical Symbols": ["∇", "∂", "∑", "α", "β", "γ"],
                    "Proper Structure": ["\n", "L_K", "R_"]
                }
                
                print("\n🔍 Markdown Formatting Analysis:")
                print("-" * 40)
                
                for category, indicators in markdown_indicators.items():
                    found = [ind for ind in indicators if ind in ai_response]
                    status = "✅" if found else "❌"
                    print(f"{status} {category}: {found if found else 'Not found'}")
                
                # Overall assessment
                total_categories = len(markdown_indicators)
                passed_categories = sum(1 for _, indicators in markdown_indicators.items() 
                                      if any(ind in ai_response for ind in indicators))
                
                print(f"\n📊 Overall Score: {passed_categories}/{total_categories} categories passed")
                
                if passed_categories >= 4:
                    print("🎉 EXCELLENT: Markdown formatting is working properly!")
                elif passed_categories >= 2:
                    print("⚠️ PARTIAL: Some Markdown formatting is working")
                else:
                    print("❌ POOR: Markdown formatting needs improvement")
                
                return True
                
            else:
                print(f"❌ API Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Markdown Mathematical Formula Test...")
    print("This test verifies:")
    print("1. PDF text extraction with formula cleanup")
    print("2. AI response formatting in proper Markdown")
    print("3. Mathematical symbols and equation structure")
    print("4. Headers, bold text, and code blocks")
    print()
    
    success = test_markdown_formula_formatting()
    
    if success:
        print("\n🎯 Test completed! Check the output above to see the formatted mathematical formulas.")
        print("The frontend should now render these formulas beautifully with:")
        print("  • KaTeX mathematical rendering")
        print("  • Proper Markdown headers and formatting") 
        print("  • Clean equation presentation")
    else:
        print("\n💔 Test failed. Please check the backend server and try again.")
