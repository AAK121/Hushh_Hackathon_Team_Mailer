#!/usr/bin/env python3
"""
Simple ArXiv Test - Global Python Environment
============================================

This script tests ArXiv paper search functionality using global Python.
It will automatically install required dependencies if missing.
"""

import sys
import subprocess
import json

def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def ensure_dependencies():
    """Ensure required packages are installed."""
    required_packages = ["requests", "feedparser"]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"📦 Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
                return False
    return True

def search_arxiv_simple(query, max_results=5):
    """Search ArXiv for papers using simple API call."""
    try:
        import requests
        import feedparser
        
        print(f"🔍 Searching ArXiv for: '{query}'")
        print("-" * 50)
        
        # ArXiv API URL
        base_url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        # Make request
        response = requests.get(base_url, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ ArXiv API error: {response.status_code}")
            return []
        
        # Parse results
        feed = feedparser.parse(response.content)
        papers = []
        
        print(f"✅ Found {len(feed.entries)} papers")
        print("=" * 60)
        
        for i, entry in enumerate(feed.entries, 1):
            # Extract paper info
            arxiv_id = entry.id.split('/')[-1] if entry.id else 'Unknown'
            title = entry.title.strip() if hasattr(entry, 'title') else 'No title'
            abstract = entry.summary.replace('\n', ' ').strip() if hasattr(entry, 'summary') else 'No abstract'
            published = entry.published[:10] if hasattr(entry, 'published') else 'Unknown'
            
            # Extract authors
            authors = []
            if hasattr(entry, 'authors'):
                authors = [author.name for author in entry.authors]
            elif hasattr(entry, 'author'):
                authors = [entry.author]
            
            # Extract PDF URL
            pdf_url = ""
            if hasattr(entry, 'links'):
                for link in entry.links:
                    if hasattr(link, 'type') and link.type == 'application/pdf':
                        pdf_url = link.href
                        break
            
            paper = {
                'id': arxiv_id,
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'published': published,
                'pdf_url': pdf_url
            }
            papers.append(paper)
            
            # Display paper
            print(f"📄 Paper {i}: {title}")
            print(f"   📝 ID: {arxiv_id}")
            print(f"   👥 Authors: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
            print(f"   📅 Published: {published}")
            print(f"   🔗 PDF: {pdf_url}")
            
            # Show abstract preview
            if len(abstract) > 200:
                preview = abstract[:200] + "..."
            else:
                preview = abstract
            print(f"   📄 Abstract: {preview}")
            print()
        
        return papers
        
    except Exception as e:
        print(f"❌ Error searching ArXiv: {e}")
        return []

def test_backend_connectivity():
    """Test if the backend server is running."""
    try:
        import urllib.request
        import json
        
        print("🔌 Testing Backend Server...")
        print("-" * 40)
        
        # Test health endpoint
        response = urllib.request.urlopen("http://localhost:8001/health", timeout=5)
        if response.status == 200:
            data = json.loads(response.read().decode())
            print("✅ Backend server is running!")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Backend returned: {response.status}")
            return False
            
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        print("💡 Start server with: python api.py")
        return False

def main():
    """Run the complete test suite."""
    print("🧪 Research Agent Testing - Global Python Environment")
    print("=" * 70)
    
    # Step 1: Install dependencies
    print("📦 Checking Dependencies...")
    if not ensure_dependencies():
        print("❌ Dependency installation failed")
        return
    
    print("\n" + "=" * 70)
    
    # Step 2: Test ArXiv search directly
    print("🔍 Testing ArXiv Search Functionality")
    print("=" * 70)
    
    test_queries = [
        "machine learning healthcare",
        "artificial intelligence",
        "quantum computing"
    ]
    
    total_papers = 0
    for query in test_queries:
        papers = search_arxiv_simple(query, max_results=3)
        total_papers += len(papers)
        print(f"✅ Query '{query}': {len(papers)} papers found\n")
    
    # Step 3: Test backend connectivity
    print("=" * 70)
    backend_running = test_backend_connectivity()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"🔍 ArXiv Search: {'✅ Working' if total_papers > 0 else '❌ Failed'}")
    print(f"   Total papers retrieved: {total_papers}")
    print(f"🖥️  Backend Server: {'✅ Running' if backend_running else '❌ Not Running'}")
    
    if total_papers > 0:
        print("\n🎯 SUCCESS! Core functionality is working:")
        print("   ✅ Can connect to ArXiv API")
        print("   ✅ Can parse paper metadata")
        print("   ✅ Can extract titles, authors, abstracts")
        print("   ✅ Ready for integration!")
        
        if backend_running:
            print("   ✅ Backend server is operational")
            print(f"   🌐 Visit: http://localhost:8001/docs for API documentation")
        else:
            print("   💡 To test full API: Run 'python api.py' in separate window")
    else:
        print("\n❌ ArXiv search failed - check internet connection")
    
    print(f"\n📖 For detailed testing guide, see: BACKEND_TESTING_GUIDE.md")

if __name__ == "__main__":
    main()
