"""
Base Agent - Classe base para todos os agentes do sistema
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json


class AgentResponse:
    """Resposta de um agente"""
    def __init__(
        self,
        agent_name: str,
        success: bool,
        data: Any = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_name = agent_name
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "agent_name": self.agent_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class BaseAgent(ABC):
    """
    Classe base abstrata para todos os agentes.
    
    Todos os agentes devem herdar desta classe e implementar o método process().
    """
    
    def __init__(self, name: str, role: str, description: str):
        """
        Inicializa o agente base.
        
        Args:
            name: Nome do agente
            role: Papel do agente no sistema
            description: Descrição do agente
        """
        self.name = name
        self.role = role
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_processing_time_ms": 0
        }
    
    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Processa uma requisição.
        
        Args:
            context: Contexto da requisição contendo dados necessários
            
        Returns:
            AgentResponse com o resultado do processamento
        """
        pass
    
    def log_request(self, context: Dict[str, Any]):
        """Registra uma requisição"""
        self.logger.info(f"[{self.name}] Processing request", extra={
            "agent": self.name,
            "context": json.dumps(context, default=str)
        })
        self.metrics["total_requests"] += 1
    
    def log_success(self, response: AgentResponse, processing_time_ms: float):
        """Registra sucesso"""
        self.logger.info(f"[{self.name}] Request successful", extra={
            "agent": self.name,
            "processing_time_ms": processing_time_ms,
            "response": json.dumps(response.to_dict(), default=str)
        })
        self.metrics["successful_requests"] += 1
        self.metrics["total_processing_time_ms"] += processing_time_ms
    
    def log_error(self, error: Exception, processing_time_ms: float):
        """Registra erro"""
        self.logger.error(f"[{self.name}] Request failed: {str(error)}", extra={
            "agent": self.name,
            "processing_time_ms": processing_time_ms,
            "error": str(error)
        }, exc_info=True)
        self.metrics["failed_requests"] += 1
        self.metrics["total_processing_time_ms"] += processing_time_ms
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do agente"""
        avg_time = 0
        if self.metrics["total_requests"] > 0:
            avg_time = self.metrics["total_processing_time_ms"] / self.metrics["total_requests"]
        
        return {
            "agent": self.name,
            "role": self.role,
            "metrics": {
                **self.metrics,
                "avg_processing_time_ms": round(avg_time, 2),
                "success_rate": round(
                    self.metrics["successful_requests"] / max(self.metrics["total_requests"], 1) * 100,
                    2
                )
            }
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Retorna informações do agente"""
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "status": "active"
        }
