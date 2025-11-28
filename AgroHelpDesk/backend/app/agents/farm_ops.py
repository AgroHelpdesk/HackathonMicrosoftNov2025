"""FarmOps agent module - Semantic Kernel version.

This agent aggregates operational context and data to enrich the classification.
"""

from typing import Any, Dict

from app.core.sk_base_agent import SKBaseAgent
from app.schemas.orchestrator_schemas import AgentType
from app.services.session_store import get_session
from app.utils.logger import get_logger

logger = get_logger("farm_ops")


class FarmOps(SKBaseAgent):
    """Agent responsible for enriching context with operational data using SK."""

    # Simple system prompt (this agent doesn't need LLM calls)
    SYSTEM_PROMPT = """Você é o agente FarmOps, responsável por enriquecer o contexto operacional."""

    def __init__(self):
        """Initialize FarmOps agent with Semantic Kernel."""
        super().__init__(
            agent_name="FarmOps",
            agent_type=AgentType.FARM_OPS,
            system_prompt=self.SYSTEM_PROMPT
        )

    async def _process_internal(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich context with operational data.

        Args:
            message: User message
            context: Additional context (should include fieldsense_data)

        Returns:
            Dictionary with enriched context including:
            - classification: Original classification from FieldSense
            - session_metadata: Session metadata if available
            - history: Conversation history if available
            - operational_data: Any operational data fetched
        """
        # Extract classification from context
        fieldsense_data = context.get("fieldsense_data", {})
        session_id = context.get("session_id")

        enriched_context = {
            "classification": fieldsense_data,
            "session_metadata": None,
            "history": [],
            "operational_data": {},
            "location": None,
            "machine_info": None,
            "field_info": None
        }

        # Get session data if available
        if session_id:
            session = await get_session(session_id)
            if session:
                enriched_context["session_metadata"] = session.get("metadata", {})
                enriched_context["history"] = session.get("messages", [])
                logger.info(f"Retrieved session data for {session_id}")

        # Extract entities for context enrichment
        entidades = fieldsense_data.get("entidades", {})
        
        # Extract location from entities
        talhao = entidades.get("talhao")
        local = entidades.get("local")
        if talhao:
            enriched_context["location"] = talhao
            logger.info(f"Location identified: {talhao}")
        elif local:
            enriched_context["location"] = local
            logger.info(f"Location identified: {local}")

        # Extract machine information
        maquina = entidades.get("maquina")
        if maquina:
            enriched_context["machine_info"] = {
                "id": maquina,
                "sintomas": entidades.get("sintomas")
            }
            logger.info(f"Machine identified: {maquina}")

        # TODO: Fetch additional operational data using SK plugins:
        # - Machine telemetry from database
        # - Field/crop data
        # - Weather data
        # - Maintenance history
        # - Operator information

        logger.info(f"FarmOps enriched context with keys: {list(enriched_context.keys())}")
        return enriched_context
