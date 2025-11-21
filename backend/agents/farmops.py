"""
FarmOps Agent - Coletor de informações de contexto operacional
"""
from typing import Dict, Any
import time
from .base_agent import BaseAgent, AgentResponse


class FarmOpsAgent(BaseAgent):
    """
    Agente de coleta de informações operacionais.
    
    Responsável por:
    - Coletar dados faltantes (operador, máquina, talhão)
    - Validar informações fornecidas
    - Enriquecer contexto com dados do sistema
    - Preparar contexto completo para próximos agentes
    """
    
    def __init__(self):
        super().__init__(
            name="FarmOps",
            role="Information Collector & Context Enrichment",
            description="Collects missing operational information and enriches context"
        )
        
        # Campos obrigatórios por tipo de intenção
        self.required_fields = {
            "field_diagnosis": ["plot_id", "culture", "operator_id"],
            "equipment_alert": ["equipment_id", "operator_id"],
            "inventory": ["item_type"],
            "compliance": ["document_type"],
            "general": []
        }
    
    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Processa o contexto e coleta informações faltantes.
        
        Args:
            context: Deve conter:
                - intent: str - Intenção classificada
                - extracted_info: Dict - Informações já extraídas
                - user_id: str - ID do usuário (opcional)
        
        Returns:
            AgentResponse com:
                - complete: bool - Se o contexto está completo
                - missing_fields: List[str] - Campos faltantes
                - enriched_context: Dict - Contexto enriquecido
                - questions: List[str] - Perguntas para coletar dados faltantes
        """
        start_time = time.time()
        self.log_request(context)
        
        try:
            intent = context.get("intent", "general")
            extracted_info = context.get("extracted_info", {})
            user_id = context.get("user_id")
            
            # Verificar campos obrigatórios
            required = self.required_fields.get(intent, [])
            missing = self._check_missing_fields(extracted_info, required)
            
            # Enriquecer contexto com dados do sistema
            enriched_context = self._enrich_context(extracted_info, user_id)
            
            # Gerar perguntas para campos faltantes
            questions = self._generate_questions(missing, intent)
            
            # Determinar se está completo
            is_complete = len(missing) == 0
            
            response = AgentResponse(
                agent_name=self.name,
                success=True,
                data={
                    "complete": is_complete,
                    "missing_fields": missing,
                    "enriched_context": enriched_context,
                    "questions": questions,
                    "next_agent": "AgroBrain" if is_complete else None
                },
                metadata={
                    "intent": intent,
                    "fields_collected": len(enriched_context),
                    "fields_missing": len(missing)
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
    
    def _check_missing_fields(self, extracted_info: Dict[str, Any], required: list) -> list:
        """Verifica quais campos obrigatórios estão faltando"""
        missing = []
        for field in required:
            if field not in extracted_info or not extracted_info[field]:
                missing.append(field)
        return missing
    
    def _enrich_context(self, extracted_info: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """
        Enriquece o contexto com dados do sistema.
        
        Em produção, isso consultaria bancos de dados reais.
        Por enquanto, usa dados mockados.
        """
        enriched = dict(extracted_info)
        
        # Adicionar informações do usuário se disponível
        if user_id:
            enriched["user_id"] = user_id
            # Em produção: consultar dados do usuário
            enriched["user_name"] = f"Operador {user_id}"
            enriched["user_role"] = "operator"
        
        # Se tiver plot_id, enriquecer com dados do talhão
        if "plot_id" in extracted_info:
            plot_id = extracted_info["plot_id"]
            # Em produção: consultar dados do talhão
            enriched["plot_data"] = {
                "id": plot_id,
                "area_hectares": 50.5,
                "culture": extracted_info.get("culture", "milho"),
                "planting_date": "2024-09-15",
                "growth_stage": "V6"
            }
        
        # Se tiver equipment_id, enriquecer com dados do equipamento
        if "equipment_id" in extracted_info:
            equipment_id = extracted_info["equipment_id"]
            # Em produção: consultar dados do equipamento
            enriched["equipment_data"] = {
                "id": equipment_id,
                "type": extracted_info.get("equipment", "trator"),
                "model": "John Deere 6195M",
                "last_maintenance": "2024-10-01",
                "hours_worked": 1250
            }
        
        return enriched
    
    def _generate_questions(self, missing_fields: list, intent: str) -> list:
        """Gera perguntas amigáveis para coletar campos faltantes"""
        questions = []
        
        question_templates = {
            "plot_id": "Em qual talhão você está?",
            "culture": "Qual é a cultura plantada?",
            "operator_id": "Qual é o seu código de operador?",
            "equipment_id": "Qual é o número do equipamento?",
            "item_type": "Qual insumo você precisa verificar?",
            "document_type": "Qual tipo de documento você precisa?"
        }
        
        for field in missing_fields:
            question = question_templates.get(field, f"Por favor, informe: {field}")
            questions.append(question)
        
        return questions
