"""
FieldSense Agent - Classificador agrícola especializado
"""
from typing import Dict, Any
import time
from .base_agent import BaseAgent, AgentResponse


class FieldSenseAgent(BaseAgent):
    """
    Agente de classificação de intenção e diagnóstico inicial.
    
    Responsável por:
    - Classificar a intenção do usuário
    - Identificar tipo de problema (praga, doença, equipamento, etc.)
    - Análise inicial de imagens (quando disponível)
    - Extração de contexto básico
    """
    
    def __init__(self):
        super().__init__(
            name="FieldSense",
            role="Intent Classification & Initial Diagnosis",
            description="Classifies user requests and determines the type of agricultural issue"
        )
        
        # Mapeamento de palavras-chave para intenções
        self.intent_keywords = {
            "field_diagnosis": [
                "fungo", "praga", "doença", "folha", "mancha", "amarela", 
                "seca", "podridão", "inseto", "lagarta", "ferrugem"
            ],
            "equipment_alert": [
                "vibração", "alerta", "sensor", "telemetria", "máquina",
                "trator", "colheitadeira", "falha", "erro", "temperatura"
            ],
            "knowledge_query": [
                "como", "quando", "qual", "onde", "por que", "devo",
                "melhor", "recomenda", "aplicar", "plantar"
            ],
            "inventory": [
                "estoque", "falta", "preciso", "comprar", "insumo",
                "adubo", "fertilizante", "defensivo"
            ],
            "compliance": [
                "licença", "permissão", "ambiental", "art", "relatório",
                "conformidade", "prazo", "vencimento"
            ]
        }
    
    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Processa a mensagem e classifica a intenção.
        
        Args:
            context: Deve conter:
                - message: str - Mensagem do usuário
                - images: List[str] - URLs de imagens (opcional)
                - metadata: Dict - Metadados adicionais (opcional)
        
        Returns:
            AgentResponse com:
                - intent: str - Intenção classificada
                - confidence: float - Confiança da classificação
                - extracted_info: Dict - Informações extraídas
        """
        start_time = time.time()
        self.log_request(context)
        
        try:
            message = context.get("message", "").lower()
            images = context.get("images", [])
            
            # Classificar intenção
            intent, confidence = self._classify_intent(message)
            
            # Extrair informações relevantes
            extracted_info = self._extract_information(message, intent)
            
            # Se houver imagens, adicionar flag para análise
            if images:
                extracted_info["has_images"] = True
                extracted_info["image_count"] = len(images)
                extracted_info["requires_image_analysis"] = True
            
            response = AgentResponse(
                agent_name=self.name,
                success=True,
                data={
                    "intent": intent,
                    "confidence": confidence,
                    "extracted_info": extracted_info,
                    "next_agent": self._determine_next_agent(intent)
                },
                metadata={
                    "message_length": len(message),
                    "has_images": bool(images)
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
    
    def _classify_intent(self, message: str) -> tuple[str, float]:
        """
        Classifica a intenção da mensagem.
        
        Returns:
            Tupla (intent, confidence)
        """
        scores = {}
        
        # Calcular score para cada intenção
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message)
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return "general", 0.5
        
        # Retornar intenção com maior score
        max_intent = max(scores, key=scores.get)
        max_score = scores[max_intent]
        
        # Calcular confiança (normalizada)
        confidence = min(max_score / 3, 1.0)  # 3 ou mais keywords = 100% confiança
        
        return max_intent, confidence
    
    def _extract_information(self, message: str, intent: str) -> Dict[str, Any]:
        """Extrai informações relevantes da mensagem"""
        info = {
            "intent": intent,
            "original_message": message
        }
        
        # Extrair informações específicas por intenção
        if intent == "field_diagnosis":
            # Tentar identificar cultura
            cultures = ["milho", "soja", "trigo", "café", "cana", "algodão"]
            for culture in cultures:
                if culture in message:
                    info["culture"] = culture
                    break
            
            # Tentar identificar sintomas
            symptoms = []
            symptom_keywords = {
                "manchas": ["mancha", "manchas"],
                "amarelamento": ["amarela", "amarelado", "clorose"],
                "seca": ["seca", "murcha", "desidratação"],
                "podridão": ["podre", "podridão", "apodrecendo"]
            }
            
            for symptom, keywords in symptom_keywords.items():
                if any(kw in message for kw in keywords):
                    symptoms.append(symptom)
            
            if symptoms:
                info["symptoms"] = symptoms
        
        elif intent == "equipment_alert":
            # Tentar identificar equipamento
            equipments = ["trator", "colheitadeira", "pulverizador", "plantadeira"]
            for equipment in equipments:
                if equipment in message:
                    info["equipment"] = equipment
                    break
        
        return info
    
    def _determine_next_agent(self, intent: str) -> str:
        """Determina qual agente deve processar em seguida"""
        agent_mapping = {
            "field_diagnosis": "FarmOps",
            "equipment_alert": "FarmOps",
            "knowledge_query": "AgroBrain",
            "inventory": "RunbookMaster",
            "compliance": "RunbookMaster",
            "general": "FarmOps"
        }
        
        return agent_mapping.get(intent, "FarmOps")
