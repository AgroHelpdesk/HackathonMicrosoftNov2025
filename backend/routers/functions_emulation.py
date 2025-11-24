"""
Azure Functions Emulation Router
Emulates the endpoints that would normally be served by Azure Functions.
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging
import asyncio
from datetime import datetime
from copy import deepcopy
from agents.orchestrator import AgentOrchestrator
from database import SessionLocal, Ticket, TicketStep

router = APIRouter()
logger = logging.getLogger("functions_emulation")

# Initialize orchestrator (singleton-ish)
orchestrator = AgentOrchestrator()

@router.post("/api/acs/chat/webhook")
async def acs_chat_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Emulates the ACS Chat Webhook.
    Receives events from Azure Communication Services (simulated).
    """
    logger.info("ACS Chat webhook triggered (Emulated)")
    
    try:
        try:
            event_data = await request.json()
        except Exception:
            # Handle empty body or invalid JSON
            logger.warning("Received invalid JSON in webhook")
            return {"status": "ignored", "reason": "Invalid JSON"}
            
        event_type = event_data.get("eventType")
        
        logger.info(f"Received ACS event: {event_type}")
        
        if event_type == "Microsoft.Communication.ChatMessageReceived":
            # Process in background to mimic async function behavior and not block response
            background_tasks.add_task(_process_chat_message, event_data)
            return {"status": "processed"}
        
        return {"status": "ignored", "reason": f"Event type {event_type} not handled"}
        
    except Exception as e:
        logger.error(f"Error processing ACS chat webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/acs/chat/send")
async def send_chat_message(request: Request):
    """Emulates sending a chat message and returns orchestrator response."""
    logger.info("Send chat message endpoint called (Emulated)")

    try:
        try:
            req_body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        thread_id = req_body.get("thread_id") or req_body.get("ticket_id")
        message = req_body.get("message")
        sender_id = req_body.get("sender_id", "acs-web-user")
        images = req_body.get("images", [])
        metadata = req_body.get("metadata", {})

        if not message:
            raise HTTPException(status_code=400, detail="message is required")

        if not thread_id:
            thread_id = metadata.get("thread_id") or f"thread-{sender_id}"

        logger.info(f"Processing ACS chat message for thread {thread_id}: {message[:80]}")

        async def on_step_change(agent_id, status, details):
            await update_workflow_state(thread_id, agent_id, status, details)

        result = await orchestrator.process_message(
            message=message,
            user_id=sender_id,
            images=images,
            metadata={
                **metadata,
                "thread_id": thread_id,
                "channel": metadata.get("channel", "acs_chat_emulated"),
            },
            on_step_change=on_step_change
        )

        response_payload = {
            "status": "processed" if result.get("success") else "error",
            "thread_id": thread_id,
            "message_id": result.get("timestamp", datetime.utcnow().isoformat()),
            "agent_history": result.get("agent_history", []),
            "decision": result.get("decision"),
            "recommendations": result.get("recommendations", []),
            "processing_time_ms": result.get("processing_time_ms"),
            "requires_user_input": result.get("requires_user_input", False),
            "questions": result.get("questions", []),
            "missing_fields": result.get("missing_fields", []),
        }

        if result.get("success") and result.get("explanation"):
            response_payload["response_text"] = result["explanation"]
        elif not result.get("success"):
            response_payload["error"] = result.get("error", "Unknown error")

        return response_payload

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending chat message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# --- Workflow Emulation ---

# Mock state storage
workflow_states = {}

def _default_agent_states():
    return [
        {"id": "field-sense", "status": "pending", "started_at": None, "completed_at": None, "duration_ms": 0},
        {"id": "farm-ops", "status": "pending", "started_at": None, "completed_at": None, "duration_ms": 0},
        {"id": "agro-brain", "status": "pending", "started_at": None, "completed_at": None, "duration_ms": 0},
        {"id": "runbook-master", "status": "pending", "started_at": None, "completed_at": None, "duration_ms": 0},
        {"id": "explain-it", "status": "pending", "started_at": None, "completed_at": None, "duration_ms": 0}
    ]


