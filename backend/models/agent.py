"""
Agent Model - Modelo de dados para agentes
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class Agent(BaseModel):
    """Modelo de agente"""
    id: str
    name: str
    role: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    status: str = "active"  # "active", "inactive", "maintenance"
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "fieldsense",
                "name": "FieldSense",
                "role": "Intent Classification",
                "description": "Classifies user requests and determines the type of issue",
                "capabilities": [
                    "Intent recognition",
                    "Image analysis",
                    "Context extraction"
                ],
                "status": "active",
                "metrics": {
                    "total_requests": 1250,
                    "accuracy": 0.94,
                    "avg_response_time_ms": 450
                }
            }
        }


class ChatMessage(BaseModel):
    """Mensagem de chat"""
    message: str
    ticket_id: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Resposta do chat"""
    response: str
    agent: str
    ticket_id: Optional[str] = None
    actions_taken: List[str] = Field(default_factory=list)
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "I've analyzed the image and detected a fungal infection. Creating a ticket and notifying the agronomist.",
                "agent": "FieldSense",
                "ticket_id": "T-001",
                "actions_taken": [
                    "Image analyzed",
                    "Ticket created",
                    "Agronomist notified"
                ],
                "timestamp": "2025-11-20T10:00:00Z"
            }
        }
