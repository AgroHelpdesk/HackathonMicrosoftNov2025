"""
Agent Orchestrator - Coordena o fluxo entre múltiplos agentes
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .fieldsense import FieldSenseAgent
from .farmops import FarmOpsAgent
from .agrobrain import AgroBrainAgent
from .runbook_master import RunbookMasterAgent
from .explainit import ExplainItAgent
from .base_agent import AgentResponse


class AgentOrchestrator:
    """
    Orquestrador de agentes que coordena o fluxo de processamento.
    
    Implementa o padrão Chain of Responsibility, passando o contexto
    através dos agentes na ordem apropriada.
    """
    
    def __init__(self):
        """Inicializa o orquestrador e todos os agentes"""
        self.logger = logging.getLogger("orchestrator")
        
        # Inicializar agentes
        self.agents = {
            "FieldSense": FieldSenseAgent(),
            "FarmOps": FarmOpsAgent(),
            "AgroBrain": AgroBrainAgent(),
            "RunbookMaster": RunbookMasterAgent(),
            "ExplainIt": ExplainItAgent()
        }
        
        self.logger.info("Agent Orchestrator initialized with 5 agents")
    
    async def process_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        on_step_change: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem através do pipeline de agentes.
        
        Args:
            message: Mensagem do usuário
            user_id: ID do usuário (opcional)
            images: Lista de URLs de imagens (opcional)
            metadata: Metadados adicionais (opcional)
            on_step_change: Callback async function(agent_id, status, details)
        
        Returns:
            Dicionário com:
                - success: bool
                - explanation: str - Explicação gerada pelo ExplainIt
                - decision: Dict - Decisão final
                - agent_history: List - Histórico de todos os agentes
                - transparency_report: Dict - Relatório de transparência
        """
        start_time = datetime.utcnow()
        self.logger.info(f"Processing message: {message[:50]}...")
        
        # Contexto inicial
        context = {
            "message": message,
            "user_id": user_id,
            "images": images or [],
            "metadata": metadata or {},
            "original_message": message
        }
        
        # Histórico de respostas dos agentes
        agent_history = []
        
        try:
            # 1. FieldSense - Classificação de intenção
            if on_step_change: await on_step_change("field-sense", "in-progress", {"action": "Analyzing intent"})
            fieldsense_response = await self.agents["FieldSense"].process(context)
            agent_history.append(fieldsense_response.to_dict())
            if on_step_change: await on_step_change("field-sense", "completed", {"result": fieldsense_response.data.get("intent")})
            
            if not fieldsense_response.success:
                return self._create_error_response("FieldSense failed", agent_history)
            
            # Atualizar contexto
            context.update({
                "intent": fieldsense_response.data["intent"],
                "extracted_info": fieldsense_response.data["extracted_info"]
            })
            
            # 2. FarmOps - Coleta de informações
            if on_step_change: await on_step_change("farm-ops", "in-progress", {"action": "Collecting info"})
            farmops_response = await self.agents["FarmOps"].process(context)
            agent_history.append(farmops_response.to_dict())
            if on_step_change: await on_step_change("farm-ops", "completed", {"result": "Context enriched"})
            
            if not farmops_response.success:
                return self._create_error_response("FarmOps failed", agent_history)
            
            # Verificar se precisa de mais informações
            if not farmops_response.data["complete"]:
                # Retornar com perguntas para o usuário
                return {
                    "success": True,
                    "requires_user_input": True,
                    "questions": farmops_response.data["questions"],
                    "missing_fields": farmops_response.data["missing_fields"],
                    "agent_history": agent_history
                }
            
            # Atualizar contexto
            context.update({
                "enriched_context": farmops_response.data["enriched_context"]
            })
            
            # 3. AgroBrain - Base de conhecimento
            if on_step_change: await on_step_change("agro-brain", "in-progress", {"action": "Querying knowledge base"})
            agrobrain_response = await self.agents["AgroBrain"].process(context)
            agent_history.append(agrobrain_response.to_dict())
            if on_step_change: await on_step_change("agro-brain", "completed", {"result": "Recommendations generated"})
            
            if not agrobrain_response.success:
                return self._create_error_response("AgroBrain failed", agent_history)
            
            # Atualizar contexto
            context.update({
                "knowledge": agrobrain_response.data["knowledge"],
                "recommendations": agrobrain_response.data["recommendations"]
            })
            
            # 4. RunbookMaster - Decisão e automação
            if on_step_change: await on_step_change("runbook-master", "in-progress", {"action": "Evaluating runbooks"})
            runbook_response = await self.agents["RunbookMaster"].process(context)
            agent_history.append(runbook_response.to_dict())
            if on_step_change: await on_step_change("runbook-master", "completed", {"result": runbook_response.data.get("decision")})
            
            if not runbook_response.success:
                return self._create_error_response("RunbookMaster failed", agent_history)
            
            # Atualizar contexto com decisão final
            context.update({
                "final_decision": runbook_response.data
            })
            
            # 5. ExplainIt - Transparência
            context["agent_history"] = agent_history
            if on_step_change: await on_step_change("explain-it", "in-progress", {"action": "Generating explanation"})
            explainit_response = await self.agents["ExplainIt"].process(context)
            agent_history.append(explainit_response.to_dict())
            if on_step_change: await on_step_change("explain-it", "completed", {"result": "Response ready"})
            
            if not explainit_response.success:
                return self._create_error_response("ExplainIt failed", agent_history)
            
            # Calcular tempo total
            total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Retornar resultado completo
            return {
                "success": True,
                "explanation": explainit_response.data["explanation"],
                "decision": runbook_response.data,
                "recommendations": agrobrain_response.data["recommendations"],
                "agent_history": agent_history,
                "transparency_report": explainit_response.data["transparency_report"],
                "decision_tree": explainit_response.data["decision_tree"],
                "processing_time_ms": total_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Orchestrator error: {str(e)}", exc_info=True)
            return self._create_error_response(str(e), agent_history)
    
    def _create_error_response(self, error: str, agent_history: List[Dict]) -> Dict[str, Any]:
        """Cria resposta de erro"""
        return {
            "success": False,
            "error": error,
            "agent_history": agent_history,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de todos os agentes"""
        return {
            "agents": {
                name: agent.get_metrics()
                for name, agent in self.agents.items()
            },
            "total_agents": len(self.agents)
        }
    
    def get_agent_info(self) -> List[Dict[str, Any]]:
        """Retorna informações de todos os agentes"""
        return [
            agent.get_info()
            for agent in self.agents.values()
        ]
    
    def get_runbook_catalog(self) -> Dict[str, Any]:
        """Retorna catálogo de runbooks do RunbookMaster"""
        return self.agents["RunbookMaster"].get_runbook_catalog()
