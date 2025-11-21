"""
AgroBrain Agent - Base de conhecimento agrícola com RAG
"""
from typing import Dict, Any
import time
from .base_agent import BaseAgent, AgentResponse


class AgroBrainAgent(BaseAgent):
    """
    Agente de conhecimento agrícola com RAG (Retrieval Augmented Generation).
    
    Responsável por:
    - Consultar base de conhecimento agrícola
    - Buscar informações relevantes (Azure AI Search)
    - Gerar respostas baseadas em conhecimento
    - Fornecer recomendações técnicas
    """
    
    def __init__(self):
        super().__init__(
            name="AgroBrain",
            role="Knowledge Base & RAG",
            description="Queries agricultural knowledge base and provides expert recommendations"
        )
        
        # Base de conhecimento mockada (em produção, usar Azure AI Search)
        self.knowledge_base = {
            "fungos": {
                "ferrugem": {
                    "description": "Doença fúngica comum em cereais",
                    "symptoms": ["manchas alaranjadas", "pústulas", "folhas secas"],
                    "treatment": "Aplicar fungicida triazol",
                    "prevention": "Rotação de culturas, variedades resistentes"
                },
                "antracnose": {
                    "description": "Fungo que ataca folhas e frutos",
                    "symptoms": ["manchas circulares escuras", "necrose"],
                    "treatment": "Fungicida cúprico ou sistêmico",
                    "prevention": "Evitar irrigação por aspersão"
                }
            },
            "pragas": {
                "lagarta": {
                    "description": "Inseto desfolhador",
                    "symptoms": ["folhas comidas", "presença de lagartas"],
                    "treatment": "Inseticida biológico (Bt) ou químico",
                    "prevention": "Monitoramento constante, controle biológico"
                }
            },
            "deficiencias": {
                "nitrogenio": {
                    "description": "Deficiência de nitrogênio",
                    "symptoms": ["amarelamento das folhas mais velhas"],
                    "treatment": "Aplicar fertilizante nitrogenado (ureia, sulfato de amônio)",
                    "prevention": "Adubação de cobertura adequada"
                }
            }
        }
    
    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Processa a consulta e busca conhecimento relevante.
        
        Args:
            context: Deve conter:
                - intent: str - Intenção da consulta
                - enriched_context: Dict - Contexto enriquecido
                - query: str - Consulta específica (opcional)
        
        Returns:
            AgentResponse com:
                - knowledge: Dict - Conhecimento encontrado
                - recommendations: List[str] - Recomendações
                - confidence: float - Confiança na resposta
        """
        start_time = time.time()
        self.log_request(context)
        
        try:
            intent = context.get("intent", "general")
            enriched_context = context.get("enriched_context", {})
            query = context.get("query", "")
            
            # Buscar conhecimento relevante
            knowledge = self._search_knowledge(enriched_context, intent)
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(knowledge, enriched_context)
            
            # Calcular confiança
            confidence = self._calculate_confidence(knowledge)
            
            response = AgentResponse(
                agent_name=self.name,
                success=True,
                data={
                    "knowledge": knowledge,
                    "recommendations": recommendations,
                    "confidence": confidence,
                    "next_agent": "RunbookMaster"
                },
                metadata={
                    "intent": intent,
                    "knowledge_items_found": len(knowledge),
                    "recommendations_count": len(recommendations)
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
    
    def _search_knowledge(self, context: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """
        Busca conhecimento relevante na base.
        
        Em produção, isso usaria Azure AI Search com embeddings.
        """
        knowledge = {}
        
        # Buscar por sintomas
        symptoms = context.get("symptoms", [])
        for symptom in symptoms:
            # Buscar em cada categoria
            for category, items in self.knowledge_base.items():
                for item_name, item_data in items.items():
                    if any(s in symptom for s in item_data.get("symptoms", [])):
                        if category not in knowledge:
                            knowledge[category] = []
                        knowledge[category].append({
                            "name": item_name,
                            **item_data
                        })
        
        # Se não encontrou por sintomas, buscar por cultura
        if not knowledge and "culture" in context:
            # Retornar conhecimento geral para a cultura
            knowledge["general"] = [{
                "name": "Informações Gerais",
                "description": f"Informações sobre cultivo de {context['culture']}",
                "recommendations": [
                    "Monitorar regularmente a lavoura",
                    "Manter registros de aplicações",
                    "Seguir calendário de adubação"
                ]
            }]
        
        return knowledge
    
    def _generate_recommendations(self, knowledge: Dict[str, Any], context: Dict[str, Any]) -> list:
        """Gera recomendações baseadas no conhecimento encontrado"""
        recommendations = []
        
        # Extrair recomendações do conhecimento
        for category, items in knowledge.items():
            for item in items:
                if "treatment" in item:
                    recommendations.append(f"Tratamento: {item['treatment']}")
                if "prevention" in item:
                    recommendations.append(f"Prevenção: {item['prevention']}")
                if "recommendations" in item:
                    recommendations.extend(item["recommendations"])
        
        # Adicionar recomendações gerais
        if not recommendations:
            recommendations.append("Consultar agrônomo para diagnóstico preciso")
            recommendations.append("Coletar amostras para análise laboratorial")
        
        return recommendations[:5]  # Limitar a 5 recomendações
    
    def _calculate_confidence(self, knowledge: Dict[str, Any]) -> float:
        """Calcula confiança na resposta baseado no conhecimento encontrado"""
        if not knowledge:
            return 0.3
        
        total_items = sum(len(items) for items in knowledge.values())
        
        # Mais itens = maior confiança, até um máximo de 0.95
        confidence = min(0.5 + (total_items * 0.15), 0.95)
        
        return round(confidence, 2)
