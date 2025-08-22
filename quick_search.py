#!/usr/bin/env python3
"""
Quick Research Search
====================

Simple one-shot research paper search tool.
Usage: python quick_search.py "your research query"
"""

import sys
import json
import urllib.request
import urllib.parse

def search_and_display(query, max_results=5):
    """Search and display papers for a query."""
    print(f"🔍 Searching ArXiv for: '{query}'")
    print("-" * 60)
    
    try:
        import requests
        import feedparser
        
        # ArXiv API call
        base_url = "http://export.arxiv.org/api/query?"
        search_query = f"search_query=all:{query}"
        params = f"{search_query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
        
        response = requests.get(f"{base_url}{params}", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return
        
        feed = feedparser.parse(response.content)
        papers = feed.entries
        
        if not papers:
            print("❌ No papers found. Try different keywords.")
            return
        
        print(f"✅ Found {len(papers)} papers\n")
        
        for i, entry in enumerate(papers, 1):
            print(f"📄 {i}. {entry.title.strip()}")
            
            # Authors
            authors = []
            if hasattr(entry, 'authors'):
                authors = [author.name for author in entry.authors[:3]]
            elif hasattr(entry, 'author'):
                authors = [entry.author]
            
            if authors:
                print(f"   👥 {', '.join(authors)}")
            
            # Details
            arxiv_id = entry.id.split('/')[-1] if entry.id else 'N/A'
            published = getattr(entry, 'published', 'N/A')[:10]
            print(f"   📋 ID: {arxiv_id} | Published: {published}")
            
            # PDF URL
            for link in entry.links:
                if link.type == 'application/pdf':
                    print(f"   🔗 PDF: {link.href}")
                    break
            
            # Abstract preview
            abstract = entry.summary.replace('\n', ' ').strip()
            if abstract:
                preview = abstract[:150] + "..." if len(abstract) > 150 else abstract
                print(f"   📝 {preview}")
            
            print()
        
    except ImportError:
        print("❌ Missing dependencies. Installing...")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', 'feedparser'])
        print("✅ Installed. Please run again.")
    except Exception as e:
        print(f"❌ Search failed: {e}")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("🔬 Quick Research Search")
        print("=" * 40)
        print("Usage:")
        print(f"  python {sys.argv[0]} \"your research query\"")
        print("\nExamples:")
        print(f"  python {sys.argv[0]} \"machine learning\"")
        print(f"  python {sys.argv[0]} \"quantum computing\"")
        print(f"  python {sys.argv[0]} \"deep learning computer vision\"")
        return
    
    query = ' '.join(sys.argv[1:])
    search_and_display(query)

if __name__ == "__main__":
    main()
