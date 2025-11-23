"""
Data models for Chat API requests and responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatContext(BaseModel):
    """Context information for the chat request"""
    plot_id: Optional[str] = Field(None, alias="plotId")
    crop: Optional[str] = None
    location: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat API request model"""
    message: str = Field(..., min_length=1)
    ticket_id: Optional[str] = Field(None, alias="ticketId")
    context: Optional[ChatContext] = None


class AgentResponse(BaseModel):
    """Individual agent response"""
    name: str
    data: Dict[str, Any]
    execution_time: float = Field(..., alias="executionTime")


class ChatResponse(BaseModel):
    """Chat API response model"""
    response: str
    agents: List[AgentResponse]
    suggested_actions: List[str] = Field(default_factory=list, alias="suggestedActions")
    ticket_id: Optional[str] = Field(None, alias="ticketId")
