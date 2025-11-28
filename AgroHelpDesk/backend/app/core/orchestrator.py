"""Orchestrator module.

This module coordinates the flow between all agents following the decision diagram:
1. FieldSense: Classify message and check intention clarity
2. If unclear -> Ask for clarification
3. If clear -> FarmOps: Gather context
4. AgroBrain: Retrieve knowledge
5. If procedure unknown -> Escalate to human
6. If known -> RunbookMaster: Check if can automate
7. If can automate -> Execute runbook
8. If cannot automate -> Create work order
9. ExplainIt: Generate user-friendly explanation
"""

import time
from typing import Any, Dict, List

from app.agents.field_sense import FieldSense
from app.agents.farm_ops import FarmOps
from app.agents.agro_brain import AgroBrain
from app.agents.runbook_master import RunbookMaster
from app.agents.explain_it import ExplainIt
from app.schemas.orchestrator_schemas import (
    AgentResponseSchema,
    ClarificationRequest,
    DecisionType,
    FlowDecision,
    FlowState,
    OrchestratorResponse,
)
from app.services.session_store import get_session
from app.utils.logger import get_logger

logger = get_logger("orchestrator")


class Orchestrator:
    """Main orchestrator coordinating all agents in the decision flow."""

    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.field_sense = FieldSense()
        self.farm_ops = FarmOps()
        self.agro_brain = AgroBrain()
        self.runbook_master = RunbookMaster()
        self.explain_it = ExplainIt()

    async def process(
        self, message: str, session_id: str | None = None
    ) -> OrchestratorResponse:
        """Process a user message through the complete agent flow.

        Args:
            message: User message to process
            session_id: Optional session ID for context

        Returns:
            OrchestratorResponse with complete orchestration results
        """
        start_time = time.time()
        
        logger.info(f"Orchestrator starting for message: {message[:100]}...")
        
        agent_responses: List[AgentResponseSchema] = []
        decisions: List[FlowDecision] = []
        context: Dict[str, Any] = {"session_id": session_id}
        
        # Retrieve previous session context if available
        if session_id:
            session = await get_session(session_id)
            if session:
                messages = session.get("messages", [])
                # Get last agent response from session to preserve context
                for msg in reversed(messages):
                    extra = msg.get("extra", {})
                    if extra.get("fieldsense_data"):
                        context["fieldsense_data"] = extra["fieldsense_data"]
                        logger.info(f"Restored previous FieldSense context from session: {context['fieldsense_data'].get('categoria')}")
                        break
        
        try:
            # STEP 1: FieldSense - Classify message and check intention clarity
            logger.info("STEP 1: FieldSense classification")
            fieldsense_response = await self.field_sense.process(message, context)
            agent_responses.append(fieldsense_response)
            
            if not fieldsense_response.success:
                return self._build_error_response(
                    "Erro na classificação da mensagem",
                    agent_responses,
                    decisions,
                    start_time
                )
            
            fieldsense_data = fieldsense_response.data
            context["fieldsense_data"] = fieldsense_data
            
            confianca = fieldsense_data.get("confianca", 0.0)
            categoria = fieldsense_data.get("categoria", "outro")
            perguntas_sugeridas = fieldsense_data.get("perguntas_sugeridas")
            
            # SPECIAL CASE: Handle greetings
            if categoria == "cumprimento":
                logger.info("Greeting detected - responding with friendly prompt")
                
                # Get AI-generated greeting response from FieldSense
                greeting_response = fieldsense_data.get("observacoes", "Olá! Fico feliz em ajudá-lo!")
                
                decisions.append(FlowDecision(
                    decision_type=DecisionType.INTENTION_UNCLEAR,
                    agent_name="FieldSense",
                    reason="Cumprimento recebido - aguardando descrição do problema",
                    confidence=confianca,
                    next_state=FlowState.NEEDS_CLARIFICATION
                ))
                
                clarification = ClarificationRequest(
                    reason="Initial greeting",
                    missing_info=["Description of the problem or question"],
                    suggested_questions=[
                        greeting_response,
                        "What is your question or need?",
                        "Can you tell me what is happening?"
                    ],
                    current_understanding="Greeting received"
                )
                
                return OrchestratorResponse(
                    success=True,
                    message="\n".join(clarification.suggested_questions),
                    flow_state=FlowState.NEEDS_CLARIFICATION,
                    decisions=decisions,
                    agent_responses=agent_responses,
                    clarification=clarification,
                    context=context,
                    total_execution_time_ms=int((time.time() - start_time) * 1000)
                )
            
            # DECISION POINT 1: Intention clear?
            if confianca < FieldSense.CONFIDENCE_THRESHOLD:
                # Intention unclear -> Ask for clarification
                logger.info(f"Intention unclear (confidence={confianca}), requesting clarification")
                
                decisions.append(FlowDecision(
                    decision_type=DecisionType.INTENTION_UNCLEAR,
                    agent_name="FieldSense",
                    reason=f"Confiança baixa ({confianca:.2f}) - informações insuficientes",
                    confidence=confianca,
                    next_state=FlowState.NEEDS_CLARIFICATION
                ))
                
                clarification = ClarificationRequest(
                    reason=f"Precisamos de mais informações para entender melhor (confiança: {confianca:.1%})",
                    missing_info=self._identify_missing_info(fieldsense_data),
                    suggested_questions=perguntas_sugeridas or [
                        "Pode fornecer mais detalhes?",
                        "Em qual máquina ou local isso está ocorrendo?"
                    ],
                    current_understanding=fieldsense_data.get("intencao", "Não identificado")
                )
                
                return OrchestratorResponse(
                    success=True,
                    message="\n".join(clarification.suggested_questions),
                    flow_state=FlowState.NEEDS_CLARIFICATION,
                    decisions=decisions,
                    agent_responses=agent_responses,
                    clarification=clarification,
                    work_order=None,
                    runbook_execution=None,
                    total_execution_time_ms=(time.time() - start_time) * 1000
                )
            
            # Intention is clear
            decisions.append(FlowDecision(
                decision_type=DecisionType.INTENTION_CLEAR,
                agent_name="FieldSense",
                reason=f"Intenção identificada com confiança {confianca:.2f}",
                confidence=confianca,
                next_state=FlowState.GATHERING_CONTEXT
            ))
            
            # STEP 2: FarmOps - Gather operational context
            logger.info("STEP 2: FarmOps context enrichment")
            farmops_response = await self.farm_ops.process(message, context)
            agent_responses.append(farmops_response)
            
            if farmops_response.success:
                context["farmops_data"] = farmops_response.data
            
            # STEP 3: AgroBrain - Retrieve knowledge
            logger.info("STEP 3: AgroBrain knowledge retrieval")
            agrobrain_response = await self.agro_brain.process(message, context)
            agent_responses.append(agrobrain_response)
            
            if not agrobrain_response.success:
                return self._build_error_response(
                    "Erro na busca de conhecimento",
                    agent_responses,
                    decisions,
                    start_time
                )
            
            agrobrain_data = agrobrain_response.data
            context["agrobrain_data"] = agrobrain_data
            
            procedimento_conhecido = agrobrain_data.get("procedimento_conhecido", False)
            
            # DECISION POINT 2: Procedure known?
            if not procedimento_conhecido:
                # Procedure unknown -> Escalate to human
                logger.info("Procedure unknown, escalating to human")
                
                decisions.append(FlowDecision(
                    decision_type=DecisionType.PROCEDURE_UNKNOWN,
                    agent_name="AgroBrain",
                    reason="Procedimento não encontrado na base de conhecimento",
                    confidence=0.0,
                    next_state=FlowState.HUMAN_ESCALATION
                ))
                
                # Generate explanation
                explainit_response = await self.explain_it.process(message, context)
                agent_responses.append(explainit_response)
                
                explanation = explainit_response.data.get(
                    "simplified_summary",
                    "Não encontramos procedimento específico. Um especialista será notificado."
                )
                
                return OrchestratorResponse(
                    success=True,
                    message=explanation,
                    flow_state=FlowState.HUMAN_ESCALATION,
                    decisions=decisions,
                    agent_responses=agent_responses,
                    work_order=None,
                    clarification=None,
                    runbook_execution=None,
                    total_execution_time_ms=(time.time() - start_time) * 1000
                )
            
            # Procedure is known
            decisions.append(FlowDecision(
                decision_type=DecisionType.PROCEDURE_KNOWN,
                agent_name="AgroBrain",
                reason="Procedimento encontrado na base de conhecimento",
                confidence=0.8,
                next_state=FlowState.AUTOMATION_CHECK
            ))
            
            # STEP 4: RunbookMaster - Decide automation vs work order
            logger.info("STEP 4: RunbookMaster automation decision")
            runbook_response = await self.runbook_master.process(message, context)
            agent_responses.append(runbook_response)
            
            if not runbook_response.success:
                return self._build_error_response(
                    "Erro na decisão de automação",
                    agent_responses,
                    decisions,
                    start_time
                )
            
            runbook_data = runbook_response.data
            context["runbook_data"] = runbook_data
            
            action = runbook_data.get("action")
            can_automate = runbook_data.get("can_automate", False)
            work_order = runbook_data.get("work_order")
            runbook_execution = runbook_data.get("runbook_execution")
            
            # Add decision based on action
            if action == "automate":
                decisions.append(FlowDecision(
                    decision_type=DecisionType.CAN_AUTOMATE,
                    agent_name="RunbookMaster",
                    reason="Procedimento pode ser automatizado",
                    confidence=0.9,
                    next_state=FlowState.RUNBOOK_EXECUTION
                ))
                
                if runbook_execution and runbook_execution.get("success"):
                    decisions.append(FlowDecision(
                        decision_type=DecisionType.EXECUTION_SUCCESS,
                        agent_name="RunbookMaster",
                        reason="Runbook executado com sucesso",
                        confidence=1.0,
                        next_state=FlowState.EXECUTION_SUCCESS
                    ))
                    final_state = FlowState.EXECUTION_SUCCESS
                else:
                    decisions.append(FlowDecision(
                        decision_type=DecisionType.EXECUTION_FAILED,
                        agent_name="RunbookMaster",
                        reason="Falha na execução do runbook",
                        confidence=0.5,
                        next_state=FlowState.EXECUTION_FAILED
                    ))
                    final_state = FlowState.EXECUTION_FAILED
            
            elif action == "create_os":
                decisions.append(FlowDecision(
                    decision_type=DecisionType.CANNOT_AUTOMATE,
                    agent_name="RunbookMaster",
                    reason="Requer intervenção especializada",
                    confidence=0.8,
                    next_state=FlowState.WORK_ORDER_CREATED
                ))
                final_state = FlowState.WORK_ORDER_CREATED
            
            else:  # escalate
                decisions.append(FlowDecision(
                    decision_type=DecisionType.CANNOT_AUTOMATE,
                    agent_name="RunbookMaster",
                    reason="Encaminhado para análise humana",
                    confidence=0.7,
                    next_state=FlowState.HUMAN_ESCALATION
                ))
                final_state = FlowState.HUMAN_ESCALATION
            
            # Store work_order and runbook_execution in context for ExplainIt
            if work_order:
                context["work_order"] = work_order
            if runbook_execution:
                context["runbook_execution"] = runbook_execution
            
            # STEP 5: ExplainIt - Generate user-friendly explanation
            logger.info("STEP 5: ExplainIt generating explanation")
            explainit_response = await self.explain_it.process(message, context)
            agent_responses.append(explainit_response)
            
            explanation = explainit_response.data.get(
                "simplified_summary",
                runbook_data.get("message", "Sua solicitação foi processada.")
            )
            
            # Mark flow as COMPLETED after ExplainIt finishes
            final_state = FlowState.COMPLETED
            decisions.append(FlowDecision(
                decision_type=DecisionType.EXECUTION_SUCCESS,
                agent_name="ExplainIt",
                reason="Explicação gerada e atendimento finalizado",
                confidence=1.0,
                next_state=FlowState.COMPLETED
            ))
            
            total_time = (time.time() - start_time) * 1000
            logger.info(f"Orchestrator completed in {total_time:.2f}ms with state {final_state}")
            
            return OrchestratorResponse(
                success=True,
                message=explanation,
                flow_state=final_state,
                decisions=decisions,
                agent_responses=agent_responses,
                work_order=work_order,
                clarification=None,
                runbook_execution=runbook_execution,
                total_execution_time_ms=total_time
            )
        
        except Exception as e:
            logger.exception(f"Orchestrator failed: {e}")
            return self._build_error_response(
                f"Erro no processamento: {str(e)}",
                agent_responses,
                decisions,
                start_time
            )
    
    def _identify_missing_info(self, fieldsense_data: Dict[str, Any]) -> List[str]:
        """Identify what information is missing from the classification."""
        missing = []
        entidades = fieldsense_data.get("entidades", {})
        
        if not entidades.get("maquina") and not entidades.get("local"):
            missing.append("máquina ou local")
        
        if not entidades.get("sintomas"):
            missing.append("sintomas ou descrição do problema")
        
        if not missing:
            missing.append("detalhes adicionais")
        
        return missing
    
    def _build_error_response(
        self,
        error_message: str,
        agent_responses: List[AgentResponseSchema],
        decisions: List[FlowDecision],
        start_time: float
    ) -> OrchestratorResponse:
        """Build error response."""
        return OrchestratorResponse(
            success=False,
            message=f"⚠️ {error_message}. Por favor, tente novamente ou contate o suporte.",
            flow_state=FlowState.HUMAN_ESCALATION,
            decisions=decisions,
            agent_responses=agent_responses,
            work_order=None,
            clarification=None,
            runbook_execution=None,
            total_execution_time_ms=(time.time() - start_time) * 1000
        )