def _reset_workflow_state(ticket_id: str):
    workflow_states[ticket_id] = {
        "agents": deepcopy(_default_agent_states()),
        "current_step": 0
    }


def _ensure_workflow_state(ticket_id: str):
    if ticket_id not in workflow_states:
        _reset_workflow_state(ticket_id)
    return workflow_states[ticket_id]

@router.get("/api/workflow/{ticket_id}")
async def get_workflow_state(ticket_id: str):
    """Get the current state of the agent workflow for a ticket."""
    return _ensure_workflow_state(ticket_id)

@router.post("/api/workflow/{ticket_id}/advance")
async def advance_workflow(ticket_id: str):
    """Advance the workflow to the next step."""
    state = _ensure_workflow_state(ticket_id)
    agents = state["agents"]
    current_step = state["current_step"]

    if current_step >= len(agents):
        return state

    current_agent = agents[current_step]

    if current_agent["status"] == "pending":
        await update_workflow_state(ticket_id, current_agent["id"], "in-progress", {"action": "manual advance"})
    elif current_agent["status"] == "in-progress":
        await update_workflow_state(ticket_id, current_agent["id"], "completed", {"action": "manual advance"})
        if state["current_step"] < len(agents):
            next_agent = agents[state["current_step"]]
            if next_agent["status"] == "pending":
                await update_workflow_state(ticket_id, next_agent["id"], "in-progress", {"action": "manual advance"})
    else:
        if state["current_step"] < len(agents):
            next_agent = agents[state["current_step"]]
            if next_agent["status"] == "pending":
                await update_workflow_state(ticket_id, next_agent["id"], "in-progress", {"action": "manual advance"})

    return state

@router.post("/api/workflow/{ticket_id}/reset")
async def reset_workflow(ticket_id: str):
    """Reset the workflow state."""
    _reset_workflow_state(ticket_id)
    return workflow_states[ticket_id]


async def update_workflow_state(ticket_id: str, agent_id: str, status: str, details: Dict[str, Any]):
    """Update the workflow state for a ticket."""
    state = _ensure_workflow_state(ticket_id)

    agent_record = None
    agent_index = None
    for idx, agent in enumerate(state["agents"]):
        if agent["id"] == agent_id:
            agent_record = agent
            agent_index = idx
            break

    if not agent_record:
        return

    now = datetime.utcnow().isoformat()
    agent_record.setdefault("duration_ms", 0)

    if status == "in-progress":
        agent_record["status"] = "in-progress"
        agent_record["started_at"] = agent_record.get("started_at") or now
        agent_record["completed_at"] = None
        state["current_step"] = agent_index
    elif status == "completed":
        agent_record["status"] = "completed"
        agent_record["completed_at"] = now
        start = agent_record.get("started_at")
        if start:
            try:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(now)
                agent_record["duration_ms"] = int((end_dt - start_dt).total_seconds() * 1000)
            except ValueError:
                logger.warning("Invalid start time format for agent %s", agent_id)
        state["current_step"] = agent_index + 1
    else:
        agent_record["status"] = status

async def _process_chat_message(event_data: Dict[str, Any]):
    """Processa mensagem de chat recebida (Logic copied from acs_chat.py)"""
    try:
        data = event_data.get("data", {})
        
        # Extrair informações da mensagem
        message_body = data.get("messageBody", "")
        sender_id = data.get("senderCommunicationIdentifier", {}).get("rawId", "")
        thread_id = data.get("threadId", "")
        message_id = data.get("id", "")
        
        # Extrair anexos/imagens se houver
        attachments = data.get("attachments", [])
        images = [att.get("url") for att in attachments if att.get("attachmentType") == "image"]
        
        logger.info(f"Processing message from {sender_id}: {message_body[:50]}...")
        
        # Define callback for workflow updates
        async def on_step_change(agent_id, status, details):
            await update_workflow_state(thread_id, agent_id, status, details)

        # Processar através do orquestrador
        result = await orchestrator.process_message(
            message=message_body,
            user_id=sender_id,
            images=images,
            metadata={
                "thread_id": thread_id,
                "message_id": message_id,
                "channel": "acs_chat",
                "timestamp": datetime.utcnow().isoformat()
            },
            on_step_change=on_step_change
        )
        
        # Enviar resposta de volta ao chat
        if result["success"]:
            await _send_chat_response(thread_id, result)
        else:
            await _send_error_response(thread_id, result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"Error in _process_chat_message: {str(e)}", exc_info=True)

