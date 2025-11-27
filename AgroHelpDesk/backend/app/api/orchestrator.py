"""Orchestrator API endpoints.

This module provides REST API endpoints for direct orchestrator processing.
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.orchestrator import Orchestrator
from app.utils.logger import get_logger

logger = get_logger("api.orchestrator")
router = APIRouter()
orch = Orchestrator()


class QueryPayload(BaseModel):
    """Request payload for orchestrator processing."""

    message: str = Field(..., min_length=1, description="User message to process")
    session_id: Optional[str] = Field(None, description="Optional session identifier")


class QueryResponse(BaseModel):
    """Response model for orchestrator processing."""

    response: str = Field(..., description="Processed response")
    explicacao: Optional[str] = Field(None, description="Explanation of actions taken")
    trace: list[dict[str, Any]] = Field(..., description="Agent execution trace")
    context: dict[str, Any] = Field(..., description="Enriched context")
    decision: dict[str, Any] = Field(..., description="Decision made by RunbookMaster")


@router.post("/process", response_model=QueryResponse)
async def process(payload: QueryPayload) -> QueryResponse:
    """Process a message through the orchestrator.

    Args:
        payload: Query payload with message and optional session_id.

    Returns:
        Processed result with response, explanation, and trace.

    Raises:
        HTTPException: If processing fails.
    """
    try:
        logger.info(f"Processing message: {payload.message[:50]}...")

        result = await orch.process(payload.message, session_id=payload.session_id)

        logger.info("Message processed successfully")
        return QueryResponse(**result)

    except Exception as e:
        logger.exception(f"Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message through orchestrator",
        )
