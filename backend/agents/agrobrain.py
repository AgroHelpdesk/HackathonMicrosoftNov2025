"""
AgroBrain Agent - Base de conhecimento agrícola com RAG
"""
from typing import Dict, Any
import time
from .base_agent import BaseAgent, AgentResponse


class AgroBrainAgent(BaseAgent):
    """
    Agente de conhecimento agrícola com RAG (Retrieval Augmented Generation).
    
    Responsável por:
    - Consultar base de conhecimento agrícola
    - Buscar informações relevantes (Azure AI Search)
    - Gerar respostas baseadas em conhecimento
    - Fornecer recomendações técnicas
    """
    
    def __init__(self):
        super().__init__(
            name="AgroBrain",
            role="Knowledge Base & RAG",
            description="Queries agricultural knowledge base and provides expert recommendations"
        )
        
        # Inicializar Local RAG
        try:
            from ..data_processing.local_rag import LocalRAG
            self.rag = LocalRAG()
        except ImportError:
            self.logger.warning("LocalRAG dependencies not found.")
            self.rag = None
    
    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Processa a consulta e busca conhecimento relevante.
        """
        start_time = time.time()
        self.log_request(context)
        
        try:
            intent = context.get("intent", "general")
            enriched_context = context.get("enriched_context", {})
            query = context.get("query", "")
            message = context.get("message", "")
            
            # Usar a mensagem original se query não estiver definida
            search_query = query if query else message
            
            # Buscar conhecimento relevante
            knowledge_docs = self._search_knowledge(search_query)
            
            # Gerar resposta com LLM
            response_text = self._generate_response(search_query, knowledge_docs)
            
            # Extrair recomendações (se possível estruturar)
            recommendations = self._extract_recommendations(response_text)
            
            # Calcular confiança
            confidence = self._calculate_confidence(knowledge_docs)
            
            response = AgentResponse(
                agent_name=self.name,
                success=True,
                data={
                    "knowledge": [d.page_content for d in knowledge_docs],
                    "response_text": response_text,
                    "recommendations": recommendations,
                    "confidence": confidence,
                    "next_agent": "RunbookMaster"
                },
                metadata={
                    "intent": intent,
                    "knowledge_items_found": len(knowledge_docs)
                }
            )
            
            processing_time = (time.time() - start_time) * 1000
            self.log_success(response, processing_time)
            
            return response
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.log_error(e, processing_time)
            
            return AgentResponse(
                agent_name=self.name,
                success=False,
                error=str(e)
            )
    
    def _search_knowledge(self, query: str) -> list:
        """
        Busca conhecimento relevante na base RAG.
        """
        if not self.rag:
            return []
            
        try:
            return self.rag.query(query, n_results=3)
        except Exception as e:
            self.logger.error(f"RAG search failed: {e}")
            return []
    
    def _generate_response(self, query: str, docs: list) -> str:
        """Gera resposta usando LLM e contexto recuperado"""
        if not self.llm:
            return "Desculpe, não consigo gerar uma resposta no momento."
            
        context_text = "\n\n".join([d.page_content for d in docs])
        
        prompt = f"""
        You are an expert agricultural assistant named AgroBrain.
        Use the following context to answer the user's question.
        If the answer is not in the context, say you don't know but offer general advice based on your training.
        
        Context:
        {context_text}
        
        User Question: {query}
        
        Answer (in Portuguese):
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return "Ocorreu um erro ao gerar a resposta."

    def _extract_recommendations(self, text: str) -> list:
        """Tenta extrair recomendações do texto gerado"""
        # Implementação simplificada
        recommendations = []
        lines = text.split('\n')
        for line in lines:
            if line.strip().startswith('-') or line.strip().startswith('*') or line.strip()[0:1].isdigit():
                recommendations.append(line.strip())
        return recommendations[:5]
    
    def _calculate_confidence(self, docs: list) -> float:
        """Calcula confiança na resposta baseado no conhecimento encontrado"""
        if not docs:
            return 0.3
        
        # Assumindo que se encontrou docs, a confiança é maior
        return min(0.5 + (len(docs) * 0.15), 0.95)
