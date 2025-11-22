"""
Local RAG implementation using ChromaDB and Ollama
"""
import os
from typing import List, Dict, Any, Optional
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import chromadb

class LocalRAG:
    """
    Manages local RAG operations using ChromaDB and Ollama Embeddings.
    """
    
    def __init__(self, collection_name: str = "agro_knowledge_base", persist_directory: str = "./chroma_db"):
        """
        Initialize LocalRAG.
        
        Args:
            collection_name: Name of the ChromaDB collection.
            persist_directory: Directory to store ChromaDB data.
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize Embeddings (using nomic-embed-text which is good for RAG)
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
        )
        
        # Initialize Vector Store
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory,
        )
        
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of dictionaries containing 'content' and 'metadata'.
        """
        docs_to_add = []
        ids = []
        
        for doc in documents:
            # Ensure content is a string
            content = doc.get("content", "")
            if not content:
                continue
                
            # Prepare metadata (must be flat dict of str, int, float, bool)
            metadata = doc.get("metadata", {})
            # Add other fields to metadata if needed, or keep them separate
            # For simplicity, we assume 'metadata' in input is ready or we construct it
            
            # If input doc has specific fields we want to index as metadata:
            safe_metadata = {}
            for k, v in doc.items():
                if k != "content" and k != "id":
                    if isinstance(v, (str, int, float, bool)):
                        safe_metadata[k] = v
                    else:
                        safe_metadata[k] = str(v) # Convert complex types to string
            
            # Use provided ID or generate one
            doc_id = str(doc.get("id", f"doc_{len(ids)}"))
            
            docs_to_add.append(Document(page_content=content, metadata=safe_metadata))
            ids.append(doc_id)
            
        if docs_to_add:
            print(f"Adding {len(docs_to_add)} documents to ChromaDB...")
            self.vector_store.add_documents(documents=docs_to_add, ids=ids)
            print("Documents added successfully.")
            
    def query(self, query_text: str, n_results: int = 5, filter: Optional[Dict] = None) -> List[Document]:
        """
        Query the vector store.
        
        Args:
            query_text: The search query.
            n_results: Number of results to return.
            filter: Optional metadata filter.
            
        Returns:
            List of matching Documents.
        """
        print(f"Querying ChromaDB for: '{query_text}'")
        results = self.vector_store.similarity_search(
            query_text,
            k=n_results,
            filter=filter
        )
        return results
        
    def delete_collection(self):
        """Deletes the entire collection (useful for re-indexing)."""
        self.vector_store.delete_collection()
        print(f"Collection '{self.collection_name}' deleted.")
