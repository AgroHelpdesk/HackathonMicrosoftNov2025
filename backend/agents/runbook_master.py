"""
RunbookMaster Agent - Decision Logic
Determines appropriate actions and runbooks
"""

import json
import logging
from typing import Dict, Any
from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class RunbookMasterAgent:
    """Agent for decision-making and runbook selection"""
    
    SYSTEM_PROMPT = """Você é o RunbookMaster, um agente especializado em tomar decisões sobre automação agrícola.

Sua tarefa é analisar a situação e decidir qual ação tomar.

Runbooks disponíveis:
1. **RB-01**: Gerar relatório de pragas (Safe) - Para problemas fitossanitários
2. **RB-02**: Abrir ordem de serviço urgente (Critical) - Para problemas mecânicos críticos
3. **RB-03**: Verificar inventário (Safe) - Para questões de estoque
4. **RB-04**: Pré-preencher relatório ART (Critical) - Para situações que requerem agrônomo

Níveis de risco:
- **Safe**: Pode ser executado automaticamente
- **Critical**: Requer aprovação humana

Responda APENAS com um objeto JSON no seguinte formato:
{
    "action": "código do runbook (ex: RB-01)",
    "description": "descrição da ação",
    "riskLevel": "Safe ou Critical",
    "reasoning": "explicação da decisão",
    "requiresApproval": true/false
}

Se nenhum runbook for apropriado, use:
{
    "action": "ESCALATE",
    "description": "Encaminhar para atendimento humano",
    "riskLevel": "Safe",
    "reasoning": "explicação",
    "requiresApproval": true
}
"""
    
    def __init__(self, openai_service: OpenAIService):
        """Initialize RunbookMaster agent"""
        self.openai_service = openai_service
        logger.info("RunbookMaster Agent initialized")
    
    def decide_action(
        self,
        message: str,
        intent: str,
        knowledge_answer: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Decide on appropriate action
        
        Args:
            message: Original user message
            intent: Classified intent
            knowledge_answer: Answer from AgroBrain
            context: Optional context
            
        Returns:
            Dict with action, risk level, and reasoning
        """
        try:
            # Build decision context
            decision_context = f"""Mensagem do usuário: {message}

Intenção classificada: {intent}

Resposta da base de conhecimento:
{knowledge_answer}
"""
            
            if context:
                decision_context += f"\n\nContexto adicional: {json.dumps(context, ensure_ascii=False)}"
            
            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": decision_context}
            ]
            
            # Get decision from OpenAI
            response = self.openai_service.chat_completion_with_json(
                messages=messages,
                temperature=0.3,
                max_tokens=300
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            logger.info(f"RunbookMaster decided action: {result.get('action')} (risk: {result.get('riskLevel')})")
            
            return {
                "action": result.get("action", "ESCALATE"),
                "description": result.get("description", ""),
                "riskLevel": result.get("riskLevel", "Critical"),
                "reasoning": result.get("reasoning", ""),
                "requiresApproval": result.get("requiresApproval", True)
            }
            
        except Exception as e:
            logger.error(f"Error in RunbookMaster decision: {e}")
            # Return safe default on error
            return {
                "action": "ESCALATE",
                "description": "Encaminhar para atendimento humano",
                "riskLevel": "Critical",
                "reasoning": f"Erro na decisão: {str(e)}",
                "requiresApproval": True
            }
