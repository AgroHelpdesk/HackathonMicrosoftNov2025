"""RunbookMaster agent module - Semantic Kernel version.

This agent decides on automation vs human escalation
and executes runbooks when appropriate using SK plugins.
"""

import random
import uuid
from datetime import datetime
from typing import Any, Dict

from app.core.sk_base_agent import SKBaseAgent
from app.config.agent_config import (
    RUNBOOK_DEFINITIONS,
    get_priority_for_severity,
    get_runbook_definition,
    get_specialist_for_category,
    map_category_to_schema,
)
from app.core.automation import trigger_runbook
from app.plugins.runbook_plugin import RunbookPlugin
from app.plugins.work_order_plugin import WorkOrderPlugin
from app.schemas.orchestrator_schemas import (
    AgentType,
    DecisionType,
    RunbookExecution,
    WorkOrder,
)
from app.utils.logger import get_logger

logger = get_logger("runbook_master")


class RunbookMaster(SKBaseAgent):
    """Agent responsible for automation decisions and runbook execution using SK."""

    # System prompt for RunbookMaster
    SYSTEM_PROMPT = """Você é o agente RunbookMaster, responsável por decisões de automação."""

    def __init__(self):
        """Initialize RunbookMaster agent with Semantic Kernel."""
        super().__init__(
            agent_name="RunbookMaster",
            agent_type=AgentType.RUNBOOK_MASTER,
            system_prompt=self.SYSTEM_PROMPT
        )
        
        # Initialize plugins
        self.runbook_plugin = RunbookPlugin()
        self.work_order_plugin = WorkOrderPlugin()
        
        # Add plugins to kernel
        self.kernel.add_plugin(self.runbook_plugin, plugin_name="Runbook")
        self.kernel.add_plugin(self.work_order_plugin, plugin_name="WorkOrder")

    async def _process_internal(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on automation vs escalation and execute if appropriate.

        Args:
            message: User message
            context: Context including fieldsense_data, farmops_data, agrobrain_data

        Returns:
            Dictionary with decision including:
            - decision_type: Type of decision made
            - action: automate/escalate/create_os
            - message: User-facing message
            - can_automate: Whether automation is possible
            - work_order: WorkOrder object if created
            - runbook_execution: RunbookExecution object if executed
        """
        fieldsense_data = context.get("fieldsense_data", {})
        agrobrain_data = context.get("agrobrain_data", {})
        
        categoria = fieldsense_data.get("categoria", "")
        severidade = fieldsense_data.get("severidade", "media")
        procedimento_conhecido = agrobrain_data.get("procedimento_conhecido", False)
        requer_especialista = agrobrain_data.get("requer_especialista", True)
        nivel_complexidade = agrobrain_data.get("nivel_complexidade", "medio")

        logger.info(
            f"RunbookMaster decision inputs: categoria={categoria}, "
            f"procedimento_conhecido={procedimento_conhecido}, "
            f"requer_especialista={requer_especialista}"
        )

        # Decision flow following the diagram

        # 1. Check if procedure is known
        if not procedimento_conhecido:
            # Unknown procedure -> escalate to human
            return self._escalate_to_human(fieldsense_data, "Procedimento não encontrado na base de conhecimento")

        # 2. Procedure is known, check if can automate
        can_automate = self._can_automate(categoria, severidade, nivel_complexidade, requer_especialista)

        if can_automate:
            # Try to execute runbook
            runbook_result = await self._execute_runbook(categoria, fieldsense_data)
            
            if runbook_result["success"]:
                return {
                    "decision_type": DecisionType.EXECUTION_SUCCESS,
                    "action": "automate",
                    "message": f"✓ Procedimento executado com sucesso: {runbook_result['runbook_name']}",
                    "can_automate": True,
                    "runbook_execution": runbook_result,
                    "work_order": None
                }
            else:
                # Execution failed -> escalate
                return self._escalate_to_human(
                    fieldsense_data,
                    f"Falha na execução automática: {runbook_result.get('error_message', 'Erro desconhecido')}"
                )
        else:
            # Cannot automate -> create work order and assign specialist
            return await self._create_work_order(fieldsense_data, agrobrain_data)

    def _can_automate(
        self,
        categoria: str,
        severidade: str,
        nivel_complexidade: str,
        requer_especialista: bool
    ) -> bool:
        """Determine if procedure can be automated."""
        # Cannot automate if requires specialist
        if requer_especialista:
            logger.info("Cannot automate: requires specialist")
            return False
        
        # Cannot automate if high complexity
        if nivel_complexidade == "alto":
            logger.info("Cannot automate: high complexity")
            return False
        
        # Cannot automate critical failures
        if severidade == "alta" and "falha" in categoria.lower():
            logger.info("Cannot automate: critical failure")
            return False
        
        # Can automate simple queries and low-risk operations
        if categoria in ["estoque_insumos", "duvida_operacional"] and nivel_complexidade == "baixo":
            logger.info("Can automate: simple operation")
            return True
        
        # Default: cannot automate
        return False

    async def _execute_runbook(
        self,
        categoria: str,
        fieldsense_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute appropriate runbook based on category using SK plugin."""
        # Select runbook based on category
        runbook_name = None
        
        if "estoque" in categoria.lower():
            runbook_name = "consultar_estoque"
        elif "sistema_ti" in categoria.lower() or "erro" in str(fieldsense_data.get("entidades", {}).get("sintomas", "")).lower():
            runbook_name = "reset_sistema"
        else:
            runbook_name = "inspecao_basica"
        
        runbook = get_runbook_definition(runbook_name)
        
        if not runbook:
            return {
                "runbook_name": "Desconhecido",
                "steps_completed": 0,
                "total_steps": 0,
                "success": False,
                "execution_log": [],
                "error_message": "Runbook não encontrado"
            }
        
        # Simulate execution
        try:
            # Call actual automation if available
            result = await trigger_runbook(runbook_name, {"entidades": fieldsense_data.get("entidades", {})})
            
            # Simulate success/failure (90% success for easy, 70% for medium)
            success_rate = 0.9 if runbook["difficulty"] == "easy" else 0.7
            success = random.random() < success_rate
            
            steps = runbook["steps"]
            execution_log = []
            steps_completed = 0
            
            for i, step in enumerate(steps, 1):
                if success or i < len(steps):
                    execution_log.append(f"✓ Passo {i}: {step}")
                    steps_completed = i
                else:
                    execution_log.append(f"✗ Passo {i}: {step} - FALHOU")
                    break
            
            return {
                "runbook_name": runbook["name"],
                "steps_completed": steps_completed,
                "total_steps": len(steps),
                "success": success,
                "execution_log": execution_log,
                "error_message": None if success else f"Falha no passo {steps_completed + 1}"
            }
        
        except Exception as e:
            logger.exception(f"Runbook execution failed: {e}")
            return {
                "runbook_name": runbook["name"],
                "steps_completed": 0,
                "total_steps": len(runbook["steps"]),
                "success": False,
                "execution_log": [f"✗ Erro na execução: {str(e)}"],
                "error_message": str(e)
            }

    async def _create_work_order(
        self,
        fieldsense_data: Dict[str, Any],
        agrobrain_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create work order and assign to specialist using SK plugin.
        
        The WorkOrderPlugin handles Cosmos DB persistence automatically via async call.
        """
        entidades = fieldsense_data.get("entidades", {})
        categoria = fieldsense_data.get("categoria", "outro")
        severidade = fieldsense_data.get("severidade", "media")
        
        # Map FieldSense category to WorkOrder schema category
        schema_category = map_category_to_schema(categoria)
        
        # Get specialist and priority from config
        specialist = get_specialist_for_category(categoria)
        priority = get_priority_for_severity(severidade)
        
        # Build description
        title = fieldsense_data.get('intencao', 'Ocorrência não especificada')
        description = f"{title}. {agrobrain_data.get('conhecimento', '')}"
        
        # Call plugin's kernel function to create and persist work order
        try:
            order_id = await self.work_order_plugin.create_work_order(
                title=title,
                description=description,
                category=schema_category,  # Use mapped category
                priority=priority,
                machine=entidades.get("maquina"),
                location=entidades.get("talhao")
            )
            
            logger.info(
                f"✅ Work order {order_id} created and persisted via plugin to Cosmos DB. "
                f"Assigned to {specialist}."
            )
            
            # Build work order dict for response
            work_order_dict = self.work_order_plugin.build_work_order_dict(
                title=title,
                description=description,
                category=categoria,
                priority=priority,
                machine=entidades.get("maquina"),
                location=entidades.get("talhao"),
                symptoms=entidades.get("sintomas"),
                assigned_specialist=specialist,
                estimated_time_hours=2.0
            )
            work_order_dict["order_id"] = order_id  # Use the ID from Cosmos DB
            
        except Exception as e:
            logger.error(f"❌ Error creating work order via plugin: {e}")
            # Fallback: create local work order
            work_order_dict = self.work_order_plugin.build_work_order_dict(
                title=title,
                description=description,
                category=categoria,
                priority=priority,
                machine=entidades.get("maquina"),
                location=entidades.get("talhao"),
                symptoms=entidades.get("sintomas"),
                assigned_specialist=specialist,
                estimated_time_hours=2.0
            )
            order_id = work_order_dict["order_id"]
        
        logger.info(
            f"Work order {order_id} created and assigned to {specialist}. "
            f"Persistence handled by WorkOrderPlugin."
        )
        
        return {
            "decision_type": DecisionType.CANNOT_AUTOMATE,
            "action": "create_os",
            "message": f"📋 Ordem de serviço {order_id} criada e encaminhada para {specialist}.",
            "can_automate": False,
            "work_order": work_order_dict,
            "runbook_execution": None
        }

    def _escalate_to_human(
        self,
        fieldsense_data: Dict[str, Any],
        reason: str
    ) -> Dict[str, Any]:
        """Escalate to human specialist."""
        logger.info(f"Escalating to human: {reason}")
        
        return {
            "decision_type": DecisionType.PROCEDURE_UNKNOWN,
            "action": "escalate",
            "message": f"⚠️ {reason}. Um especialista será notificado para auxiliá-lo.",
            "can_automate": False,
            "work_order": None,
            "runbook_execution": None,
            "escalation_reason": reason
        }
