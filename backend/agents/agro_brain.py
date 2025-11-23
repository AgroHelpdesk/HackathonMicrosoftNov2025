"""
AgroBrain Agent - Knowledge Retrieval (RAG)
Retrieves relevant information from knowledge base
"""

import logging
from typing import Dict, Any, List
from services.openai_service import OpenAIService
from services.search_service import SearchService

logger = logging.getLogger(__name__)


class AgroBrainAgent:
    """Agent for knowledge retrieval using RAG"""
    
    SYSTEM_PROMPT = """Você é o AgroBrain, um agente especializado em conhecimento agrícola.

Sua tarefa é responder perguntas usando o contexto fornecido de documentos técnicos e bases de conhecimento.

Diretrizes:
1. Use APENAS as informações do contexto fornecido
2. Se o contexto não contiver informações relevantes, diga claramente
3. Cite as fontes quando possível
4. Seja preciso e técnico, mas compreensível
5. Responda em português brasileiro

Formato da resposta:
- Resposta clara e direta
- Cite as fontes entre [colchetes]
- Se não souber, seja honesto
"""
    
    def __init__(self, openai_service: OpenAIService, search_service: SearchService):
        """Initialize AgroBrain agent"""
        self.openai_service = openai_service
        self.search_service = search_service
        logger.info("AgroBrain Agent initialized")
    
    def retrieve_knowledge(
        self,
        query: str,
        intent: str = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve knowledge using RAG
        
        Args:
            query: User query
            intent: Classified intent (optional)
            top_k: Number of documents to retrieve
            
        Returns:
            Dict with answer, sources, and relevance score
        """
        try:
            # Search for relevant documents
            logger.info(f"Searching knowledge base for: {query[:50]}...")
            search_results = self.search_service.search(query, top=top_k)
            
            if not search_results:
                return {
                    "answer": "Desculpe, não encontrei informações relevantes na base de conhecimento para responder sua pergunta.",
                    "sources": [],
                    "relevance": 0.0
                }
            
            # Format context for RAG
            context = self.search_service.format_context_for_rag(search_results)
            
            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"Contexto:\n{context}\n\nPergunta: {query}"}
            ]
            
            # Get answer from OpenAI
            answer = self.openai_service.chat_completion(
                messages=messages,
                temperature=0.5,
                max_tokens=800
            )
            
            # Extract sources
            sources = [
                {
                    "fileName": result["fileName"],
                    "fileType": result["fileType"],
                    "score": result["score"]
                }
                for result in search_results
            ]
            
            # Calculate average relevance
            avg_relevance = sum(r["score"] for r in search_results) / len(search_results)
            
            logger.info(f"AgroBrain generated answer with {len(sources)} sources (relevance: {avg_relevance:.2f})")
            
            return {
                "answer": answer,
                "sources": sources,
                "relevance": avg_relevance
            }
            
        except Exception as e:
            logger.error(f"Error in AgroBrain knowledge retrieval: {e}")
            return {
                "answer": f"Erro ao buscar conhecimento: {str(e)}",
                "sources": [],
                "relevance": 0.0
            }
