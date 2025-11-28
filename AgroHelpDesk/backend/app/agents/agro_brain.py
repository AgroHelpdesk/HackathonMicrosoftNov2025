"""AgroBrain agent module - Semantic Kernel version.

This agent retrieves agricultural knowledge using Azure AI Search
with RAG (Retrieval-Augmented Generation) pattern via Semantic Kernel.
"""

from typing import Any, Dict

from pydantic import ValidationError

from app.core.sk_base_agent import SKBaseAgent
from app.plugins.azure_search_plugin import AzureSearchPlugin
from app.schemas.llm_responses import AgroBrainResponse
from app.schemas.orchestrator_schemas import AgentType
from app.utils.json_parser import parse_and_validate_json
from app.utils.logger import get_logger
from app.utils.query_builders import build_enhanced_user_query, build_search_query_from_context
from app.utils.response_builders import (
    build_error_response,
    build_fallback_response,
    build_insufficient_info_response,
)

logger = get_logger("agro_brain")


class AgroBrain(SKBaseAgent):
    """Agent responsible for retrieving agricultural knowledge using RAG with SK.
    
    Uses Azure AI Search + Semantic Kernel to provide:
    - Technical agricultural knowledge
    - Machine telemetry analysis
    - Mechanical maintenance guidance
    - Safety protocols from manufacturers
    - Agricultural best practices
    - Phytosanitary and pest management
    - Weather recommendations
    """

    # System prompt for AgroBrain
    SYSTEM_PROMPT = """Você é o agente AgroBrain.

Você é um especialista técnico em:
- agronomia e práticas agrícolas
- telemetria de máquinas agrícolas
- manutenção mecânica de colheitadeiras, tratores e plantadeiras
- protocolos de segurança de fabricantes (John Deere, CNH, AGCO)
- boas práticas agrícolas (BPA)
- fitossanidade e manejo de pragas
- recomendações meteorológicas
- procedimentos operacionais da fazenda

Sua função é:
1. Analisar o contexto de busca fornecido da base de conhecimento.
2. Não inventar dados de máquina, telemetria ou sintomas que não foram informados.
3. Avaliar se existe um PROCEDIMENTO CONHECIDO e DOCUMENTADO na base de conhecimento:
   - procedimento_conhecido: true se há documentação clara e completa
   - procedimento_conhecido: false se não há informação suficiente ou procedimento não documentado
4. Avaliar o nível de complexidade do procedimento:
   - "baixo": procedimento simples, poucos passos, baixo risco
   - "medio": procedimento moderado, requer atenção, risco controlado
   - "alto": procedimento complexo, muitos passos, alto risco ou requer especialista
5. Indicar se requer especialista humano:
   - requer_especialista: true se o procedimento é crítico, perigoso ou muito complexo
   - requer_especialista: false se pode ser executado com orientação
6. Explicar com precisão técnica:
   - possíveis causas
   - riscos
   - qual protocolo do fabricante se aplica
   - recomendações de segurança

Nunca executar automação — apenas fornecer conhecimento.
Se a busca não retornar dados suficientes, marque procedimento_conhecido como false.

Formato do output (JSON válido):
{
  "conhecimento": "...",
  "riscos": "...",
  "recomendacoes": "...",
  "fontes": ["id1", "id2"],
  "procedimento_conhecido": true ou false,
  "nivel_complexidade": "baixo" ou "medio" ou "alto",
  "requer_especialista": true ou false
}

Seja preciso, técnico e cite somente dados encontrados na busca.

Todas as repostas devem ser em inglês."""

    def __init__(self):
        """Initialize AgroBrain agent with Semantic Kernel."""
        super().__init__(
            agent_name="AgroBrain",
            agent_type=AgentType.AGRO_BRAIN,
            system_prompt=self.SYSTEM_PROMPT
        )
        
        # Initialize Azure Search plugin
        self.search_plugin = AzureSearchPlugin()
        
        # Add plugin to kernel
        self.kernel.add_plugin(self.search_plugin, plugin_name="AzureSearch")

    async def _process_internal(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message using AI Search RAG + SK for technical expertise.
        
        Args:
            message: User message
            context: Additional context (should include FieldSense and FarmOps data)
            
        Returns:
            Dict with technical knowledge, risks, recommendations, and sources
        """
        try:
            # Extract data from context
            fieldsense_data = context.get("fieldsense_data", {})
            farmops_data = context.get("farmops_data", {})

            # Build search query from available data
            search_query = build_search_query_from_context(message, fieldsense_data, farmops_data)
            
            logger.info(f"AgroBrain search query: {search_query}")
            
            # Use SK plugin to search
            search_results_text = await self.search_plugin.search_knowledge_base(
                query=search_query,
                top=5
            )
            
            if not search_results_text or "Nenhum resultado" in search_results_text:
                logger.warning("No search results found")
                return build_insufficient_info_response()
            
            logger.info(f"Search results retrieved: {len(search_results_text)} chars")
            
            # Build enhanced user query with context
            user_query = build_enhanced_user_query(
                message,
                fieldsense_data,
                farmops_data,
                "\nForneça análise técnica detalhada com base nos documentos encontrados."
            )
            
            # Add search results to the query
            full_query = f"""{user_query}

CONTEXTO DA BASE DE CONHECIMENTO:
{search_results_text}

Use APENAS as informações fornecidas no contexto acima para responder.
Se o contexto não contiver informações suficientes, marque procedimento_conhecido como false."""
            
            logger.info("Calling SK with RAG context...")
            
            # Use SK to invoke structured prompt
            response_dict = await self.invoke_structured_prompt(
                user_message=full_query,
                temperature=0.3,
                max_tokens=1000
            )
            
            logger.info(f"SK RAG response received")
            
            # Validate with Pydantic
            try:
                validated_response = AgroBrainResponse(**response_dict)
                
                # Convert to dict and add metadata
                parsed_data = validated_response.model_dump()
                parsed_data["method"] = "semantic_kernel_rag"
                parsed_data["search_results_count"] = search_results_text.count("[")  # Approximate count
                
                logger.info(f"AgroBrain provided knowledge with {len(parsed_data.get('fontes', []))} sources")
                
                return parsed_data
                
            except (ValidationError, ValueError) as e:
                logger.error(f"Failed to validate SK response: {e}")
                logger.debug(f"Raw response: {response_dict}")
                return build_fallback_response(str(response_dict))
        
        except Exception as e:
            logger.error(f"Error in AgroBrain processing: {e}", exc_info=True)
            return build_error_response(str(e))
