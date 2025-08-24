#!/usr/bin/env python3
"""
Test script to verify mathematical formula cleanup
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hushh_mcp.agents.research_agent.index import research_agent

async def test_formula_extraction():
    """Test formula extraction with the Killing vector fields paper"""
    
    print("🧪 Testing mathematical formula extraction...")
    
    # Test paper with mathematical formulas
    paper_id = "gr-qc/9811031v2"  # Killing vector fields paper
    user_id = "test_user"
    consent_tokens = {
        "custom.temporary": "test_token",
        "vault.read.file": "test_token",
        "vault.write.file": "test_token"
    }
    
    message = "Please list all the mathematical equations from this paper in proper format, with their equation numbers."
    
    print(f"📄 Testing with paper ID: {paper_id}")
    print("📋 Requesting properly formatted equations...")
    
    try:
        result = await research_agent.chat_about_paper(
            user_id=user_id,
            consent_tokens=consent_tokens,
            paper_id=paper_id,
            message=message
        )
        
        if result["success"]:
            print("✅ SUCCESS: Paper processed with formula cleanup!")
            print("📝 AI Response with cleaned formulas:")
            print("=" * 80)
            print(result['response'])
            print("=" * 80)
            
            # Check if mathematical symbols are properly formatted
            response = result['response']
            if any(symbol in response for symbol in ['∇', '∂', '∑', '∫', 'α', 'β', 'γ', 'δ']):
                print("🎉 MATHEMATICAL SYMBOLS PROPERLY FORMATTED!")
            else:
                print("⚠️  Mathematical symbols may still need improvement")
                
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"💥 ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_formula_extraction())
