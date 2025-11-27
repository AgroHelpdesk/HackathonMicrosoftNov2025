"""Work Order models and schemas.

This module defines Pydantic models for work order operations,
ensuring type safety and validation across the function app.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class WorkOrderStatus(str, Enum):
    """Work order status enumeration."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class WorkOrderPriority(str, Enum):
    """Work order priority levels."""
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class WorkOrderCategory(str, Enum):
    """Work order category classification."""
    MAQUINARIO = "maquinario"
    IRRIGACAO = "irrigacao"
    PLANTIO = "plantio"
    COLHEITA = "colheita"
    INSUMOS = "insumos"
    SOLO = "solo"
    PRAGA = "praga"
    OUTRO = "outro"


class WorkOrderCreate(BaseModel):
    """Schema for creating a new work order."""
    
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Work order title"
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Detailed description of the issue"
    )
    category: WorkOrderCategory = Field(
        ...,
        description="Category of the work order"
    )
    priority: WorkOrderPriority = Field(
        default=WorkOrderPriority.MEDIA,
        description="Priority level"
    )
    assigned_specialist: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Specialist assigned to handle the work order"
    )
    machine_id: Optional[str] = Field(
        None,
        max_length=50,
        description="Machine or equipment identifier"
    )
    field_id: Optional[str] = Field(
        None,
        max_length=50,
        description="Field or location identifier"
    )
    estimated_time_hours: Optional[float] = Field(
        default=2.0,
        ge=0.1,
        le=1000.0,
        description="Estimated time to complete in hours"
    )
    symptoms: Optional[str] = Field(
        None,
        max_length=500,
        description="Observed symptoms or issues"
    )
    requester_id: Optional[str] = Field(
        None,
        max_length=100,
        description="ID of the person requesting the work order"
    )
    requester_contact: Optional[str] = Field(
        None,
        max_length=100,
        description="Contact information of requester"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "title": "Falha no sistema de irrigação",
                "description": "Gotejamento irregular detectado no talhão A3",
                "category": "irrigacao",
                "priority": "alta",
                "assigned_specialist": "Técnico de Irrigação",
                "machine_id": "IRRIG-001",
                "field_id": "A3",
                "estimated_time_hours": 4.0,
                "symptoms": "Vazão irregular, baixa pressão"
            }
        }


class WorkOrder(BaseModel):
    """Complete work order model including system fields."""
    
    id: str = Field(
        ...,
        description="Unique work order ID (Cosmos DB document id)"
    )
    order_id: str = Field(
        ...,
        description="Business work order identifier (e.g., OS-ABC123)"
    )
    title: str = Field(..., description="Work order title")
    description: str = Field(..., description="Detailed description")
    category: WorkOrderCategory = Field(..., description="Category")
    priority: WorkOrderPriority = Field(..., description="Priority level")
    status: WorkOrderStatus = Field(
        default=WorkOrderStatus.PENDING,
        description="Current status"
    )
    assigned_specialist: str = Field(..., description="Assigned specialist")
    machine_id: Optional[str] = Field(None, description="Machine identifier")
    field_id: Optional[str] = Field(None, description="Field identifier")
    estimated_time_hours: float = Field(
        default=2.0,
        description="Estimated completion time"
    )
    symptoms: Optional[str] = Field(None, description="Observed symptoms")
    requester_id: Optional[str] = Field(None, description="Requester ID")
    requester_contact: Optional[str] = Field(None, description="Requester contact")
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Completion timestamp"
    )
    
    # Tracking
    notes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Activity notes and updates"
    )
    attachments: List[str] = Field(
        default_factory=list,
        description="Attachment URLs or references"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    # Cosmos DB partition key (status-based for optimal distribution)
    partition_key: str = Field(
        ...,
        description="Cosmos DB partition key (uses status for efficient queries)"
    )
    
    @field_validator('updated_at', mode='before')
    @classmethod
    def set_updated_at(cls, v):
        """Ensure updated_at is current."""
        return datetime.utcnow()
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "order_id": "OS-A1B2C3D4",
                "title": "Falha no sistema de irrigação",
                "description": "Gotejamento irregular detectado no talhão A3",
                "category": "irrigacao",
                "priority": "alta",
                "status": "pending",
                "assigned_specialist": "Técnico de Irrigação",
                "machine_id": "IRRIG-001",
                "field_id": "A3",
                "estimated_time_hours": 4.0,
                "created_at": "2025-11-26T10:30:00Z",
                "updated_at": "2025-11-26T10:30:00Z"
            }
        }
    
    def to_cosmos_dict(self) -> Dict[str, Any]:
        """Convert to Cosmos DB document format.
        
        Returns:
            Dictionary ready for Cosmos DB insertion with status-based partition key
        """
        data = self.model_dump(mode='json')
        
        # Partition key is always the status for optimal distribution
        data['partition_key'] = data['status']
        
        # Convert datetime objects to ISO strings
        for field in ['created_at', 'updated_at', 'completed_at']:
            if data.get(field):
                if isinstance(data[field], datetime):
                    data[field] = data[field].isoformat()
        
        # Optional: Set TTL for completed items (90 days)
        # Uncomment to enable automatic cleanup of old completed orders
        # if data['status'] == 'completed' and data.get('completed_at'):
        #     data['ttl'] = 90 * 24 * 60 * 60  # 90 days in seconds
        
        return data
