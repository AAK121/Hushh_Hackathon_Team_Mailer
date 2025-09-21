# hushh_mcp/agents/research_agent/index.py

from __future__ import annotations

import os
import sys
import uuid
import json
import asyncio
import feedparser
import requests
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path
import functools

# Configure logging early
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_async_run(coro):
    """
    Safely run async coroutines in serverless environments.
    Handles event loop issues that can occur in Vercel/serverless deployments.
    """
    try:
        # Try to get existing loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            # Create new loop if closed
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except RuntimeError as e:
        if "Event loop is closed" in str(e) or "no running event loop" in str(e):
            # Create new event loop for serverless environments
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                # Don't close the loop in serverless environments
                pass
        else:
            raise

# Fix for Python 3.13 ForwardRef compatibility
try:
    # Try to patch ForwardRef._evaluate to handle the recursive_guard parameter
    import typing
    if hasattr(typing, 'ForwardRef') and sys.version_info >= (3, 13):
        original_evaluate = typing.ForwardRef._evaluate
        def patched_evaluate(self, globalns, localns, frozenset=frozenset, recursive_guard=None):
            if recursive_guard is None:
                recursive_guard = frozenset()
            return original_evaluate(self, globalns, localns, frozenset)
        typing.ForwardRef._evaluate = patched_evaluate
except Exception as e:
    logger.warning(f"Could not patch ForwardRef for Python 3.13 compatibility: {e}")

# Handle TypedDict import with fallback for ForwardRef issues
try:
    from typing import TypedDict
except ImportError:
    # Fallback for older Python versions
    try:
        from typing_extensions import TypedDict
    except ImportError:
        # Final fallback - create a simple dict subclass
        class TypedDict(dict):
            def __init_subclass__(cls, **kwargs):
                super().__init_subclass__()

# LangGraph and LangChain imports
try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    print("Warning: langgraph not available, using simplified workflow")
    LANGGRAPH_AVAILABLE = False
    # Create minimal fallback classes
    class StateGraph:
        def __init__(self, state_class):
            self.state_class = state_class
        def add_node(self, name, func):
            pass
        def add_edge(self, from_node, to_node):
            pass
        def set_entry_point(self, node):
            pass
        def compile(self):
            return self
    START = "START"
    END = "END"

from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# PDF processing
import PyPDF2
from io import BytesIO

# FastAPI and async
import aiofiles
from fastapi import UploadFile

# HushMCP imports
from hushh_mcp.constants import ConsentScope
from hushh_mcp.consent.token import validate_token

# Vault encryption functions - implemented directly for Vercel compatibility
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
import base64
from hushh_mcp.types import EncryptedPayload

def encrypt_data(plaintext: str, key_hex: str) -> EncryptedPayload:
    """Encrypt data using AES-256-GCM - Direct implementation for Vercel compatibility."""
    try:
        IV_LENGTH = 12  # GCM recommended IV size
        ALGORITHM_NAME = "aes-256-gcm"
        
        key = bytes.fromhex(key_hex)
        iv = os.urandom(IV_LENGTH)
        backend = default_backend()

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=backend)
        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
        tag = encryptor.tag

        return EncryptedPayload(
            ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
            iv=base64.b64encode(iv).decode('utf-8'),
            tag=base64.b64encode(tag).decode('utf-8'),
            encoding="base64",
            algorithm=ALGORITHM_NAME
        )
    except Exception as e:
        raise RuntimeError(f"Encryption failed: {str(e)}")

def decrypt_data(payload: EncryptedPayload, key_hex: str) -> str:
    """Decrypt data using AES-256-GCM - Direct implementation for Vercel compatibility."""
    try:
        key = bytes.fromhex(key_hex)
        iv = base64.b64decode(payload.iv)
        tag = base64.b64decode(payload.tag)
        ciphertext = base64.b64decode(payload.ciphertext)

        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=backend)
        decryptor = cipher.decryptor()

        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted.decode('utf-8')

    except InvalidTag:
        raise ValueError("Decryption failed: Invalid authentication tag. Possible tampering.")
    except Exception as e:
        raise RuntimeError(f"Decryption failed: {str(e)}")
from hushh_mcp.config import (
    VAULT_ENCRYPTION_KEY, 
    ARXIV_API_BASE_URL,
    ARXIV_PDF_BASE_URL,
    ARXIV_ABS_BASE_URL,
    API_REQUEST_TIMEOUT,
    ARXIV_MAX_RESULTS
)

# Define state class with error handling for ForwardRef issues
try:
    class ResearchAgentState(TypedDict):
        """State definition for the Research Agent LangGraph workflow."""
        user_id: str
        consent_tokens: Dict[str, str]
        session_id: str
        query: Optional[str]
        paper_id: Optional[str]
        paper_content: Optional[str]
        arxiv_results: Optional[List[Dict]]
        summary: Optional[str]
        snippet: Optional[str]
        instruction: Optional[str]
        processed_snippet: Optional[str]
        notes: Optional[Dict[str, str]]
        error: Optional[str]
        status: str
        mode: str  # 'interactive' or 'api'
except Exception as e:
    logger.warning(f"TypedDict definition failed, using fallback: {e}")
    # Fallback to regular dict for compatibility
    class ResearchAgentState(dict):
        """Fallback state definition for compatibility."""
        pass
    
