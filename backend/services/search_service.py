"""
Azure AI Search Service
Handles semantic search queries for RAG
"""

import os
import logging
from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)


class SearchService:
    """Service for interacting with Azure AI Search"""
    
    def __init__(self):
        """Initialize Azure AI Search client"""
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "agro-knowledge-base")
        
        if not self.endpoint:
            raise ValueError("AZURE_SEARCH_ENDPOINT environment variable is required")
        
        # Use Azure CLI credentials
        credential = DefaultAzureCredential()
        
        self.client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=credential
        )
        
        logger.info(f"Search Service initialized with index: {self.index_name}")
    
    def search(
        self,
        query: str,
        top: int = 5,
        select: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search
        
        Args:
            query: Search query text
            top: Number of results to return
            select: Fields to include in results
            
        Returns:
            List of search results
        """
        if select is None:
            select = ["content", "title", "fileName", "fileType", "blobPath"]
        
        try:
            results = self.client.search(
                search_text=query,
                top=top,
                select=select,
                query_type="semantic",
                semantic_configuration_name="agro-semantic-config"
            )
            
            # Convert results to list of dicts
            search_results = []
            for result in results:
                search_results.append({
                    "content": result.get("content", ""),
                    "title": result.get("title", ""),
                    "fileName": result.get("fileName", ""),
                    "fileType": result.get("fileType", ""),
                    "blobPath": result.get("blobPath", ""),
                    "score": result.get("@search.score", 0.0)
                })
            
            logger.info(f"Search returned {len(search_results)} results for query: {query[:50]}...")
            return search_results
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            # Return empty results on error instead of failing
            return []
    
    def format_context_for_rag(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format search results into context for RAG
        
        Args:
            search_results: List of search result dicts
            
        Returns:
            Formatted context string
        """
        if not search_results:
            return "Nenhum documento relevante encontrado."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            source = f"{result['fileName']} ({result['fileType']})"
            content = result['content'][:500]  # Limit content length
            context_parts.append(f"[Fonte {i}: {source}]\n{content}\n")
        
        return "\n".join(context_parts)
