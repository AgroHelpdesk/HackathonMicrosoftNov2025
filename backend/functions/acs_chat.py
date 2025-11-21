"""
ACS Chat Integration - Azure Communication Services Chat
"""
import azure.functions as func
import logging
import json
from typing import Dict, Any
from datetime import datetime

# Importar orquestrador de agentes
from agents.orchestrator import AgentOrchestrator

# Blueprint para funções ACS
bp = func.Blueprint()

# Inicializar orquestrador
orchestrator = AgentOrchestrator()


@bp.route(route="acs/chat/webhook", methods=["POST"])
async def acs_chat_webhook(req: func.HttpRequest) -> func.HttpResponse:
    """
    Webhook para receber eventos de chat do ACS.
    
    Processa mensagens recebidas via ACS Chat e responde através do sistema de agentes.
    """
    logging.info("ACS Chat webhook triggered")
    
    try:
        # Parse do evento
        event_data = req.get_json()
        event_type = event_data.get("eventType")
        
        logging.info(f"Received ACS event: {event_type}")
        
        # Processar apenas eventos de mensagem
        if event_type == "Microsoft.Communication.ChatMessageReceived":
            await _process_chat_message(event_data)
            
            return func.HttpResponse(
                json.dumps({"status": "processed"}),
                status_code=200,
                mimetype="application/json"
            )
        
        # Outros tipos de eventos
        return func.HttpResponse(
            json.dumps({"status": "ignored", "reason": f"Event type {event_type} not handled"}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error processing ACS chat webhook: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


async def _process_chat_message(event_data: Dict[str, Any]):
    """Processa mensagem de chat recebida"""
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
        
        logging.info(f"Processing message from {sender_id}: {message_body[:50]}...")
        
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
        logging.error(f"Error in _process_chat_message: {str(e)}", exc_info=True)
        raise


async def _send_chat_response(thread_id: str, result: Dict[str, Any]):
    """Envia resposta para o thread de chat"""
    try:
        # TODO: Implementar envio real via ACS Chat SDK
        # Por enquanto, apenas log
        
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
        
        logging.info(f"Would send to thread {thread_id}: {response_message[:100]}...")
        
        # Em produção:
        # from azure.communication.chat import ChatClient
        # chat_client = ChatClient(endpoint, credential)
        # chat_thread_client = chat_client.get_chat_thread_client(thread_id)
        # chat_thread_client.send_message(content=response_message)
        
    except Exception as e:
        logging.error(f"Error sending chat response: {str(e)}", exc_info=True)


async def _send_error_response(thread_id: str, error: str):
    """Envia mensagem de erro para o thread"""
    error_message = f"❌ Desculpe, ocorreu um erro ao processar sua mensagem: {error}"
    logging.info(f"Would send error to thread {thread_id}: {error_message}")
    
    # Em produção: usar ACS Chat SDK para enviar mensagem


@bp.route(route="acs/chat/send", methods=["POST"])
async def send_chat_message(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint para enviar mensagens via ACS Chat programaticamente.
    
    Body:
        {
            "thread_id": "thread_id",
            "message": "message content"
        }
    """
    logging.info("Send chat message endpoint called")
    
    try:
        req_body = req.get_json()
        thread_id = req_body.get("thread_id")
        message = req_body.get("message")
        
        if not thread_id or not message:
            return func.HttpResponse(
                json.dumps({"error": "thread_id and message are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # TODO: Implementar envio via ACS Chat SDK
        logging.info(f"Would send message to thread {thread_id}: {message[:50]}...")
        
        return func.HttpResponse(
            json.dumps({
                "status": "sent",
                "thread_id": thread_id,
                "message_id": "mock_message_id"
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error sending chat message: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