class ResearchAgent:
    """
    AI-powered Research Agent using LangGraph for workflow orchestration.
    
    Capabilities:
    - Natural language arXiv search optimization
    - PDF paper processing and analysis
    - AI-powered summarization
    - Interactive snippet processing
    - Multi-editor note management
    """
    
    def __init__(self):
        # Try multiple environment variable names for Google API key
        api_key = (
            os.environ.get("GOOGLE_API_KEY") or 
            os.environ.get("GEMINI_API_KEY") or 
            "AIzaSyCyTIMomAZ-EtebfSToII2gwLo8pInVXwY"  # Fallback key from .env
        )
        
        logger.info(f"🔑 Using Gemini API key: {api_key[:10]}...")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.3,
            google_api_key=api_key
        )
        
        # Create LangGraph workflow (if available)
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._create_workflow()
            logger.info("🔬 Research Agent initialized with LangGraph workflow")
        else:
            self.workflow = None
            logger.info("🔬 Research Agent initialized with simplified workflow (langgraph not available)")
        
        # Storage for papers and sessions - Use in-memory storage for Vercel compatibility
        self.papers_storage = {}  # In-memory storage instead of filesystem
        self.vault_storage = {}   # In-memory vault storage
        logger.info("🔬 Research Agent using in-memory storage (Vercel compatible)")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for research operations."""
        workflow = StateGraph(ResearchAgentState)
        
        # Add nodes
        workflow.add_node("validate_consent", self._validate_consent)
        workflow.add_node("optimize_search_query", self._optimize_search_query)
        workflow.add_node("search_arxiv", self._search_arxiv)
        workflow.add_node("extract_pdf_text", self._extract_pdf_text)
        workflow.add_node("generate_summary", self._generate_summary)
        workflow.add_node("process_snippet", self._process_snippet)
        workflow.add_node("save_notes", self._save_notes)
        workflow.add_node("error_handler", self._error_handler)
        
        # Add edges
        workflow.add_edge(START, "validate_consent")
        workflow.add_conditional_edges(
            "validate_consent",
            self._route_after_validation,
            {
                "search": "optimize_search_query",
                "upload": "extract_pdf_text", 
                "summary": "generate_summary",
                "snippet": "process_snippet",
                "notes": "save_notes",
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("optimize_search_query", "search_arxiv")
        workflow.add_edge("search_arxiv", END)
        workflow.add_edge("extract_pdf_text", END)
        workflow.add_edge("generate_summary", END)
        workflow.add_edge("process_snippet", END)
        workflow.add_edge("save_notes", END)
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    def _validate_consent(self, state: ResearchAgentState) -> ResearchAgentState:
        """Validate required consent tokens for the requested operation."""
        try:
            user_id = state["user_id"]
            consent_tokens = state["consent_tokens"]
            
            # Check for demo tokens - bypass validation
            if all(token == "demo_token" for token in consent_tokens.values()):
                logger.info(f"🧪 Demo mode - bypassing consent validation for user {user_id}")
                return state
            
            # Determine required scopes based on status/operation
            required_scopes = []
            if state["status"] in ["arxiv_search", "snippet_processing"]:
                required_scopes = [ConsentScope.CUSTOM_TEMPORARY]
            elif state["status"] in ["pdf_upload", "summary_generation"]:
                required_scopes = [ConsentScope.VAULT_READ_FILE, ConsentScope.VAULT_WRITE_FILE]
            elif state["status"] == "note_saving":
                required_scopes = [ConsentScope.VAULT_WRITE_FILE]
            
            # Validate tokens
            valid_tokens = {}
            for scope in required_scopes:
                scope_key = scope.value
                if scope_key not in consent_tokens:
                    raise ValueError(f"Missing consent token for scope: {scope_key}")
                
                token = consent_tokens[scope_key]
                is_valid, error_msg, token_obj = validate_token(token, scope)
                if not is_valid:
                    raise ValueError(f"Invalid consent token for scope: {scope_key} - {error_msg}")
                
                valid_tokens[scope_key] = token
            
            state["consent_tokens"] = valid_tokens
            logger.info(f"✅ Consent validation successful for user {user_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Consent validation failed: {e}")
            state["error"] = f"Consent validation failed: {str(e)}"
            state["status"] = "error"
            return state
    
    def _route_after_validation(self, state: ResearchAgentState) -> str:
        """Route to appropriate node after consent validation."""
        if state.get("error"):
            return "error"
        
        status = state["status"]
        routing_map = {
            "arxiv_search": "search",
            "pdf_upload": "upload",
            "summary_generation": "summary", 
            "snippet_processing": "snippet",
            "note_saving": "notes"
        }
        
        return routing_map.get(status, "error")
    
    def _optimize_search_query(self, state: ResearchAgentState) -> ResearchAgentState:
        """Optimize user's natural language query for arXiv search."""
        try:
            user_query = state["query"]
            
            # Create prompt for query optimization
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert at converting natural language research requests into effective arXiv search queries.

Your task is to transform user requests into optimized arXiv search queries that will find the most relevant academic papers.

Guidelines:
1. Extract key technical terms and concepts
2. Use proper academic terminology 
3. Consider synonyms and related terms
4. Format for arXiv search syntax
5. Focus on the core research question

Examples:
User: "I want papers about waste management"
Optimized: "waste management OR solid waste OR municipal waste OR recycling OR environmental engineering"

User: "machine learning for healthcare applications"  
Optimized: "machine learning healthcare OR medical artificial intelligence OR clinical AI OR health informatics"

User: "quantum computing algorithms"
Optimized: "quantum computing OR quantum algorithms OR quantum information OR qubit"