async def _send_chat_response(thread_id: str, result: Dict[str, Any]):
    """Envia resposta para o thread de chat"""
    try:
        explanation = result.get("explanation", "")
        recommendations = result.get("recommendations", [])
        decision = result.get("decision", {})
        
        # Formatar mensagem de resposta
        response_message = f"{explanation}\n\n"
        
        if recommendations:
            response_message += "**Recomendações:**\n"
            for i, rec in enumerate(recommendations, 1):
                response_message += f"{i}. {rec}\n"
        
        decision_type = decision.get("decision")
        if decision_type == "auto_execute":
            response_message += "\n✅ Ação executada automaticamente."
        elif decision_type == "request_approval":
            response_message += "\n⏸️ Aguardando sua aprovação para executar."
        
        logger.info(f"Would send to thread {thread_id}: {response_message[:100]}...")
        
    except Exception as e:
        logger.error(f"Error sending chat response: {str(e)}", exc_info=True)

async def _send_error_response(thread_id: str, error: str):
    """Envia mensagem de erro para o thread"""
    error_message = f"❌ Desculpe, ocorreu um erro ao processar sua mensagem: {error}"
    logger.info(f"Would send error to thread {thread_id}: {error_message}")

async def _simulate_workflow_progress(ticket_id: str):
    """
    Simulates the progression of agents working on a ticket.
    """
    steps = [
        {"agent_id": "field-sense", "agent": "FieldSense", "text": "Analyzing user intent: Field Diagnosis detected."},
        {"agent_id": "farm-ops", "agent": "FarmOps", "text": "Retrieving plot data for location... Soil moisture is low."},
        {"agent_id": "agro-brain", "agent": "AgroBrain", "text": "Querying knowledge base for 'yellow leaves' in corn... Found 3 matches."},
        {"agent_id": "runbook-master", "agent": "RunbookMaster", "text": "Selected 'Irrigation Protocol A'. Safety check passed. Auto-executing."},
        {"agent_id": "explain-it", "agent": "ExplainIt", "text": "Generated transparency report. Confidence score: 98%."}
    ]

    db = SessionLocal()
    try:
        # Verify ticket exists
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            logger.warning(f"Simulation failed: Ticket {ticket_id} not found")
            return

        for step_data in steps:
            await update_workflow_state(ticket_id, step_data["agent_id"], "in-progress", {"action": step_data["text"]})
            await asyncio.sleep(3) # Simulate processing time
            
            new_step = TicketStep(
                ticket_id=ticket_id,
                agent=step_data["agent"],
                text=step_data["text"],
                ts=datetime.utcnow().isoformat()
            )
            db.add(new_step)
            db.commit()
            logger.info(f"Added simulation step: {step_data['agent']} for ticket {ticket_id}")
            await update_workflow_state(ticket_id, step_data["agent_id"], "completed", {"result": step_data["text"]})
            
    except Exception as e:
        logger.error(f"Error in workflow simulation: {e}")
    finally:
        db.close()

@router.post("/api/simulation/workflow/{ticket_id}")
async def start_workflow_simulation(ticket_id: str, background_tasks: BackgroundTasks):
    """
    Starts a simulated workflow for a given ticket.
    Updates the ticket steps dynamically over time.
    """
    _reset_workflow_state(ticket_id)
    background_tasks.add_task(_simulate_workflow_progress, ticket_id)
    return {"status": "Simulation started", "ticket_id": ticket_id}
