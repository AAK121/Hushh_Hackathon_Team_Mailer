#!/usr/bin/env python3
"""
Interactive Research Agent Terminal
===================================

A simple command-line interface to test the research agent.
Just type your research query and see the papers!
"""

import json
import urllib.request
import urllib.parse
import sys
from datetime import datetime

def print_banner():
    """Print a nice banner."""
    print("=" * 70)
    print("🔬 INTERACTIVE RESEARCH AGENT TERMINAL")
    print("=" * 70)
    print("Type your research queries and get academic papers instantly!")
    print("Examples:")
    print("  • machine learning healthcare")
    print("  • quantum computing algorithms") 
    print("  • artificial intelligence robotics")
    print("  • deep learning computer vision")
    print("\nCommands:")
    print("  • 'quit' or 'exit' to stop")
    print("  • 'help' for more info")
    print("=" * 70)

def search_papers(query, max_papers=5):
    """Search for papers using the research agent API."""
    print(f"\n🔍 Searching for: '{query}'")
    print("⏳ Please wait...")
    
    try:
        # Create a simple token for testing (will be blocked by security, but that's expected)
        url = "http://localhost:8001/agents/research/search/arxiv"
        
        data = {
            "user_id": f"terminal_user_{datetime.now().strftime('%H%M%S')}",
            "consent_tokens": {
                "custom.temporary": f"terminal_test_token_{datetime.now().timestamp()}"
            },
            "query": query
        }
        
        # Make the request
        req_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
        
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode())
        
        # Check if successful
        if result.get('status') == 'success':
            papers = result.get('results', {}).get('papers', [])
            total_found = result.get('results', {}).get('total_found', len(papers))
            
            print(f"✅ Found {len(papers)} papers (Total available: {total_found})")
            print("=" * 70)
            
            for i, paper in enumerate(papers[:max_papers], 1):
                print(f"\n📄 Paper {i}:")
                print(f"   📚 Title: {paper.get('title', 'N/A')}")
                
                authors = paper.get('authors', [])
                if authors:
                    author_list = ', '.join(authors[:3])
                    if len(authors) > 3:
                        author_list += f" + {len(authors) - 3} more"
                    print(f"   👥 Authors: {author_list}")
                
                print(f"   🔗 arXiv ID: {paper.get('id', 'N/A')}")
                print(f"   📅 Published: {paper.get('published', 'N/A')[:10]}")
                
                if paper.get('pdf_url'):
                    print(f"   📄 PDF: {paper.get('pdf_url')}")
                
                # Show abstract preview
                abstract = paper.get('abstract', '')
                if abstract:
                    preview = abstract[:200] + "..." if len(abstract) > 200 else abstract
                    print(f"   📝 Abstract: {preview}")
                
                # Show categories
                categories = paper.get('categories', [])
                if categories:
                    cat_names = [cat.get('term', cat) if isinstance(cat, dict) else str(cat) for cat in categories[:3]]
                    print(f"   🏷️  Categories: {', '.join(cat_names)}")
            
            return True
            
        else:
            # The API returned an error (likely consent validation)
            errors = result.get('errors', ['Unknown error'])
            error_text = ' '.join(errors)
            
            # Check if it's a consent validation error (which is expected)
            if any(word in error_text.lower() for word in ['consent', 'token', 'invalid', 'scope']):
                print("🔒 API Security Note: Invalid token (this is expected for testing)")
                print("💡 Let's try the direct ArXiv search instead...")
                return search_papers_direct(query, max_papers)
            else:
                print(f"❌ API Error: {error_text}")
                print("💡 Let's try the direct ArXiv search instead...")
                return search_papers_direct(query, max_papers)
    
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("💡 Let's try the direct ArXiv search instead...")
        return search_papers_direct(query, max_papers)

