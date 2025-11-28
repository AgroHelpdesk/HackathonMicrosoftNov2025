"""Pydantic schemas for orchestrator and agent responses."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class AgentType(str, Enum):
    """Enum for agent types."""
    FIELD_SENSE = "field_sense"
    FARM_OPS = "farm_ops"
    AGRO_BRAIN = "agro_brain"
    RUNBOOK_MASTER = "runbook_master"
    EXPLAIN_IT = "explain_it"


class FlowState(str, Enum):
    """Enum for flow states."""
    INTENTION_CHECK = "intention_check"
    NEEDS_CLARIFICATION = "needs_clarification"
    GATHERING_CONTEXT = "gathering_context"
    KNOWLEDGE_CHECK = "knowledge_check"
    HUMAN_ESCALATION = "human_escalation"
    AUTOMATION_CHECK = "automation_check"
    WORK_ORDER_CREATED = "work_order_created"
    RUNBOOK_EXECUTION = "runbook_execution"
    EXECUTION_SUCCESS = "execution_success"
    EXECUTION_FAILED = "execution_failed"
    COMPLETED = "completed"


class DecisionType(str, Enum):
    """Enum for decision types."""
    INTENTION_CLEAR = "intention_clear"
    INTENTION_UNCLEAR = "intention_unclear"
    PROCEDURE_KNOWN = "procedure_known"
    PROCEDURE_UNKNOWN = "procedure_unknown"
    CAN_AUTOMATE = "can_automate"
    CANNOT_AUTOMATE = "cannot_automate"
    EXECUTION_SUCCESS = "execution_success"
    EXECUTION_FAILED = "execution_failed"


class FlowDecision(BaseModel):
    """Schema for a decision point in the flow."""
    decision_type: DecisionType = Field(..., description="Type of decision made")
    agent_name: str = Field(..., description="Agent that made the decision")
    reason: str = Field(..., description="Reason for the decision")
    confidence: float = Field(..., description="Confidence level (0.0 to 1.0)")
    next_state: FlowState = Field(..., description="Next state based on this decision")
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class WorkOrder(BaseModel):
    """Schema for work order."""
    order_id: str = Field(..., description="Unique work order ID")
    created_at: str = Field(..., description="Creation timestamp")
    priority: str = Field(..., description="Priority level (low, medium, high, critical)")
    category: str = Field(..., description="Category of the issue")
    description: str = Field(..., description="Detailed description")
    assigned_specialist: str = Field(..., description="Type of specialist assigned")
    estimated_time_hours: float = Field(..., description="Estimated time to complete")
    machine_id: Optional[str] = Field(None, description="Machine ID if applicable")
    field_id: Optional[str] = Field(None, description="Field ID if applicable")
    status: str = Field(default="pending", description="Current status")


class ClarificationRequest(BaseModel):
    """Schema for clarification request."""
    reason: str = Field(..., description="Why clarification is needed")
    missing_info: List[str] = Field(..., description="List of missing information")
    suggested_questions: List[str] = Field(..., description="Suggested questions for user")
    current_understanding: str = Field(..., description="What was understood so far")


class RunbookExecution(BaseModel):
    """Schema for runbook execution result."""
    runbook_name: str = Field(..., description="Name of the runbook executed")
    steps_completed: int = Field(..., description="Number of steps completed")
    total_steps: int = Field(..., description="Total number of steps")
    success: bool = Field(..., description="Whether execution was successful")
    execution_log: List[str] = Field(..., description="Log of execution steps")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class AgentResponseSchema(BaseModel):
    """Schema for individual agent response."""
    agent_name: str = Field(..., description="Name of the agent")
    agent_type: AgentType = Field(..., description="Type of the agent")
    success: bool = Field(..., description="Whether the agent executed successfully")
    data: Dict[str, Any] = Field(..., description="Agent-specific response data")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if agent failed")

    class Config:
        """Pydantic config."""
        use_enum_values = True


class OrchestratorResponse(BaseModel):
    """Schema for complete orchestrator response."""
    success: bool = Field(..., description="Whether orchestration completed successfully")
    message: str = Field(..., description="User-facing response message")
    flow_state: FlowState = Field(..., description="Final state of the flow")
    decisions: List[FlowDecision] = Field(default=[], description="All decisions made during flow")
    agent_responses: List[AgentResponseSchema] = Field(default=[], description="All agent responses")
    work_order: Optional[WorkOrder] = Field(None, description="Work order if created")
    clarification: Optional[ClarificationRequest] = Field(None, description="Clarification request if needed")
    runbook_execution: Optional[RunbookExecution] = Field(None, description="Runbook execution result if executed")
    total_execution_time_ms: float = Field(..., description="Total orchestration time")
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