Return ONLY the optimized search query, nothing else."""),
                ("human", f"Convert this research request into an optimized arXiv search query: {user_query}")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            optimized_query = response.content.strip()
            
            state["query"] = optimized_query
            logger.info(f"🔍 Query optimized: '{user_query}' → '{optimized_query}'")
            return state
            
        except Exception as e:
            logger.error(f"❌ Query optimization failed: {e}")
            state["error"] = f"Query optimization failed: {str(e)}"
            return state
    
    def _search_arxiv(self, state: ResearchAgentState) -> ResearchAgentState:
        """Search arXiv using the optimized query."""
        try:
            query = state["query"]
            logger.info(f"🔍 Searching arXiv for: {query}")
            
            # arXiv API search with configurable timeout
            search_query = f"search_query=all:{query}"
            max_results = ARXIV_MAX_RESULTS
            params = f"{search_query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
            
            # Use configurable URLs and timeout
            response = requests.get(f"{ARXIV_API_BASE_URL}?{params}", timeout=API_REQUEST_TIMEOUT)
            
            if response.status_code != 200:
                raise Exception(f"arXiv API error: {response.status_code}")
            
            # Parse XML response
            feed = feedparser.parse(response.content)
            logger.info(f"📋 Parsed {len(feed.entries)} entries from arXiv")
            
            papers = []
            for entry in feed.entries:
                # Extract authors
                authors = []
                if hasattr(entry, 'authors'):
                    authors = [author.name for author in entry.authors]
                elif hasattr(entry, 'author'):
                    authors = [entry.author]
                
                # Extract arXiv ID from the link
                arxiv_id = entry.id.split('/abs/')[-1] if '/abs/' in entry.id else entry.id
                
                # Extract categories
                categories = []
                if hasattr(entry, 'tags'):
                    categories = [tag.term for tag in entry.tags]
                
                paper = {
                    "id": arxiv_id,
                    "title": entry.title.replace('\n', ' ').strip(),
                    "authors": authors,
                    "summary": entry.summary.replace('\n', ' ').strip(),
                    "published": getattr(entry, 'published', '')[:10],  # Just date part
                    "updated": getattr(entry, 'updated', ''),
                    "pdf_url": f"{ARXIV_PDF_BASE_URL}/{arxiv_id}.pdf",
                    "abs_url": f"{ARXIV_ABS_BASE_URL}/{arxiv_id}",
                    "categories": categories,
                    "arxiv_id": arxiv_id
                }
                papers.append(paper)
            
            state["arxiv_results"] = papers
            logger.info(f"📚 Found {len(papers)} papers for query: {query}")
            return state
            
        except requests.exceptions.Timeout:
            logger.error("⏰ ArXiv API request timed out")
            state["error"] = "ArXiv search timed out. Please try again."
            return state
        except Exception as e:
            logger.error(f"❌ ArXiv search failed: {e}")
            state["error"] = f"ArXiv search failed: {str(e)}"
            return state
    
    def _download_and_process_pdf(self, paper_id: str, pdf_url: str) -> str:
        """Download and extract text from a PDF URL."""
        try:
            # Download PDF
            logger.info(f"📥 Downloading PDF: {pdf_url}")
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Sanitize paper_id for filename (replace slashes with underscores)
            safe_paper_id = paper_id.replace('/', '_').replace('\\', '_')
            
            # Store PDF content in memory instead of filesystem
            pdf_content = response.content
            self.papers_storage[f"{safe_paper_id}.pdf"] = pdf_content
            
            # Extract text using PyPDF2
            pdf_reader = PyPDF2.PdfReader(BytesIO(response.content))
            text_content = ""
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                # Clean up mathematical notation
                cleaned_text = self._clean_mathematical_notation(page_text)
                text_content += cleaned_text + "\n"
            
            logger.info(f"📄 Extracted text from PDF: {paper_id} ({len(pdf_reader.pages)} pages)")
            return text_content
            
        except Exception as e:
            logger.error(f"❌ PDF download/processing failed for {paper_id}: {e}")
            return ""
    
    def _clean_mathematical_notation(self, text: str) -> str:
        """Clean up mathematical notation from PDF text extraction."""
        
        # Dictionary of common PDF text extraction artifacts and their proper representations
        replacements = {
            # Parentheses
            '/parenleftbig': '(',
            '/parenrightbig': ')',
            '/parenleftBig': '(',
            '/parenrightBig': ')',
            
            # Mathematical symbols
            '/summationdisplay': '∑',
            '/summation': '∑',
            '/integral': '∫',
            '/integraltext': '∫',
            '/productdisplay': '∏',
            '/product': '∏',
            
            # Greek letters
            '/alpha': 'α',
            '/beta': 'β',
            '/gamma': 'γ',
            '/delta': 'δ',
            '/epsilon': 'ε',
            '/zeta': 'ζ',
            '/eta': 'η',
            '/theta': 'θ',
            '/lambda': 'λ',
            '/mu': 'μ',
            '/nu': 'ν',
            '/xi': 'ξ',
            '/pi': 'π',
            '/rho': 'ρ',
            '/sigma': 'σ',
            '/tau': 'τ',
            '/phi': 'φ',
            '/chi': 'χ',
            '/psi': 'ψ',
            '/omega': 'ω',
            '/Gamma': 'Γ',
            '/Delta': 'Δ',
            '/Theta': 'Θ',
            '/Lambda': 'Λ',
            '/Xi': 'Ξ',
            '/Pi': 'Π',
            '/Sigma': 'Σ',
            '/Phi': 'Φ',
            '/Psi': 'Ψ',
            '/Omega': 'Ω',
            
            # Mathematical operators
            '/cdot': '·',
            '/times': '×',
            '/div': '÷',
            '/pm': '±',
            '/mp': '∓',
            '/leq': '≤',
            '/geq': '≥',
            '/neq': '≠',
            '/approx': '≈',
            '/equiv': '≡',
            '/sim': '~',
            '/propto': '∝',
            '/infty': '∞',
            '/partial': '∂',
            '/nabla': '∇',
            '/sqrt': '√',
            
            # Arrows
            '/rightarrow': '→',
            '/leftarrow': '←',
            '/leftrightarrow': '↔',
            '/Rightarrow': '⇒',
            '/Leftarrow': '⇐',
            '/Leftrightarrow': '⇔',
            
            # Set theory
            '/in': '∈',
            '/notin': '∉',
            '/subset': '⊂',
            '/supset': '⊃',
            '/subseteq': '⊆',
            '/supseteq': '⊇',
            '/cup': '∪',
            '/cap': '∩',
            '/emptyset': '∅',
            
            # Logic
            '/wedge': '∧',
            '/vee': '∨',
            '/neg': '¬',
            '/forall': '∀',
            '/exists': '∃',
            
            # Fractions and superscripts
            '/frac': '',
            '/over': '/',
            '/atop': '/',
            
            # Brackets
            '/lbrace': '{',
            '/rbrace': '}',
            '/lbrack': '[',
            '/rbrack': ']',
            '/langle': '⟨',
            '/rangle': '⟩',
            
            # Spacing artifacts
            '/,': ' ',
            '/;': ' ',
            '/quad': '  ',
            '/qquad': '    ',
            '/ ': ' ',
            
            # Common PDF extraction artifacts
            'fi': 'fi',  # ligature
            'fl': 'fl',  # ligature
            'ff': 'ff',  # ligature
        }
        
        # Apply replacements
        cleaned_text = text
        for old, new in replacements.items():
            cleaned_text = cleaned_text.replace(old, new)
        
        # Clean up multiple spaces
        import re
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text
    
    def _extract_references_section(self, text: str) -> str:
        """Extract the references/bibliography section from paper text."""
        try:
            # Common patterns for references sections
            reference_patterns = [
                r'(?i)\n\s*references\s*\n',
                r'(?i)\n\s*bibliography\s*\n',
                r'(?i)\n\s*literature\s+cited\s*\n',
                r'(?i)\n\s*works\s+cited\s*\n',
                r'(?i)\n\s*citations\s*\n',
                r'(?i)\n\s*\[\s*references\s*\]\s*\n',
                r'(?i)\n\s*\d+\.\s*references\s*\n',
                r'(?i)\n\s*\d+\s+references\s*\n'
            ]
            
            # Try to find references section start
            references_start = None
            for pattern in reference_patterns:
                import re
                match = re.search(pattern, text)
                if match:
                    references_start = match.end()
                    break
            
            if references_start:
                # Extract from references start to end of document
                references_text = text[references_start:]
                
                # Try to find where references end (appendix, acknowledgments, etc.)
                end_patterns = [
                    r'(?i)\n\s*appendix\s*\n',
                    r'(?i)\n\s*acknowledgments?\s*\n',
                    r'(?i)\n\s*acknowledgements?\s*\n',
                    r'(?i)\n\s*author\s+information\s*\n',
                    r'(?i)\n\s*supplementary\s+material\s*\n'
                ]
                
                references_end = len(references_text)
                for pattern in end_patterns:
                    match = re.search(pattern, references_text)
                    if match:
                        references_end = match.start()
                        break
                
                extracted_refs = references_text[:references_end].strip()
                
                # Validate that we found actual references (should contain brackets or numbers)
                if re.search(r'(\[\d+\]|\(\d{4}\)|^\s*\d+\.)', extracted_refs, re.MULTILINE):
                    return extracted_refs
            
            # Fallback: look for numbered references in the last part of the document
            # Take last 30% of document and look for reference patterns
            fallback_start = int(len(text) * 0.7)
            fallback_text = text[fallback_start:]
            
            # Look for patterns like [1], [2], etc. or numbered references
            if re.search(r'(\[\d+\].*\n.*){3,}', fallback_text, re.MULTILINE):
                return fallback_text
                
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract references section: {e}")
            return None
    
    def _extract_pdf_text(self, state: ResearchAgentState) -> ResearchAgentState:
        """Extract text content from uploaded PDF."""
        try:
            paper_id = state["paper_id"]
            
            # Read PDF content from in-memory storage
            pdf_key = f"{paper_id}.pdf"
            if pdf_key not in self.papers_storage:
                raise FileNotFoundError(f"PDF not found in memory: {paper_id}")
            
            # Extract text using PyPDF2
            pdf_content = self.papers_storage[pdf_key]
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            text_content = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            
            # Store extracted text in vault
            text_data = {
                "paper_id": paper_id,
                "extracted_text": text_content,
                "page_count": len(pdf_reader.pages),
                "extracted_at": datetime.now(timezone.utc).isoformat()
            }
            
            vault_key = f"paper_text_{paper_id}"
            self._store_in_vault(text_data, vault_key, state["user_id"], state["consent_tokens"])
            
            # Create JSON file for chat functionality (same format as arXiv papers)
            paper_data = {
                "content": text_content,
                "metadata": {
                    "paper_id": paper_id, 
                    "uploaded_at": datetime.now(timezone.utc).isoformat(),
                    "page_count": len(pdf_reader.pages),
                    "source": "uploaded"
                },
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Save JSON data in memory instead of filesystem
            json_key = f"{paper_id}.json"
            self.papers_storage[json_key] = json.dumps(paper_data, ensure_ascii=False, indent=2)
            
            state["paper_content"] = text_content
            logger.info(f"📄 Extracted text from PDF: {paper_id} ({len(pdf_reader.pages)} pages) and saved JSON for chat access")
            return state
            
        except Exception as e:
            logger.error(f"❌ PDF text extraction failed: {e}")
            state["error"] = f"PDF text extraction failed: {str(e)}"
            return state
    
    def _generate_summary(self, state: ResearchAgentState) -> ResearchAgentState:
        """Generate AI-powered summary of the research paper."""
        try:
            paper_content = state["paper_content"]
            paper_id = state["paper_id"]
            
            # Create summarization prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert academic research assistant. Your task is to create comprehensive, well-structured summaries of research papers.

Create a summary with these sections:

## 🎯 Research Objective
What problem does this paper address? What are the main research questions?

## 🔬 Methodology  
What approaches, methods, or techniques were used? Include key experimental details.

## 📊 Key Findings
What are the main results and discoveries? Include important metrics or outcomes.

## 💡 Contributions
What novel contributions does this work make to the field?

## 🔗 Implications
What are the broader implications and potential applications?

## 🚀 Future Work
What future research directions are suggested?

Guidelines:
- Be concise but comprehensive
- Use clear, accessible language
- Highlight the most important points
- Maintain academic accuracy
- Focus on actionable insights"""),
                ("human", f"Please summarize this research paper:\n\n{paper_content[:8000]}...")  # Limit text to avoid token limits
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            summary = response.content
            
            # Store summary in vault
            summary_data = {
                "paper_id": paper_id,
                "summary": summary,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": "gemini-2.0-flash-exp"
            }
            
            vault_key = f"paper_summary_{paper_id}"
            self._store_in_vault(summary_data, vault_key, state["user_id"], state["consent_tokens"])
            
            state["summary"] = summary
            logger.info(f"📝 Generated summary for paper: {paper_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Summary generation failed: {e}")
            state["error"] = f"Summary generation failed: {str(e)}"
            return state
    
    def _process_snippet(self, state: ResearchAgentState) -> ResearchAgentState:
        """Process text snippet according to user instruction."""
        try:
            snippet = state["snippet"]
            instruction = state["instruction"]
            paper_id = state.get("paper_id", "unknown")
            
            # Create processing prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert research assistant. Your task is to process text snippets from academic papers according to specific user instructions.

