"""Chat API endpoints.

This module provides REST API endpoints for chat session management
and message handling.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.orchestrator import Orchestrator
from app.services.acs_messages import send_message_to_thread
from app.services.acs_threads import create_thread, delete_thread
from app.services.session_store import add_message, create_session, get_session, list_history
from app.utils.logger import get_logger

logger = get_logger("api.chat")
router = APIRouter()
orch = Orchestrator()


class StartSessionResponse(BaseModel):
    """Response model for session creation."""

    session_id: str = Field(..., description="Unique session identifier")


class SendMessagePayload(BaseModel):
    """Request payload for sending a message."""

    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., min_length=1, description="User message text")
    user_id: Optional[str] = Field(None, description="Optional user identifier")


class SendMessageResponse(BaseModel):
    """Response model for message sending."""

    ok: bool = Field(..., description="Success status")
    reply: str = Field(..., description="Bot reply message")
    flow_state: Optional[str] = Field(None, description="Current flow state")
    needs_clarification: Optional[bool] = Field(None, description="Whether clarification is needed")
    work_order_id: Optional[str] = Field(None, description="Work order ID if created")
    execution_summary: Optional[dict[str, Any]] = Field(None, description="Execution summary")


class HistoryResponse(BaseModel):
    """Response model for message history."""

    messages: list[dict[str, Any]] = Field(..., description="List of messages")


@router.post("/start_session", response_model=StartSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session() -> StartSessionResponse:
    """Create a new chat session.

    Returns:
        Session identifier for the new session.

    Raises:
        HTTPException: If session creation fails.
    """
    try:
        # Create thread on ACS
        thread = await create_thread()
        # The new SDK returns {'id': '...', 'topic': '...', 'created_on': '...'}
        thread_id = thread.get("id")

        if not thread_id:
            logger.error(f"Failed to extract thread_id from ACS response: {thread}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create communication thread",
            )

        # Create session
        session_id = str(uuid.uuid4())
        await create_session(
            session_id, thread_id, initial_metadata={"created_by": "ui", "version": "0.1.0"}
        )

        logger.info(f"Session created: {session_id} with thread: {thread_id}")
        return StartSessionResponse(session_id=session_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error creating session",
        )


@router.post("/send_message", response_model=SendMessageResponse)
async def send_message(payload: SendMessagePayload) -> SendMessageResponse:
    """Send a message in an existing chat session.

    Args:
        payload: Message payload with session_id and message text.

    Returns:
        Bot reply to the message.

    Raises:
        HTTPException: If session not found or processing fails.
    """
    try:
        # Verify session exists
        session = await get_session(payload.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        # Store incoming message
        await add_message(
            payload.session_id,
            role="user",
            text=payload.message,
            extra={"user_id": payload.user_id},
        )

        # Send to ACS thread (triggers webhook and orchestrator)
        await send_message_to_thread(
            session["thread_id"],
            payload.message,
            sender_display_name=payload.user_id or "OPERADOR",
        )

        # Process message through orchestrator
        result = await orch.process(payload.message, session_id=payload.session_id)
        
        # Extract response data
        reply_text = result.message
        flow_state = result.flow_state if isinstance(result.flow_state, str) else (result.flow_state.value if result.flow_state else None)
        needs_clarification = result.clarification is not None
        work_order_id = result.work_order.order_id if result.work_order else None
        
        # Build execution summary
        execution_summary = {
            "total_time_ms": result.total_execution_time_ms,
            "agents_executed": len(result.agent_responses),
            "decisions_made": len(result.decisions),
            "success": result.success
        }
        
        # Add work order or runbook execution details if available
        if result.work_order:
            execution_summary["work_order"] = {
                "id": result.work_order.order_id,
                "specialist": result.work_order.assigned_specialist,
                "priority": result.work_order.priority
            }
        
        if result.runbook_execution:
            execution_summary["runbook_execution"] = {
                "name": result.runbook_execution.runbook_name,
                "success": result.runbook_execution.success,
                "steps_completed": result.runbook_execution.steps_completed
            }

        # Store bot reply with metadata
        # Extract fieldsense_data from agent responses to preserve context
        fieldsense_data = None
        for agent_response in result.agent_responses:
            if agent_response.agent_name == "FieldSense" and agent_response.success:
                fieldsense_data = agent_response.data
                break
        
        await add_message(
            payload.session_id,
            role="bot",
            text=reply_text,
            extra={
                "flow_state": flow_state,
                "needs_clarification": needs_clarification,
                "work_order_id": work_order_id,
                "execution_summary": execution_summary,
                "fieldsense_data": fieldsense_data  # Save for next conversation turn
            }
        )

        logger.info(
            f"Message processed for session {payload.session_id}: "
            f"state={flow_state}, clarification={needs_clarification}"
        )
        
        return SendMessageResponse(
            ok=True,
            reply=reply_text,
            flow_state=flow_state,
            needs_clarification=needs_clarification,
            work_order_id=work_order_id,
            execution_summary=execution_summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def history(session_id: str) -> HistoryResponse:
    """Get message history for a session.

    Args:
        session_id: Session identifier.

    Returns:
        List of messages in the session.

    Raises:
        HTTPException: If retrieval fails.
    """
    try:
        messages = await list_history(session_id)
        logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
        return HistoryResponse(messages=messages)

    except Exception as e:
        logger.exception(f"Error retrieving history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve message history",
        )


@router.post("/close_session/{session_id}", status_code=status.HTTP_200_OK)
async def close_session(session_id: str) -> dict:
    """Close a chat session and its associated thread.

    Args:
        session_id: Session identifier to close.

    Returns:
        Success confirmation.

    Raises:
        HTTPException: If session not found or closure fails.
    """
    try:
        # Verify session exists
        session = await get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Session not found"
            )

        thread_id = session.get("thread_id")
        
        # Delete thread from ACS
        if thread_id:
            try:
                await delete_thread(thread_id)
                logger.info(f"ACS thread {thread_id} deleted successfully")
            except Exception as e:
                logger.error(f"Failed to delete ACS thread {thread_id}: {e}")
                # Continue even if thread deletion fails

        # Mark session as closed in metadata
        session["metadata"]["status"] = "closed"
        session["metadata"]["closed_at"] = str(datetime.now())
        
        logger.info(f"Session {session_id} closed successfully")
        
        return {
            "ok": True,
            "message": "Session and thread closed successfully",
            "session_id": session_id,
            "thread_id": thread_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error closing session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to close session",
        )

