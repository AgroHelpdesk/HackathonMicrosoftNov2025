"""
Ticket Model - Modelo de dados para tickets
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    """Passo executado por um agente"""
    agent: str
    action: str
    details: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Ticket(BaseModel):
    """Modelo de ticket"""
    id: str
    type: str  # "Field Diagnosis", "Equipment Alert", "Pest Identification", etc.
    summary: str
    channel: str  # "WhatsApp", "Teams", "Email", etc.
    location: Optional[str] = None
    crop: Optional[str] = None
    stage: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    steps: List[AgentStep] = Field(default_factory=list)
    status: str = "open"  # "open", "in_progress", "resolved", "escalated"
    decision: Optional[str] = None
    resolution: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "T-001",
                "type": "Field Diagnosis",
                "summary": "Possible fungal infection on soybean leaves",
                "channel": "WhatsApp",
                "location": "Plot 22",
                "crop": "Soybean",
                "stage": "V5",
                "images": ["https://storage.blob.core.windows.net/images/leaf001.jpg"],
                "steps": [
                    {
                        "agent": "FieldSense",
                        "action": "Intent Classification",
                        "details": "Classified as Field Diagnosis",
                        "timestamp": "2025-11-20T10:00:00Z"
                    }
                ],
                "status": "open",
                "decision": None,
                "created_at": "2025-11-20T10:00:00Z",
                "updated_at": "2025-11-20T10:00:00Z"
            }
        }


class TicketCreate(BaseModel):
    """Dados para criar um novo ticket"""
    message: str
    channel: str = "API"
    images: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TicketUpdate(BaseModel):
    """Dados para atualizar um ticket"""
    status: Optional[str] = None
    decision: Optional[str] = None
    resolution: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