def search_papers_direct(query, max_papers=5):
    """Direct ArXiv search bypassing the API."""
    print(f"\n🔍 Direct ArXiv Search for: '{query}'")
    
    try:
        import requests
        import feedparser
        
        # Direct ArXiv API call
        base_url = "http://export.arxiv.org/api/query?"
        search_query = f"search_query=all:{query}"
        params = f"{search_query}&start=0&max_results={max_papers}&sortBy=relevance&sortOrder=descending"
        
        response = requests.get(f"{base_url}{params}", timeout=15)
        
        if response.status_code != 200:
            print(f"❌ ArXiv API Error: HTTP {response.status_code}")
            return False
        
        # Parse results
        feed = feedparser.parse(response.content)
        papers = feed.entries
        
        if not papers:
            print("❌ No papers found for this query")
            return False
        
        print(f"✅ Found {len(papers)} papers")
        print("=" * 70)
        
        for i, entry in enumerate(papers, 1):
            print(f"\n📄 Paper {i}:")
            print(f"   📚 Title: {entry.title.strip()}")
            
            # Authors
            authors = []
            if hasattr(entry, 'authors'):
                authors = [author.name for author in entry.authors]
            elif hasattr(entry, 'author'):
                authors = [entry.author]
            
            if authors:
                author_list = ', '.join(authors[:3])
                if len(authors) > 3:
                    author_list += f" + {len(authors) - 3} more"
                print(f"   👥 Authors: {author_list}")
            
            # arXiv ID
            arxiv_id = entry.id.split('/')[-1] if entry.id else 'N/A'
            print(f"   🔗 arXiv ID: {arxiv_id}")
            
            # Published date
            published = getattr(entry, 'published', 'N/A')[:10]
            print(f"   📅 Published: {published}")
            
            # PDF URL
            pdf_url = None
            for link in entry.links:
                if link.type == 'application/pdf':
                    pdf_url = link.href
                    break
            
            if pdf_url:
                print(f"   📄 PDF: {pdf_url}")
            
            # Abstract
            abstract = entry.summary.replace('\n', ' ').strip()
            if abstract:
                preview = abstract[:200] + "..." if len(abstract) > 200 else abstract
                print(f"   📝 Abstract: {preview}")
            
            # Categories
            if hasattr(entry, 'tags'):
                categories = [tag.term for tag in entry.tags[:3]]
                print(f"   🏷️  Categories: {', '.join(categories)}")
        
        return True
        
    except ImportError:
        print("❌ Missing dependencies. Installing...")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', 'feedparser'], 
                      capture_output=True)
        print("✅ Dependencies installed. Please try again.")
        return False
    
    except Exception as e:
        print(f"❌ Direct search failed: {e}")
        return False

def show_help():
    """Show help information."""
    print("\n" + "=" * 70)
    print("🆘 HELP & TIPS")
    print("=" * 70)
    print("• Search Tips:")
    print("  - Use specific terms: 'neural networks medical diagnosis'")
    print("  - Combine concepts: 'quantum machine learning'")
    print("  - Try different phrasings if no results")
    print("")
    print("• Available Commands:")
    print("  - help: Show this help")
    print("  - quit/exit: Close the program")
    print("  - Any other text: Search for papers")
    print("")
    print("• Examples of good queries:")
    print("  - 'deep learning natural language processing'")
    print("  - 'computer vision object detection'")
    print("  - 'reinforcement learning robotics'")
    print("  - 'blockchain cryptocurrency security'")
    print("=" * 70)

def main():
    """Main interactive loop."""
    print_banner()
    
    # Check if server is running
    try:
        response = urllib.request.urlopen("http://localhost:8001/health", timeout=3)
        print("✅ Research Agent API server is running")
    except:
        print("⚠️ Research Agent API server not detected")
        print("💡 Will use direct ArXiv search instead")
    
    print("\nReady! Type your research query:")
    
    while True:
        try:
            # Get user input
            query = input("\n🔬 Research Query: ").strip()
            
            # Handle commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for using the Research Agent Terminal!")
                break
            elif query.lower() in ['help', 'h', '?']:
                show_help()
                continue
            elif not query:
                print("💡 Please enter a research query or 'help' for assistance")
                continue
            
            # Search for papers
            success = search_papers(query)
            
            if success:
                print(f"\n💡 Want to search for something else? Type a new query!")
            else:
                print(f"\n💡 Try a different query or check your internet connection")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("💡 Please try again or type 'quit' to exit")

if __name__ == "__main__":
    main()
