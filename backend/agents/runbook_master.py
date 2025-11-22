"""
RunbookMaster Agent - Decisão e automação segura
"""
from typing import Dict, Any, List
import time
from .base_agent import BaseAgent, AgentResponse


class RunbookMasterAgent(BaseAgent):
    """
    Agente de decisão e seleção de runbooks.
    
    Responsável por:
    - Selecionar runbook apropriado para a situação
    - Validar segurança da automação (Safe vs Critical)
    - Decidir entre automação ou escalação
    - Executar ou agendar runbooks
    """
    
    def __init__(self):
        super().__init__(
            name="RunbookMaster",
            role="Decision & Automation",
            description="Selects appropriate runbooks and decides on automation vs escalation"
        )
        
        # Catálogo de runbooks disponíveis
        self.runbooks = {
            "RB-01": {
                "name": "Generate Pest Report",
                "description": "Gera relatório de pragas e doenças",
                "safety_level": "Safe",
                "required_params": ["plot_id", "pest_type"],
                "estimated_time_minutes": 2,
                "auto_execute": True
            },
            "RB-02": {
                "name": "Open Urgent Work Order",
                "description": "Abre ordem de serviço urgente",
                "safety_level": "Critical",
                "required_params": ["equipment_id", "issue_description"],
                "estimated_time_minutes": 5,
                "auto_execute": False,  # Requer aprovação
                "approval_required": True
            },
            "RB-03": {
                "name": "Inventory Check",
                "description": "Verifica estoque de insumos",
                "safety_level": "Safe",
                "required_params": ["item_type"],
                "estimated_time_minutes": 1,
                "auto_execute": True
            },
            "RB-04": {
                "name": "Pre-fill ART Report",
                "description": "Pré-preenche relatório de Anotação de Responsabilidade Técnica",
                "safety_level": "Critical",
                "required_params": ["activity_type", "area_hectares"],
                "estimated_time_minutes": 10,
                "auto_execute": False,
                "approval_required": True
            },
            "RB-05": {
                "name": "Compliance Check",
                "description": "Verifica licenças e conformidade ambiental",
                "safety_level": "Safe",
                "required_params": ["document_type"],
                "estimated_time_minutes": 3,
                "auto_execute": True
            }
        }
        
        # Mapeamento de intenção para runbooks
        self.intent_to_runbook = {
            "field_diagnosis": ["RB-01"],
            "equipment_alert": ["RB-02"],
            "inventory": ["RB-03"],
            "compliance": ["RB-05"],
            "knowledge_query": []  # Não requer runbook
        }
    
    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Processa o contexto e seleciona runbook apropriado.
        
        Args:
            context: Deve conter:
                - intent: str - Intenção
                - enriched_context: Dict - Contexto enriquecido
                - knowledge: Dict - Conhecimento do AgroBrain
                - recommendations: List[str] - Recomendações
        
        Returns:
            AgentResponse com:
                - selected_runbook: str - ID do runbook selecionado
                - runbook_details: Dict - Detalhes do runbook
                - decision: str - "auto_execute", "request_approval", ou "escalate"
                - reason: str - Razão da decisão
        """
        start_time = time.time()
        self.log_request(context)
        
        try:
            intent = context.get("intent", "general")
            enriched_context = context.get("enriched_context", {})
            
            # Selecionar runbook(s) candidato(s)
            candidate_runbooks = self._select_candidate_runbooks(intent, enriched_context)
            
            if not candidate_runbooks:
                # Nenhum runbook aplicável - escalar para humano
                response = AgentResponse(
                    agent_name=self.name,
                    success=True,
                    data={
                        "selected_runbook": None,
                        "decision": "escalate",
                        "reason": "No applicable runbook found for this situation",
                        "escalation_to": "agronomist",
                        "next_agent": "ExplainIt"
                    },
                    metadata={
                        "intent": intent,
                        "candidates_evaluated": 0
                    }
                )
            else:
                # Selecionar melhor runbook
                selected_rb_id = candidate_runbooks[0]
                runbook = self.runbooks[selected_rb_id]
                
                # Verificar parâmetros necessários
                missing_params = self._check_missing_params(runbook, enriched_context)
                
                if missing_params:
                    decision = "request_params"
                    reason = f"Missing required parameters: {', '.join(missing_params)}"
                elif runbook["safety_level"] == "Critical" and runbook.get("approval_required"):
                    decision = "request_approval"
                    reason = "Critical runbook requires human approval"
                elif runbook["auto_execute"]:
                    decision = "auto_execute"
                    reason = "Safe runbook, auto-executing"
                else:
                    decision = "request_approval"
                    reason = "Runbook requires approval"
                
                response = AgentResponse(
                    agent_name=self.name,
                    success=True,
                    data={
                        "selected_runbook": selected_rb_id,
                        "runbook_details": runbook,
                        "decision": decision,
                        "reason": reason,
                        "missing_params": missing_params,
                        "next_agent": "ExplainIt"
                    },
                    metadata={
                        "intent": intent,
                        "candidates_evaluated": len(candidate_runbooks),
                        "safety_level": runbook["safety_level"]
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
    
    def _select_candidate_runbooks(self, intent: str, context: Dict[str, Any]) -> List[str]:
        """Seleciona runbooks candidatos baseado na intenção"""
        candidates = self.intent_to_runbook.get(intent, [])
        
        # Filtrar baseado em contexto adicional
        # Por exemplo, se houver urgência, priorizar runbooks urgentes
        if context.get("urgency") == "high":
            # Reordenar para priorizar runbooks críticos
            candidates = sorted(
                candidates,
                key=lambda rb_id: 0 if self.runbooks[rb_id]["safety_level"] == "Critical" else 1
            )
        
        return candidates
    
    def _check_missing_params(self, runbook: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Verifica parâmetros faltantes para executar o runbook"""
        required = runbook.get("required_params", [])
        missing = []
        
        for param in required:
            if param not in context or not context[param]:
                missing.append(param)
        
        return missing
    
    def get_runbook_catalog(self) -> Dict[str, Any]:
        """Retorna catálogo completo de runbooks"""
        return {
            "runbooks": self.runbooks,
            "total_count": len(self.runbooks),
            "safe_count": sum(1 for rb in self.runbooks.values() if rb["safety_level"] == "Safe"),
            "critical_count": sum(1 for rb in self.runbooks.values() if rb["safety_level"] == "Critical")
        }
