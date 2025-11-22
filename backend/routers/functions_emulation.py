"""
Azure Functions Emulation Router
Emulates the endpoints that would normally be served by Azure Functions.
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging
from datetime import datetime
from agents.orchestrator import AgentOrchestrator

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
        event_data = await request.json()
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
    """
    Emulates the endpoint to send messages via ACS Chat.
    """
    logger.info("Send chat message endpoint called (Emulated)")
    
    try:
        req_body = await request.json()
        thread_id = req_body.get("thread_id")
        message = req_body.get("message")
        
        if not thread_id or not message:
            raise HTTPException(status_code=400, detail="thread_id and message are required")
        
        logger.info(f"Would send message to thread {thread_id}: {message[:50]}...")
        
        return {
            "status": "sent",
            "thread_id": thread_id,
            "message_id": "mock_message_id_emulated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending chat message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

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
            }
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