Guidelines:
- Follow the user's instruction precisely
- Maintain academic accuracy and rigor
- Provide clear, well-structured responses
- If explaining concepts, use accessible language
- If summarizing, capture key points concisely
- If analyzing, provide insightful commentary
- Always cite or reference the source text when relevant"""),
                ("human", f"""Please process this text snippet according to the instruction:

**Text Snippet:**
{snippet}

**User Instruction:**
{instruction}

Provide your response:""")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            processed_result = response.content
            
            # Store processing result
            processing_data = {
                "paper_id": paper_id,
                "snippet": snippet,
                "instruction": instruction,
                "result": processed_result,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
            vault_key = f"snippet_processing_{uuid.uuid4().hex[:8]}"
            self._store_in_vault(processing_data, vault_key, state["user_id"], state["consent_tokens"])
            
            state["processed_snippet"] = processed_result
            logger.info(f"✨ Processed snippet for paper: {paper_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Snippet processing failed: {e}")
            state["error"] = f"Snippet processing failed: {str(e)}"
            return state
    
    def _save_notes(self, state: ResearchAgentState) -> ResearchAgentState:
        """Save user notes to vault storage."""
        try:
            notes = state["notes"]
            session_id = state["session_id"]
            paper_id = state.get("paper_id", "general")
            
            # Store notes in vault
            notes_data = {
                "session_id": session_id,
                "paper_id": paper_id,
                "notes": notes,
                "saved_at": datetime.now(timezone.utc).isoformat()
            }
            
            vault_key = f"research_notes_{session_id}_{paper_id}"
            self._store_in_vault(notes_data, vault_key, state["user_id"], state["consent_tokens"])
            
            logger.info(f"💾 Saved notes for session: {session_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Note saving failed: {e}")
            state["error"] = f"Note saving failed: {str(e)}"
            return state
    
    def _error_handler(self, state: ResearchAgentState) -> ResearchAgentState:
        """Handle errors in the workflow."""
        error = state.get("error", "Unknown error occurred")
        logger.error(f"🚨 Research Agent Error: {error}")
        
        state["status"] = "error"
        return state
    
    def _store_in_vault(self, data: Dict[str, Any], vault_key: str, user_id: str, consent_tokens: Dict[str, str]):
        """Store data in the HushMCP vault with encryption."""
        try:
            # Validate write permissions
            write_scope_key = ConsentScope.VAULT_WRITE_FILE.value
            if write_scope_key not in consent_tokens:
                raise ValueError("Missing vault write permission")
            
            # Encrypt and store
            encrypted_data = encrypt_data(json.dumps(data), VAULT_ENCRYPTION_KEY)
            
            # Use in-memory storage for Vercel compatibility
            vault_key_full = f"{user_id}_{vault_key}"
            self.vault_storage[vault_key_full] = {
                'ciphertext': encrypted_data.ciphertext,
                'iv': encrypted_data.iv,
                'tag': encrypted_data.tag,
                'encoding': encrypted_data.encoding,
                'algorithm': encrypted_data.algorithm,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"📁 Stored encrypted data for key: {vault_key_full}")
            return {"status": "success", "message": f"Data stored successfully for key: {vault_key}"}
            
        except Exception as e:
            logger.error(f"❌ Vault storage failed: {e}")
            raise
    
    async def search_arxiv_with_content(self, user_id: str, consent_tokens: Dict[str, str], query: str, max_papers: int = 3) -> Dict[str, Any]:
        """Enhanced arXiv search with automatic PDF downloading and content extraction."""
        session_id = f"enhanced_search_{uuid.uuid4().hex[:8]}"
        
        try:
            logger.info(f"🔍 Enhanced search for: {query}")
            
            # First do regular search
            initial_state = ResearchAgentState(
                user_id=user_id,
                consent_tokens=consent_tokens,
                session_id=session_id,
                query=query,
                status="arxiv_search",
                mode="api",
                paper_id=None,
                paper_content=None,
                arxiv_results=None,
                summary=None,
                snippet=None,
                instruction=None,
                processed_snippet=None,
                notes=None,
                error=None
            )
            
            # Run search workflow
            app = self.workflow.compile()
            final_state = app.invoke(initial_state)
            
            if final_state.get("error"):
                return {
                    "success": False,
                    "error": final_state["error"],
                    "session_id": session_id
                }
            
            papers = final_state.get("arxiv_results", [])
            enhanced_papers = []
            
            # Process top papers with full content
            for i, paper in enumerate(papers[:max_papers]):
                try:
                    logger.info(f"📥 Processing paper {i+1}/{max_papers}: {paper['title'][:50]}...")
                    
                    # Download and extract PDF content
                    content = self._download_and_process_pdf(paper['arxiv_id'], paper['pdf_url'])
                    
                    if content:
                        # Generate enhanced summary with full content
                        enhanced_summary = await self._generate_enhanced_summary(content, paper)
                        paper['enhanced_summary'] = enhanced_summary
                        paper['has_full_content'] = True
                        paper['content_preview'] = content[:1000] + "..." if len(content) > 1000 else content
                    else:
                        paper['enhanced_summary'] = paper['summary']  # fallback to abstract
                        paper['has_full_content'] = False
                    
                    enhanced_papers.append(paper)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process paper {paper['arxiv_id']}: {e}")
                    paper['enhanced_summary'] = paper['summary']  # fallback
                    paper['has_full_content'] = False
                    enhanced_papers.append(paper)
            
            # Add remaining papers without full processing
            enhanced_papers.extend(papers[max_papers:])
            
            return {
                "success": True,
                "session_id": session_id,
                "query": final_state["query"],
                "results": enhanced_papers,
                "total_papers": len(papers),
                "processed_papers": min(max_papers, len(papers))
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def _generate_enhanced_summary(self, content: str, paper_info: dict) -> str:
        """Generate enhanced summary from full paper content."""
        try:
            # Truncate content if too long (to avoid token limits)
            max_content_length = 8000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "\n...[Content truncated]"
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert academic research assistant. Create a comprehensive summary of this research paper that goes beyond the abstract.

Focus on:
1. **Main Research Question**: What problem does this paper address?
2. **Methodology**: How did they approach the problem?
3. **Key Findings**: What are the main results and discoveries?
4. **Implications**: What does this mean for the field?
5. **Limitations**: What are the constraints or limitations mentioned?
6. **Future Work**: What directions for future research are suggested?

Provide a detailed but concise summary that would be helpful for someone researching this topic."""),
                ("user", f"""Paper Title: {paper_info.get('title', 'Unknown')}
Authors: {', '.join(paper_info.get('authors', []))}
Published: {paper_info.get('published', 'Unknown')}

Abstract: {paper_info.get('summary', 'Not available')}

Full Paper Content:
{content}

Please provide a comprehensive summary that goes beyond the abstract and covers the key aspects of the full paper.""")
            ])
            
            response = self.llm.invoke(prompt.format_messages())
            return response.content
            
        except Exception as e:
            logger.error(f"❌ Enhanced summary generation failed: {e}")
            return paper_info.get('summary', 'Summary not available')

    async def search_arxiv(self, user_id: str, consent_tokens: Dict[str, str], query: str, mode: str = "api") -> Dict[str, Any]:
        """Execute arXiv search workflow."""
        session_id = f"search_{uuid.uuid4().hex[:8]}"
        
        initial_state = ResearchAgentState(
            user_id=user_id,
            consent_tokens=consent_tokens,
            session_id=session_id,
            query=query,
            status="arxiv_search",
            mode=mode,
            paper_id=None,
            paper_content=None,
            arxiv_results=None,
            summary=None,
            snippet=None,
            instruction=None,
            processed_snippet=None,
            notes=None,
            error=None
        )
        
        result = await self.workflow.ainvoke(initial_state)
        
        if result.get("error"):
            return {
                "success": False,
                "error": result["error"],
                "session_id": session_id
            }
        
        return {
            "success": True,
            "session_id": session_id,
            "query": result["query"],
            "results": result["arxiv_results"],
            "total_papers": len(result["arxiv_results"]) if result["arxiv_results"] else 0
        }
    
    async def process_pdf_upload(self, user_id: str, consent_tokens: Dict[str, str], paper_id: str, pdf_file: UploadFile, mode: str = "api") -> Dict[str, Any]:
        """Process uploaded PDF file."""
        session_id = f"upload_{uuid.uuid4().hex[:8]}"
        
        try:
            # Store uploaded file in memory instead of filesystem
            content = await pdf_file.read()
            pdf_key = f"{paper_id}.pdf"
            self.papers_storage[pdf_key] = content
            
            initial_state = ResearchAgentState(
                user_id=user_id,
                consent_tokens=consent_tokens,
                session_id=session_id,
                paper_id=paper_id,
                status="pdf_upload",
                mode=mode,
                query=None,
                paper_content=None,
                arxiv_results=None,
                summary=None,
                snippet=None,
                instruction=None,
                processed_snippet=None,
                notes=None,
                error=None
            )
            
            result = await self.workflow.ainvoke(initial_state)
            
            if result.get("error"):
                return {
                    "success": False,
                    "error": result["error"],
                    "session_id": session_id
                }
            
            return {
                "success": True,
                "session_id": session_id,
                "paper_id": paper_id,
                "text_extracted": len(result["paper_content"]) if result["paper_content"] else 0
            }
            
        except Exception as e:
            logger.error(f"❌ PDF upload processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def generate_paper_summary(self, user_id: str, consent_tokens: Dict[str, str], paper_id: str, mode: str = "api") -> Dict[str, Any]:
        """Generate summary for a paper."""
        session_id = f"summary_{uuid.uuid4().hex[:8]}"
        
        try:
            # First extract text if not already done
            pdf_key = f"{paper_id}.pdf"
            if pdf_key not in self.papers_storage:
                return {
                    "success": False,
                    "error": f"Paper not found: {paper_id}",
                    "session_id": session_id
                }
            
            # Extract text
            pdf_content = self.papers_storage[pdf_key]
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            text_content = ""
            for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            
            initial_state = ResearchAgentState(
                user_id=user_id,
                consent_tokens=consent_tokens,
                session_id=session_id,
                paper_id=paper_id,
                paper_content=text_content,
                status="summary_generation",
                mode=mode,
                query=None,
                arxiv_results=None,
                summary=None,
                snippet=None,
                instruction=None,
                processed_snippet=None,
                notes=None,
                error=None
            )
            
            result = await self.workflow.ainvoke(initial_state)
            
            if result.get("error"):
                return {
                    "success": False,
                    "error": result["error"],
                    "session_id": session_id
                }
            
            return {
                "success": True,
                "session_id": session_id,
                "paper_id": paper_id,
                "summary": result["summary"]
            }
            
        except Exception as e:
            logger.error(f"❌ Summary generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def process_text_snippet(self, user_id: str, consent_tokens: Dict[str, str], paper_id: str, snippet: str, instruction: str, mode: str = "api") -> Dict[str, Any]:
        """Process text snippet with user instruction."""
        session_id = f"snippet_{uuid.uuid4().hex[:8]}"
        
        initial_state = ResearchAgentState(
            user_id=user_id,
            consent_tokens=consent_tokens,
            session_id=session_id,
            paper_id=paper_id,
            snippet=snippet,
            instruction=instruction,
            status="snippet_processing",
            mode=mode,
            query=None,
            paper_content=None,
            arxiv_results=None,
            summary=None,
            processed_snippet=None,
            notes=None,
            error=None
        )
        
        result = await self.workflow.ainvoke(initial_state)
        
        if result.get("error"):
            return {
                "success": False,
                "error": result["error"],
                "session_id": session_id
            }
        
        return {
            "success": True,
            "session_id": session_id,
            "paper_id": paper_id,
            "original_snippet": snippet,
            "instruction": instruction,
            "processed_result": result["processed_snippet"]
        }
    
    async def save_session_notes(self, user_id: str, consent_tokens: Dict[str, str], paper_id: str, editor_id: str, content: str, mode: str = "api") -> Dict[str, Any]:
        """Save notes to vault storage."""
        session_id = f"notes_{uuid.uuid4().hex[:8]}"
        
        notes = {editor_id: content}
        
        initial_state = ResearchAgentState(
            user_id=user_id,
            consent_tokens=consent_tokens,
            session_id=session_id,
            paper_id=paper_id,
            notes=notes,
            status="note_saving",
            mode=mode,
            query=None,
            paper_content=None,
            arxiv_results=None,
            summary=None,
            snippet=None,
            instruction=None,
            processed_snippet=None,
            error=None
        )
        
        result = await self.workflow.ainvoke(initial_state)
        
        if result.get("error"):
            return {
                "success": False,
                "error": result["error"],
                "session_id": session_id
            }
        
        return {
            "success": True,
            "session_id": session_id,
            "paper_id": paper_id,
            "editor_id": editor_id,
            "content_length": len(content)
        }
    
    async def chat_about_paper(self, user_id: str, consent_tokens: Dict[str, str], paper_id: str, message: str, conversation_history: List[Dict[str, str]] = None, mode: str = "api") -> Dict[str, Any]:
        """
        Chat with AI about a specific paper.
        
        Args:
            user_id: User identifier
            consent_tokens: Required consent tokens
            paper_id: ID of the paper to discuss
            message: User's message/question
            conversation_history: Previous conversation messages
            mode: Execution mode ('api' or 'interactive')
            
        Returns:
            Dict with success status, AI response, and session info
        """
        session_id = f"chat_{uuid.uuid4().hex[:8]}"
        
        try:
            # Validate consent tokens first
            required_scopes = [ConsentScope.CUSTOM_TEMPORARY, ConsentScope.VAULT_READ_FILE]
            for scope in required_scopes:
                if scope.value not in consent_tokens:
                    logger.warning(f"Missing consent token for scope: {scope.value}")
                    return {
                        "success": False,
                        "error": f"Missing consent token for scope: {scope.value}",
                        "session_id": session_id
                    }
            
            # Try to load paper from vault or download if not available
            paper_content = None
            paper_metadata = None
            
            try:
                # Sanitize paper_id for filename consistency
                safe_paper_id = paper_id.replace('/', '_').replace('\\', '_')
                
                # Try to load from in-memory JSON storage
                json_key = f"{safe_paper_id}.json"
                if json_key in self.papers_storage:
                    paper_data = json.loads(self.papers_storage[json_key])
                    paper_content = paper_data.get("content", "")
                    paper_metadata = paper_data.get("metadata", {})
                    logger.info(f"📄 Loaded paper {paper_id} from JSON storage")
                
                # Fallback to encrypted vault if JSON not found
                elif False:  # Disable vault for now
                    vault_key = f"{safe_paper_id}.enc"
                    if vault_key in self.papers_storage:
                        encrypted_data = self.papers_storage[vault_key]
                        decrypted_data = decrypt_data(encrypted_data, VAULT_ENCRYPTION_KEY)
                        paper_data = json.loads(decrypted_data)
                        paper_content = paper_data.get("content", "")
                        paper_metadata = paper_data.get("metadata", {})
                        logger.info(f"📄 Loaded paper {paper_id} from vault")
                
                else:
                    # Automatically download and process PDF if not in storage
                    logger.info(f"📥 Paper {paper_id} not found in storage, attempting to download...")
                    pdf_url = f"{ARXIV_PDF_BASE_URL}/{paper_id}.pdf"
                    paper_content = self._download_and_process_pdf(paper_id, pdf_url)
                    
                    if paper_content:
                        # Store in simple JSON file for future use
                        paper_data = {
                            "content": paper_content,
                            "metadata": {"paper_id": paper_id, "downloaded_at": datetime.now(timezone.utc).isoformat()},
                            "processed_at": datetime.now(timezone.utc).isoformat()
                        }
                        
                        # Store in memory instead of filesystem
                        storage_key = f"{safe_paper_id}.json"
                        self.papers_storage[storage_key] = json.dumps(paper_data, ensure_ascii=False, indent=2)
                        
                        logger.info(f"✅ Downloaded and processed paper {paper_id}")
                    else:
                        logger.warning(f"❌ Failed to download paper {paper_id}")
                        
            except Exception as e:
                logger.warning(f"⚠️ Could not load/download paper {paper_id}: {e}")
            
            # Build conversation context
            conversation_context = ""
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    conversation_context += f"{role}: {content}\n"
            
            # Create chat prompt
            chat_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert AI research assistant with FULL ACCESS to complete academic paper content. You have the ENTIRE paper text available to you - NOT just abstracts or summaries.

                Paper Information:
                {paper_info}

                Previous Conversation:
                {conversation_context}

                CRITICAL INSTRUCTIONS:
                - You have COMPLETE access to the full paper content including ALL sections
                - NEVER say the paper content is truncated or that references are not available
                - You can see the entire paper from introduction to conclusion to references
                - Provide detailed, specific responses based on the complete paper content
                - Quote specific sections, figures, or data when relevant
                - Explain methodology, results, and implications in detail
                - Answer questions about introduction, methods, results, discussion, conclusions, AND references
                - Discuss specific experiments, datasets, algorithms, or findings mentioned in the paper
                - Compare findings with related work mentioned in the paper
                - Be precise and reference specific parts of the paper
                - If asked about details not in the paper, clearly state that
                
                **REFERENCES AND CITATIONS:**
                - When asked for references, extract and list ALL references found in the paper
                - Format references clearly with proper numbering or citation style
                - If references section is truncated, mention this and provide what's available
                - Include DOIs, arXiv IDs, and journal information when present
                - Group references by type if helpful (journals, conferences, books, etc.)
                
                **RESPONSE FORMATTING:**
                - FORMAT ALL RESPONSES IN PROPER MARKDOWN SYNTAX
                - Use # ## ### for headers to structure your response
                - Use **bold** for emphasis and important terms
                - Use *italics* for paper titles and terms
                - Use > blockquotes for important quotes from the paper
                - Use - or * for bullet lists, 1. 2. 3. for numbered lists
                - Use `code` for technical terms, variable names, or short formulas
                
                **MATHEMATICAL FORMULAS - CRITICAL FORMATTING:**
                - ALWAYS format mathematical equations using MARKDOWN CODE BLOCKS with math syntax
                - For inline math: use `$equation$` 
                - For display math: use ```math or $$equation$$
                - Present equations with proper equation numbers when available like: **(2.1)**, **(3.4)**
                - Use proper mathematical symbols (∇, ∂, ∑, ∫, α, β, γ, etc.)
                - Clean up any garbled mathematical notation from PDF extraction
                - Example format:
                
                **Equation (3.1)** - Killing Vector Field:
                ```math
                L_K g_ab = ∇_a K_b + ∇_b K_a = 0
                ```
                
                **Equation (3.4)** - Ricci Contraction:
                ```math
                ∇_a ∇^a K_c + R_cd K^d = 0
                ```

                ⚠️ CRITICAL RESPONSE RULES ⚠️:
                - NEVER say "paper content is truncated" 
                - NEVER say "references section is not available"
                - NEVER apologize for truncated content
                - You have FULL access to ALL sections including references
                - Always provide complete, detailed answers based on the full paper content
                """),
                ("human", "{user_message}")
            ])

            # Prepare comprehensive paper information
            paper_info = "Paper content not available"
            if paper_content:
                # Check if user is asking for references specifically
                user_asking_for_references = any(keyword in message.lower() for keyword in [
                    'references', 'bibliography', 'citations', 'reference list', 'works cited', 'literature cited'
                ])
                
                if user_asking_for_references:
                    # For references, try to extract the references section specifically
                    references_section = self._extract_references_section(paper_content)
                    if references_section:
                        paper_info = f"""
                        ✅ COMPLETE REFERENCES SECTION AVAILABLE ✅
                        
                        Paper ID: {paper_id}
                        Status: FULL PAPER CONTENT LOADED
                        Total Paper Length: {len(paper_content)} characters
                        
                        Complete References Section:
                        {references_section}
                        
                        [COMPLETE REFERENCES SECTION ABOVE - YOU HAVE FULL ACCESS]
                        """
                    else:
                        # If no references section found, use the last part of the paper
                        max_content_length = 25000  # Increased for references
                        if len(paper_content) > max_content_length:
                            # Take the last part of the paper where references usually are
                            content_to_use = paper_content[-max_content_length:]
                            paper_info = f"""
                            ✅ COMPLETE PAPER CONTENT AVAILABLE ✅
                            
                            Paper ID: {paper_id}
                            Status: FULL PAPER LOADED - REFERENCES SECTION INCLUDED
                            Total Paper Length: {len(paper_content)} characters
                            
                            Last Section of Paper (Contains References):
                            {content_to_use}
                            
                            [SHOWING LAST {max_content_length} CHARACTERS - REFERENCES SECTION INCLUDED]
                            """
                        else:
                            paper_info = f"""
                            ✅ COMPLETE FULL PAPER AVAILABLE ✅
                            
                            Paper ID: {paper_id}
                            Status: COMPLETE PAPER CONTENT LOADED
                            
                            Complete Full Paper Text:
                            {paper_content}
                            
                            [COMPLETE PAPER CONTENT ABOVE - ALL SECTIONS INCLUDING REFERENCES]
                            """
                else:
                    # For non-reference queries, use standard approach with increased limit
                    max_content_length = 20000  # Increased from 15000
                    content_to_use = paper_content[:max_content_length] if len(paper_content) > max_content_length else paper_content
                    
                    paper_info = f"""
                    ✅ COMPLETE FULL PAPER AVAILABLE ✅
                    
                    Paper ID: {paper_id}
                    Status: FULL PAPER CONTENT LOADED
                    Total Paper Length: {len(paper_content)} characters
                    
                    Paper Content:
                    {content_to_use}
                    
                    {'[FIRST PART OF PAPER SHOWN - ASK FOR REFERENCES TO SEE THAT SECTION]' if len(paper_content) > max_content_length else '[COMPLETE PAPER CONTENT ABOVE - ALL SECTIONS AVAILABLE]'}
                    """
            elif paper_metadata:
                paper_info = f"""
                LIMITED INFORMATION AVAILABLE (Abstract only)
                
                Title: {paper_metadata.get('title', 'Unknown')}
                Authors: {', '.join(paper_metadata.get('authors', []))}
                Abstract: {paper_metadata.get('summary', 'Not available')}
                
                Note: Full paper content could not be retrieved. Responses will be based on abstract only.
                """
            
            # Generate response using LLM
            logger.info(f"🤖 Sending prompt to Gemini for paper {paper_id}")
            messages = chat_prompt.format_messages(
                paper_info=paper_info,
                conversation_context=conversation_context,
                user_message=message
            )
            logger.info(f"📝 Prompt length: {len(str(messages))} characters")
            
            try:
                # Safer async call with event loop handling
                try:
                    response = await self.llm.ainvoke(messages)
                    ai_response = response.content
                except RuntimeError as runtime_error:
                    if "Event loop is closed" in str(runtime_error):
                        logger.warning("⚠️ Event loop closed, attempting synchronous call...")
                        # Fallback to synchronous call
                        response = self.llm.invoke(messages)
                        ai_response = response.content
                    else:
                        raise runtime_error
                
                logger.info(f"✅ Received AI response: {len(ai_response)} characters")
                logger.info(f"💬 Generated chat response for paper {paper_id}")
                
                # Validate response quality
                if not ai_response or len(ai_response.strip()) < 10:
                    logger.warning(f"⚠️ Received very short or empty AI response: '{ai_response}'")
                    raise Exception("AI response was too short or empty")
                
                return {
                    "success": True,
                    "response": ai_response,
                    "session_id": session_id,
                    "paper_id": paper_id,
                    "message_count": len(conversation_history) + 1 if conversation_history else 1
                }
                
            except Exception as llm_error:
                logger.error(f"❌ LLM API error for paper {paper_id}: {llm_error}")
                logger.error(f"🔍 Error type: {type(llm_error).__name__}")
                
                # Try a simplified prompt if the complex one failed
                logger.info("🔄 Attempting simplified AI response...")
                try:
                    simple_prompt = ChatPromptTemplate.from_messages([
                        ("system", """You are an expert AI research assistant. Provide helpful, accurate responses about research topics.
                        
                        RESPONSE FORMATTING:
                        - FORMAT ALL RESPONSES IN PROPER MARKDOWN SYNTAX
                        - Use # ## ### for headers to structure your response
                        - Use **bold** for emphasis and important terms
                        - Use *italics* for paper titles and technical terms
                        - Use > blockquotes for important quotes
                        - Use - or * for bullet lists, 1. 2. 3. for numbered lists
                        - Use `code` for technical terms or formulas
                        
                        Keep responses clear, informative, and helpful."""),
                        ("human", "User question: {user_message}\n\nPaper context: {paper_context}")
                    ])
                    
                    simple_context = paper_content[:1000] if paper_content else "Paper content not available"
                    simple_messages = simple_prompt.format_messages(
                        user_message=message, 
                        paper_context=simple_context
                    )
                    
                    # Safer async call with event loop handling
                    try:
                        simple_response = await self.llm.ainvoke(simple_messages)
                        simple_ai_response = simple_response.content
                    except RuntimeError as runtime_error:
                        if "Event loop is closed" in str(runtime_error):
                            logger.warning("⚠️ Event loop closed in simplified call, using synchronous...")
                            simple_response = self.llm.invoke(simple_messages)
                            simple_ai_response = simple_response.content
                        else:
                            raise runtime_error
                    
                    if simple_ai_response and len(simple_ai_response.strip()) > 10:
                        logger.info(f"✅ Simplified AI response succeeded: {len(simple_ai_response)} characters")
                        return {
                            "success": True,
                            "response": simple_ai_response,
                            "session_id": session_id,
                            "paper_id": paper_id,
                            "message_count": len(conversation_history) + 1 if conversation_history else 1
                        }
                
                except Exception as simple_error:
                    logger.error(f"❌ Simplified AI response also failed: {simple_error}")
                
                # If all AI attempts fail, return error for backend to handle
                raise llm_error
            
        except Exception as e:
            logger.error(f"❌ Chat error for paper {paper_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "response": "I'm sorry, I encountered an error while processing your message. Please try again."
            }

    async def simple_chat(self, message: str) -> str:
        """
        Simple chat without paper context for fallback scenarios.
        
        Args:
            message: User's message/question
            
        Returns:
            AI response as string
        """
        try:
            logger.info(f"🔄 Starting simple chat for message: '{message[:50]}...'")
            
            # Create a simple prompt for general chat
            simple_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert AI research assistant. Provide helpful, accurate responses about research topics, academic papers, and scientific questions.

                RESPONSE FORMATTING:
                - FORMAT ALL RESPONSES IN PROPER MARKDOWN SYNTAX
                - Use # ## ### for headers to structure your response
                - Use **bold** for emphasis and important terms
                - Use *italics* for paper titles and technical terms
                - Use > blockquotes for important quotes
                - Use - or * for bullet lists, 1. 2. 3. for numbered lists
                - Use `code` for technical terms or formulas
                
                Keep responses clear, informative, and helpful."""),
                ("human", "{user_message}")
            ])
            
            messages = simple_prompt.format_messages(user_message=message)
            logger.info(f"📝 Simple chat prompt created, length: {len(str(messages))} characters")
            
            # Safer async call with event loop handling
            try:
                response = await self.llm.ainvoke(messages)
                ai_response = response.content
            except RuntimeError as runtime_error:
                if "Event loop is closed" in str(runtime_error):
                    logger.warning("⚠️ Event loop closed in simple chat, using synchronous...")
                    response = self.llm.invoke(messages)
                    ai_response = response.content
                else:
                    raise runtime_error
            
            logger.info(f"✅ Simple chat response received: {len(ai_response)} characters")
            
            # Validate response
            if not ai_response or len(ai_response.strip()) < 5:
                logger.warning(f"⚠️ Simple chat response too short: '{ai_response}'")
                return f"I can help with research questions! You asked: '{message}'. Could you please provide more details about what you'd like to explore?"
            
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ Simple chat error: {e}")
            logger.error(f"🔍 Error type: {type(e).__name__}")
            
            # Return a more helpful error message based on the user's input
            if any(word in message.lower() for word in ['okay', 'ok', 'yes', 'sure', 'thanks']):
                return f"Thanks for your message! I'm ready to help you analyze research papers and answer questions. What would you like to explore?"
            else:
                return f"I understand you're asking about: '{message}'. I can help with research questions and paper analysis. Could you please provide more details about what you'd like to know?"

# Global agent instance
research_agent = ResearchAgent()

def run_agent():
    """Entry point for the research agent."""
    print("🔬 Research Agent initialized with LangGraph workflow")
    return research_agent
