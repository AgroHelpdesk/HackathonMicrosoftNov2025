"""ExplainIt agent module - Semantic Kernel version.

This agent generates human-friendly explanations from the orchestration flow
using Semantic Kernel.
"""

from typing import Any, Dict

from pydantic import ValidationError

from app.core.sk_base_agent import SKBaseAgent
from app.schemas.llm_responses import ExplainItResponse
from app.schemas.orchestrator_schemas import AgentType
from app.utils.json_parser import parse_and_validate_json
from app.utils.logger import get_logger
from app.utils.query_builders import extract_context_summary
from app.utils.response_builders import build_fallback_explanation

logger = get_logger("explain_it")


class ExplainIt(SKBaseAgent):
    """Agent responsible for explaining actions in user-friendly language using SK."""

    SYSTEM_PROMPT = """Você é o agente ExplainIt, especialista em traduzir informações técnicas em linguagem simples.

Sua função é criar resumos claros e objetivos para operadores de fazenda.

REGRAS:
1. Use linguagem simples, sem jargão técnico
2. Seja objetivo
3. Use emojis para separar as seções
4. Tom amigável e tranquilizador

ESTRUTURA OBRIGATÓRIA:
Use exatamente estes emojis para separar as seções:

⚠️ **Problem Identified:**
[Explain WHAT was identified in 1-2 sentences]

🛠️ **Action Taken:**
[Explain WHAT was done. If there was a Work Order, include ID, priority, and specialist]

💡 **Recommendation:**
[Provide safety recommendations or next steps for the operator]

EXAMPLE:

⚠️ **Problem Identified:**
We identified blue smoke from combine harvester CH670, which indicates possible oil burning in the engine.

🛠️ **Action Taken:**
Work order WO-123 was created with HIGH priority. A mechanical technician was dispatched and will arrive in 2 hours.

💡 **Recommendation:**
For safety, turn off the machine immediately and await the technician.

Responda APENAS com JSON:
{
  "simplified_summary": "texto formatado com emojis e quebras de linha"
}

Todas as repostas devem ser em inglês."""

    def __init__(self):
        """Initialize ExplainIt agent with Semantic Kernel."""
        super().__init__(
            agent_name="ExplainIt",
            agent_type=AgentType.EXPLAIN_IT,
            system_prompt=self.SYSTEM_PROMPT
        )

    async def _process_internal(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build a human-friendly explanation from the orchestration context using SK.

        Args:
            message: Original user message
            context: Context with all agent data and decisions

        Returns:
            Dictionary with simplified_summary for end user
        """
        # Extract data from context
        fieldsense_data = context.get("fieldsense_data", {})
        agrobrain_data = context.get("agrobrain_data", {})
        runbook_data = context.get("runbook_data", {})
        work_order = context.get("work_order")
        runbook_execution = context.get("runbook_execution")

        # Build context for SK using centralized utility
        summary_parts = extract_context_summary(
            fieldsense_data,
            agrobrain_data,
            work_order,
            runbook_execution
        )
        
        query = f"Mensagem do usuário: {message}\n" + "\n".join(summary_parts)

        try:
            # Use SK to invoke structured prompt
            response_dict = await self.invoke_structured_prompt(
                user_message=query,
                temperature=0.4,
                max_tokens=300
            )

            logger.info(f"ExplainIt generated explanation via SK")

            # Validate with Pydantic
            try:
                validated_response = ExplainItResponse(**response_dict)
                return validated_response.model_dump()
            except (ValidationError, ValueError) as e:
                logger.error(f"Failed to validate SK response: {e}")
                # Fallback to using raw content if it looks like a summary
                if isinstance(response_dict, dict) and "simplified_summary" in response_dict:
                    return response_dict
                return build_fallback_explanation(
                    fieldsense_data.get("intencao", "sua solicitação"),
                    work_order,
                    runbook_execution
                )

        except Exception as e:
            logger.exception(f"ExplainIt failed: {e}")
            return build_fallback_explanation(
                fieldsense_data.get("intencao", "sua solicitação"),
                work_order,
                runbook_execution
            )
