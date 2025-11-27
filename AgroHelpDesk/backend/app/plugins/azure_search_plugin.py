"""Azure Cognitive Search plugin for Semantic Kernel.

This plugin provides knowledge retrieval capabilities using Azure Cognitive Search.
"""

from typing import Annotated, Optional

from semantic_kernel.functions import kernel_function

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("azure_search_plugin")


class AzureSearchPlugin:
    """Plugin for Azure Cognitive Search integration."""
    
    def __init__(self):
        """Initialize Azure Search plugin."""
        self.search_endpoint = settings.AZURE_SEARCH_ENDPOINT
        self.search_key = settings.AZURE_SEARCH_KEY
        self.search_index = settings.AZURE_SEARCH_INDEX_NAME
        
        # Initialize search client if credentials are available
        self.search_client = None
        if self.search_endpoint and self.search_key and self.search_index:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential
            
            self.search_client = SearchClient(
                endpoint=self.search_endpoint,
                index_name=self.search_index,
                credential=AzureKeyCredential(self.search_key)
            )
            logger.info(f"Azure Search client initialized for index: {self.search_index}")
        else:
            logger.warning("Azure Search credentials not configured - search will use fallback")
    
    @kernel_function(
        name="search_knowledge_base",
        description="Search the agricultural knowledge base for relevant information"
    )
    async def search_knowledge_base(
        self,
        query: Annotated[str, "The search query"],
        top: Annotated[int, "Number of results to return"] = 5
    ) -> Annotated[str, "Search results as formatted text"]:
        """Search the knowledge base for relevant information.
        
        Args:
            query: Search query
            top: Number of results to return
            
        Returns:
            Formatted search results
        """
        logger.info(f"Searching knowledge base: query='{query}', top={top}")
        
        if not self.search_client:
            logger.warning("Search client not available - returning fallback")
            return self._get_fallback_knowledge(query)
        
        try:
            # Perform semantic search
            results = self.search_client.search(
                search_text=query,
                top=top,
                # Remove specific select to avoid errors if fields don't exist
                select=["*"],
                query_type="semantic" if hasattr(self.search_client, "semantic_configuration") else "simple"
            )
            
            # Format results
            formatted_results = []
            for idx, result in enumerate(results, 1):
                # Try to find title field
                title = result.get("title") or result.get("name") or result.get("id") or "Sem título"
                
                # Try to find content field (check common names)
                content = (
                    result.get("content") or 
                    result.get("text") or 
                    result.get("description") or 
                    result.get("chunk") or
                    str(result) # Fallback to string representation if no content field found
                )
                
                # Try to find category
                category = result.get("category") or result.get("source") or ""
                
                formatted_results.append(
                    f"[{idx}] {title}\n"
                    f"Categoria: {category}\n"
                    f"Conteúdo: {content}\n"
                )
            
            if not formatted_results:
                logger.info("No results found in knowledge base")
                return "Nenhum resultado encontrado na base de conhecimento."
            
            logger.info(f"Found {len(formatted_results)} results")
            return "\n---\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return self._get_fallback_knowledge(query)
    
    @kernel_function(
        name="check_procedure_exists",
        description="Check if a procedure exists in the knowledge base"
    )
    async def check_procedure_exists(
        self,
        procedure_name: Annotated[str, "Name or description of the procedure"]
    ) -> Annotated[bool, "True if procedure exists, False otherwise"]:
        """Check if a procedure exists in the knowledge base.
        
        Args:
            procedure_name: Name or description of the procedure
            
        Returns:
            True if procedure exists, False otherwise
        """
        logger.info(f"Checking if procedure exists: {procedure_name}")
        
        if not self.search_client:
            # Fallback: assume common procedures exist
            common_procedures = [
                "reset", "reiniciar", "manutenção", "calibração",
                "limpeza", "troca de óleo", "filtro"
            ]
            exists = any(proc in procedure_name.lower() for proc in common_procedures)
            logger.info(f"Fallback check: procedure exists = {exists}")
            return exists
        
        try:
            results = self.search_client.search(
                search_text=procedure_name,
                top=1,
                select=["*"]
            )
            
            # Check if we got any results
            has_results = False
            for _ in results:
                has_results = True
                break
            
            logger.info(f"Procedure exists: {has_results}")
            return has_results
            
        except Exception as e:
            logger.error(f"Procedure check failed: {e}", exc_info=True)
            return False
    
    def _get_fallback_knowledge(self, query: str) -> str:
        """Get fallback knowledge when search is not available.
        
        Args:
            query: Search query
            
        Returns:
            Fallback knowledge text
        """
        # Simple keyword-based fallback
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["fumaça", "smoke", "azul", "blue"]):
            return """
[1] Fumaça Azul em Motores Diesel
Categoria: Manutenção Mecânica
Conteúdo: Fumaça azul indica queima de óleo. Possíveis causas: anéis de pistão gastos, 
guias de válvula desgastadas, nível de óleo acima do recomendado. Verificar consumo de óleo 
e realizar inspeção mecânica.
"""
        
        elif any(word in query_lower for word in ["percevejo", "praga", "lagarta"]):
            return """
[1] Controle de Pragas em Soja
Categoria: Fitossanidade
Conteúdo: Para controle de percevejos, realizar monitoramento semanal. Nível de ação: 
2 percevejos por metro. Aplicar inseticida registrado conforme recomendação agronômica.
"""
        
        else:
            return """
Base de conhecimento não disponível no momento. 
Recomenda-se consultar manual técnico ou contatar suporte especializado.
"""
