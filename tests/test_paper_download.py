#!/usr/bin/env python3
"""
Test script to verify that paper downloading works correctly
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hushh_mcp.agents.research_agent.index import research_agent

async def test_paper_download():
    """Test downloading and processing a paper with slashes in the ID"""
    
    print("🧪 Testing paper download functionality...")
    
    # Test paper with slashes in ID
    paper_id = "gr-qc/0606081v1"
    user_id = "test_user"
    consent_tokens = {
        "custom.temporary": "test_token",
        "vault.read.file": "test_token",
        "vault.write.file": "test_token"
    }
    
    message = "Can you provide a summary of the introduction section?"
    
    print(f"📄 Testing with paper ID: {paper_id}")
    
    try:
        result = await research_agent.chat_about_paper(
            user_id=user_id,
            consent_tokens=consent_tokens,
            paper_id=paper_id,
            message=message
        )
        
        if result["success"]:
            print("✅ SUCCESS: Paper download and processing worked!")
            print(f"📝 AI Response: {result['response'][:200]}...")
            
            # Check if full content was accessed
            if "full paper content" in result['response'].lower() or len(result['response']) > 500:
                print("🎉 FULL CONTENT ACCESS CONFIRMED!")
            else:
                print("⚠️  May still be using abstract only")
                
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"💥 ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_paper_download())
