"""
FieldSense Agent - Intent Classification
Classifies user requests into categories
"""

import json
import logging
from typing import Dict, Any
from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class FieldSenseAgent:
    """Agent for classifying user intent"""
    
    SYSTEM_PROMPT = """Você é o FieldSense, um agente especializado em classificar solicitações agrícolas.

Sua tarefa é analisar a mensagem do usuário e classificar em uma das seguintes categorias:

1. **Phytosanitary** (Fitossanitário): Problemas com pragas, doenças, defensivos agrícolas
2. **Mechanical** (Mecânico): Problemas com tratores, equipamentos, manutenção
3. **Stock** (Estoque): Questões sobre insumos, fertilizantes, sementes
4. **General** (Geral): Perguntas gerais, informações, outros assuntos

Responda APENAS com um objeto JSON no seguinte formato:
{
    "intent": "categoria",
    "confidence": 0.95,
    "reasoning": "breve explicação"
}

Exemplos:
- "Estou vendo manchas nas folhas do milho" → Phytosanitary
- "O trator não está ligando" → Mechanical
- "Preciso verificar o estoque de fertilizante" → Stock
- "Qual é o clima previsto?" → General
"""
    
    def __init__(self, openai_service: OpenAIService):
        """Initialize FieldSense agent"""
        self.openai_service = openai_service
        logger.info("FieldSense Agent initialized")
    
    def classify(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify user intent
        
        Args:
            message: User message
            context: Optional context information
            
        Returns:
            Dict with intent, confidence, and reasoning
        """
        try:
            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
            
            # Add context if available
            if context:
                context_str = f"\nContexto adicional: {json.dumps(context, ensure_ascii=False)}"
                messages[-1]["content"] += context_str
            
            # Get classification from OpenAI
            response = self.openai_service.chat_completion_with_json(
                messages=messages,
                temperature=0.3,
                max_tokens=200
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            logger.info(f"FieldSense classified intent: {result.get('intent')} (confidence: {result.get('confidence')})")
            
            return {
                "intent": result.get("intent", "General"),
                "confidence": result.get("confidence", 0.0),
                "reasoning": result.get("reasoning", "")
            }
            
        except Exception as e:
            logger.error(f"Error in FieldSense classification: {e}")
            # Return default classification on error
            return {
                "intent": "General",
                "confidence": 0.0,
                "reasoning": f"Erro na classificação: {str(e)}"
            }
