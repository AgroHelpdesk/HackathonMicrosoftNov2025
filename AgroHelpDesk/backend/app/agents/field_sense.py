"""FieldSense agent module - Semantic Kernel version.

This agent classifies incoming agricultural messages to identify
category, severity, and related entities using Semantic Kernel.
"""

from typing import Any, Dict

from pydantic import ValidationError

from app.core.sk_base_agent import SKBaseAgent
from app.schemas.llm_responses import FieldSenseResponse
from app.schemas.orchestrator_schemas import AgentType
from app.utils.json_parser import parse_and_validate_json
from app.utils.logger import get_logger
from app.utils.response_builders import build_fallback_classification

logger = get_logger("field_sense")


class FieldSense(SKBaseAgent):
    """Agent responsible for classifying agricultural messages using Semantic Kernel."""

    # Confidence threshold for intention clarity
    CONFIDENCE_THRESHOLD = 0.55

    # System prompt for FieldSense
    SYSTEM_PROMPT = """Você é o agente FieldSense.

Sua função é interpretar mensagens de usuários do setor agrícola, normalmente operadores, agrônomos ou técnicos. 
Essas mensagens podem conter ruídos, gírias regionais, abreviações, erros de digitação, ou dados incompletos.

IMPORTANTE - Tratamento de cumprimentos:
Se a mensagem for APENAS um cumprimento (oi, olá, bom dia, boa tarde, boa noite, etc.) sem nenhuma dúvida ou problema:
- Classifique como categoria: "cumprimento"
- Confiança: 1.0
- Em observacoes: Gere uma resposta amigável e personalizada ao cumprimento (exemplo: "Olá! Fico feliz em ajudá-lo hoje!", "Bom dia! Como posso auxiliá-lo?")
- Não gere perguntas_sugeridas

Sua tarefa é:
1. Entender a intenção principal do usuário.
2. Classificar o tipo de ocorrência usando uma das categorias:
   - cumprimento (APENAS para saudações sem problema descrito)
   - falha_mecanica
   - fitossanidade
   - estoque_insumos
   - meteorologia
   - sistema_ti
   - rh_rural
   - manutencao_preventiva
   - operacao_maquina
   - duvida_operacional
   - outro

3. Extrair entidades relevantes:
   - máquina (ex.: CH670, S790, Magnum 340)
   - talhão (ex.: 15, 22B, 07)
   - sintomas (ex.: fumaça azul, barulho metálico, erro 307)
   - praga (ex.: percevejo-marrom, lagarta)
   - cultura (ex.: soja, milho, cana)
   - ação solicitada (reset, consulta, OS, desbloqueio)
   - local (opcional)
   - operador (se informado)

4. Avaliar sua confiança na interpretação (0.0 a 1.0):
   - 0.8-1.0: Informação SUFICIENTE para prosseguir (problema + identificador de máquina/local/contexto)
   - 0.5-0.7: Mensagem compreensível mas faltam múltiplos detalhes importantes
   - 0.0-0.4: Mensagem extremamente vaga ou ambígua
   
   IMPORTANTE - Critérios de SUFICIÊNCIA:
   - Se a mensagem menciona problema/sintoma E máquina/talhão/local → confiança >= 0.75
   - Se é uma resposta complementando informação anterior → confiança >= 0.7
   - Exemplos SUFICIENTES: "fumaça azul ch670", "talhão 15 percevejo", "colheitadeira parou"
   - Apenas mensagens MUITO vagas precisam de esclarecimento (ex: "ajuda", "problema")

5. Se a confiança for MENOR que 0.6, gere perguntas específicas para esclarecer:
   - Identifique exatamente quais informações CRÍTICAS estão faltando
   - Formule perguntas diretas e objetivas
   - NÃO peça esclarecimento se já houver problema + contexto mínimo

NUNCA invente informações que não estão na mensagem.
Se faltar informação, marque como null.

Responda APENAS com um JSON válido no seguinte formato:
{
  "intencao": "string descrevendo a intenção principal",
  "categoria": "uma das categorias listadas",
  "entidades": {
    "maquina": "string ou null",
    "talhao": "string ou null",
    "sintomas": "string ou null",
    "praga": "string ou null",
    "cultura": "string ou null",
    "acao_solicitada": "string ou null",
    "local": "string ou null",
    "operador": "string ou null"
  },
  "confianca": 0.0 a 1.0,
  "severidade": "baixa/media/alta",
  "observacoes": "string com notas adicionais ou null",
  "perguntas_sugeridas": ["pergunta 1", "pergunta 2"] ou null (apenas se confianca < 0.6)
}

Todas as repostas devem ser em inglês."""

    def __init__(self):
        """Initialize FieldSense agent with Semantic Kernel."""
        super().__init__(
            agent_name="FieldSense",
            agent_type=AgentType.FIELD_SENSE,
            system_prompt=self.SYSTEM_PROMPT
        )

    async def _process_internal(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify an agricultural message using Semantic Kernel.

        Args:
            message: User message to classify.
            context: Additional context.

        Returns:
            Dictionary with classification including:
            - intencao: Main intention
            - categoria: Message category
            - entidades: Extracted entities
            - confianca: Confidence score (0.0 to 1.0)
            - severidade: Severity level
            - perguntas_sugeridas: Questions if confidence < threshold
        """
        # Build context-aware prompt
        user_prompt = f'Classifique esta mensagem: "{message}"'
        
        # Add conversation context if available
        previous_fieldsense = context.get("fieldsense_data")
        if previous_fieldsense:
            categoria_anterior = previous_fieldsense.get("categoria")
            entidades_anteriores = previous_fieldsense.get("entidades", {})
            if categoria_anterior or entidades_anteriores:
                user_prompt += f"\n\nContexto da mensagem anterior: categoria={categoria_anterior}, entidades={entidades_anteriores}"
                user_prompt += "\nNOTA: Esta pode ser uma resposta complementando a mensagem anterior."

        try:
            # Use SK to invoke structured prompt
            response_dict = await self.invoke_structured_prompt(
                user_message=user_prompt,
                temperature=0.1,
                max_tokens=512
            )

            logger.info(f"SK classification response: {response_dict}")

            # Validate with Pydantic
            try:
                validated_response = FieldSenseResponse(**response_dict)
                result = validated_response.model_dump()
                result["raw_message"] = message
                result["interpretation_method"] = "semantic_kernel"

                logger.info(f"Classification result: categoria={result['categoria']}, confianca={result['confianca']}")
                return result

            except (ValidationError, ValueError) as e:
                logger.warning(f"Failed to validate SK response: {e}")
                return build_fallback_classification(message)
                
        except Exception as e:
            logger.exception(f"SK classification failed: {e}")
            return build_fallback_classification(message)
