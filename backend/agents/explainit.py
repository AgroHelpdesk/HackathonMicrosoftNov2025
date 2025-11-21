"""
ExplainIt Agent - Transparência e explicabilidade
"""
from typing import Dict, Any, List
import time
from datetime import datetime
from .base_agent import BaseAgent, AgentResponse


class ExplainItAgent(BaseAgent):
    """
    Agente de transparência e explicabilidade.
    
    Responsável por:
    - Gerar explicações claras das ações tomadas
    - Criar relatórios de decisão
    - Documentar raciocínio dos agentes
    - Fornecer logs estruturados para auditoria
    """
    
    def __init__(self):
        super().__init__(
            name="ExplainIt",
            role="Transparency & Explainability",
            description="Generates clear explanations of actions taken and decision rationale"
        )
    
    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Processa o histórico de agentes e gera explicação.
        
        Args:
            context: Deve conter:
                - agent_history: List[Dict] - Histórico de respostas dos agentes
                - original_message: str - Mensagem original do usuário
                - final_decision: Dict - Decisão final do RunbookMaster
        
        Returns:
            AgentResponse com:
                - explanation: str - Explicação em linguagem natural
                - decision_tree: List[Dict] - Árvore de decisão
                - transparency_report: Dict - Relatório completo
        """
        start_time = time.time()
        self.log_request(context)
        
        try:
            agent_history = context.get("agent_history", [])
            original_message = context.get("original_message", "")
            final_decision = context.get("final_decision", {})
            
            # Gerar explicação em linguagem natural
            explanation = self._generate_explanation(agent_history, final_decision)
            
            # Criar árvore de decisão
            decision_tree = self._create_decision_tree(agent_history)
            
            # Gerar relatório de transparência
            transparency_report = self._generate_transparency_report(
                original_message,
                agent_history,
                final_decision
            )
            
            response = AgentResponse(
                agent_name=self.name,
                success=True,
                data={
                    "explanation": explanation,
                    "decision_tree": decision_tree,
                    "transparency_report": transparency_report,
                    "audit_log": self._create_audit_log(agent_history)
                },
                metadata={
                    "agents_involved": len(agent_history),
                    "total_processing_time_ms": sum(
                        h.get("processing_time_ms", 0) for h in agent_history
                    )
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
    
    def _generate_explanation(self, agent_history: List[Dict], final_decision: Dict) -> str:
        """Gera explicação em linguagem natural"""
        explanation_parts = []
        
        # Introdução
        explanation_parts.append("Aqui está o que aconteceu com sua solicitação:\n")
        
        # Processar cada agente
        for i, agent_response in enumerate(agent_history, 1):
            agent_name = agent_response.get("agent_name", "Unknown")
            data = agent_response.get("data", {})
            
            if agent_name == "FieldSense":
                intent = data.get("intent", "unknown")
                confidence = data.get("confidence", 0) * 100
                explanation_parts.append(
                    f"{i}. **FieldSense** analisou sua mensagem e identificou que você está "
                    f"relatando: **{self._translate_intent(intent)}** (confiança: {confidence:.0f}%)"
                )
            
            elif agent_name == "FarmOps":
                complete = data.get("complete", False)
                missing = data.get("missing_fields", [])
                if complete:
                    explanation_parts.append(
                        f"{i}. **FarmOps** coletou todas as informações necessárias do sistema"
                    )
                else:
                    explanation_parts.append(
                        f"{i}. **FarmOps** identificou que faltam algumas informações: {', '.join(missing)}"
                    )
            
            elif agent_name == "AgroBrain":
                knowledge_count = data.get("metadata", {}).get("knowledge_items_found", 0)
                recommendations = data.get("recommendations", [])
                explanation_parts.append(
                    f"{i}. **AgroBrain** consultou a base de conhecimento e encontrou "
                    f"{knowledge_count} informações relevantes, gerando {len(recommendations)} recomendações"
                )
            
            elif agent_name == "RunbookMaster":
                decision = data.get("decision", "unknown")
                runbook_id = data.get("selected_runbook")
                reason = data.get("reason", "")
                
                if decision == "auto_execute":
                    explanation_parts.append(
                        f"{i}. **RunbookMaster** selecionou o runbook **{runbook_id}** e "
                        f"iniciou a execução automática. Motivo: {reason}"
                    )
                elif decision == "request_approval":
                    explanation_parts.append(
                        f"{i}. **RunbookMaster** selecionou o runbook **{runbook_id}** mas "
                        f"requer sua aprovação antes de executar. Motivo: {reason}"
                    )
                elif decision == "escalate":
                    explanation_parts.append(
                        f"{i}. **RunbookMaster** decidiu escalar para um especialista humano. "
                        f"Motivo: {reason}"
                    )
        
        # Conclusão
        decision_type = final_decision.get("decision", "unknown")
        if decision_type == "auto_execute":
            explanation_parts.append(
                "\n✅ **Ação tomada**: O sistema executou automaticamente as ações necessárias."
            )
        elif decision_type == "request_approval":
            explanation_parts.append(
                "\n⏸️ **Aguardando aprovação**: Por favor, revise e aprove a ação proposta."
            )
        elif decision_type == "escalate":
            explanation_parts.append(
                "\n👤 **Escalado para especialista**: Um agrônomo será notificado para ajudar."
            )
        
        return "\n\n".join(explanation_parts)
    
    def _translate_intent(self, intent: str) -> str:
        """Traduz intenção para português"""
        translations = {
            "field_diagnosis": "problema no campo (praga/doença)",
            "equipment_alert": "alerta de equipamento",
            "knowledge_query": "consulta de conhecimento",
            "inventory": "verificação de estoque",
            "compliance": "verificação de conformidade",
            "general": "solicitação geral"
        }
        return translations.get(intent, intent)
    
    def _create_decision_tree(self, agent_history: List[Dict]) -> List[Dict]:
        """Cria árvore de decisão visual"""
        tree = []
        
        for agent_response in agent_history:
            agent_name = agent_response.get("agent_name")
            data = agent_response.get("data", {})
            success = agent_response.get("success", False)
            
            node = {
                "agent": agent_name,
                "success": success,
                "key_data": self._extract_key_data(agent_name, data),
                "next_agent": data.get("next_agent")
            }
            tree.append(node)
        
        return tree
    
    def _extract_key_data(self, agent_name: str, data: Dict) -> Dict:
        """Extrai dados-chave de cada agente"""
        if agent_name == "FieldSense":
            return {
                "intent": data.get("intent"),
                "confidence": data.get("confidence")
            }
        elif agent_name == "FarmOps":
            return {
                "complete": data.get("complete"),
                "missing_fields": data.get("missing_fields", [])
            }
        elif agent_name == "AgroBrain":
            return {
                "knowledge_found": data.get("metadata", {}).get("knowledge_items_found", 0),
                "confidence": data.get("confidence")
            }
        elif agent_name == "RunbookMaster":
            return {
                "runbook": data.get("selected_runbook"),
                "decision": data.get("decision"),
                "safety_level": data.get("metadata", {}).get("safety_level")
            }
        return {}
    
    def _generate_transparency_report(
        self,
        original_message: str,
        agent_history: List[Dict],
        final_decision: Dict
    ) -> Dict:
        """Gera relatório completo de transparência"""
        return {
            "report_id": f"TR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "original_request": original_message,
            "agents_involved": [h.get("agent_name") for h in agent_history],
            "total_processing_time_ms": sum(
                h.get("metadata", {}).get("processing_time_ms", 0) for h in agent_history
            ),
            "final_decision": final_decision,
            "confidence_scores": {
                h.get("agent_name"): h.get("data", {}).get("confidence")
                for h in agent_history
                if h.get("data", {}).get("confidence") is not None
            },
            "automation_level": self._determine_automation_level(final_decision)
        }
    
    def _determine_automation_level(self, final_decision: Dict) -> str:
        """Determina nível de automação"""
        decision = final_decision.get("decision", "unknown")
        
        levels = {
            "auto_execute": "Fully Automated",
            "request_approval": "Semi-Automated (Requires Approval)",
            "escalate": "Manual (Human Required)",
            "request_params": "Awaiting Information"
        }
        
        return levels.get(decision, "Unknown")
    
    def _create_audit_log(self, agent_history: List[Dict]) -> List[Dict]:
        """Cria log de auditoria estruturado"""
        audit_log = []
        
        for agent_response in agent_history:
            log_entry = {
                "timestamp": agent_response.get("timestamp"),
                "agent": agent_response.get("agent_name"),
                "success": agent_response.get("success"),
                "data_summary": str(agent_response.get("data", {}))[:200],  # Primeiros 200 chars
                "metadata": agent_response.get("metadata", {})
            }
            audit_log.append(log_entry)
        
        return audit_log
