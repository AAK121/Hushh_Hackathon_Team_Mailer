"""
Memory Manager Component
Handles interactions with vector database and memory processing
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone
import os

from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from .models import RelationshipMemory

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class MemoryManager:
    """Manages storage and retrieval of relationship memories"""
    
    def __init__(self):
        # Initialize vector DB connection
        pinecone.init(
            api_key="YOUR_PINECONE_API_KEY",
            environment="YOUR_PINECONE_ENV"
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vector_store = Pinecone.from_existing_index(
            "relationship-memories",
            self.embeddings
        )
    
    async def store_memory(
        self,
        memory_text: str,
        metadata: Dict
    ) -> str:
        """Store a memory in the vector database"""
        try:
            # Create embedding and store in Pinecone
            ids = self.vector_store.add_texts(
                texts=[memory_text],
                metadatas=[metadata]
            )
            return ids[0]  # Return the vector DB ID
            
        except Exception as e:
            logger.error(f"Error storing memory in vector DB: {str(e)}")
            raise
    
    async def search_similar_memories(
        self,
        query: str,
        user_id: str,
        contact_id: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Search for similar memories using semantic search"""
        try:
            # Prepare filter for the specific user (and optionally contact)
            filter_dict = {"user_id": user_id}
            if contact_id:
                filter_dict["contact_id"] = contact_id
            
            # Search vector DB
            results = self.vector_store.similarity_search_with_score(
                query,
                k=limit,
                filter=filter_dict
            )
            
            return [
                {
                    "text": result[0].page_content,
                    "metadata": result[0].metadata,
                    "score": result[1]
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching memories: {str(e)}")
            raise
    
    async def generate_summary(
        self,
        memories: List[RelationshipMemory]
    ) -> str:
        """Generate a summary of multiple memories using LLM"""
        # TODO: Implement LLM-based summary generation
        return "Memory summary pending implementation"
    
    def _encrypt_memory(self, memory_text: str) -> str:
        """Encrypt memory text before storage"""
        return encrypt_data(memory_text)
    
    def _decrypt_memory(self, encrypted_text: str) -> str:
        """Decrypt memory text after retrieval"""
        return decrypt_data(encrypted_text)
