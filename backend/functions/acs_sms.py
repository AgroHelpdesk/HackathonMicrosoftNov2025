"""
ACS SMS Integration - Azure Communication Services SMS
"""
import azure.functions as func
import logging
import json
from typing import Dict, Any
from datetime import datetime

# Importar orquestrador de agentes
from agents.orchestrator import AgentOrchestrator

# Blueprint para funções SMS
bp = func.Blueprint()

# Inicializar orquestrador
orchestrator = AgentOrchestrator()


@bp.route(route="acs/sms/webhook", methods=["POST"])
async def acs_sms_webhook(req: func.HttpRequest) -> func.HttpResponse:
    """
    Webhook para receber eventos de SMS do ACS.
    
    Processa mensagens SMS recebidas e responde através do sistema de agentes.
    """
    logging.info("ACS SMS webhook triggered")
    
    try:
        # Parse do evento
        event_data = req.get_json()
        event_type = event_data.get("eventType")
        
        logging.info(f"Received ACS SMS event: {event_type}")
        
        # Processar apenas eventos de SMS recebido
        if event_type == "Microsoft.Communication.SMSReceived":
            await _process_sms_message(event_data)
            
            return func.HttpResponse(
                json.dumps({"status": "processed"}),
                status_code=200,
                mimetype="application/json"
            )
        
        # Eventos de delivery report
        elif event_type == "Microsoft.Communication.SMSDeliveryReportReceived":
            _log_delivery_report(event_data)
            return func.HttpResponse(
                json.dumps({"status": "logged"}),
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
        logging.error(f"Error processing ACS SMS webhook: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


async def _process_sms_message(event_data: Dict[str, Any]):
    """Processa mensagem SMS recebida"""
    try:
        data = event_data.get("data", {})
        
        # Extrair informações da mensagem
        message = data.get("message", "")
        from_number = data.get("from", "")
        to_number = data.get("to", "")
        message_id = data.get("messageId", "")
        
        logging.info(f"Processing SMS from {from_number}: {message[:50]}...")
        
        # Processar através do orquestrador
        result = await orchestrator.process_message(
            message=message,
            user_id=from_number,  # Usar número de telefone como user_id
            images=[],  # SMS não suporta imagens
            metadata={
                "from_number": from_number,
                "to_number": to_number,
                "message_id": message_id,
                "channel": "sms",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Enviar resposta de volta via SMS
        if result["success"]:
            await _send_sms_response(from_number, result)
        else:
            await _send_error_sms(from_number, result.get("error", "Unknown error"))
            
    except Exception as e:
        logging.error(f"Error in _process_sms_message: {str(e)}", exc_info=True)
        raise


async def _send_sms_response(to_number: str, result: Dict[str, Any]):
    """Envia resposta via SMS"""
    try:
        # TODO: Implementar envio real via ACS SMS SDK
        # Por enquanto, apenas log
        
        explanation = result.get("explanation", "")
        recommendations = result.get("recommendations", [])
        decision = result.get("decision", {})
        
        # Formatar mensagem SMS (limitada a 160 caracteres por segmento)
        # Simplificar para SMS
        response_message = _format_sms_response(explanation, recommendations, decision)
        
        logging.info(f"Would send SMS to {to_number}: {response_message[:100]}...")
        
        # Em produção:
        # from azure.communication.sms import SmsClient
        # sms_client = SmsClient.from_connection_string(connection_string)
        # sms_client.send(
        #     from_=from_number,
        #     to=to_number,
        #     message=response_message
        # )
        
    except Exception as e:
        logging.error(f"Error sending SMS response: {str(e)}", exc_info=True)


def _format_sms_response(explanation: str, recommendations: list, decision: Dict) -> str:
    """Formata resposta para SMS (concisa)"""
    # Extrair apenas a parte essencial da explicação
    lines = explanation.split("\n")
    
    # Pegar primeiras linhas relevantes
    essential_lines = [line for line in lines if line.strip() and not line.startswith("#")][:3]
    
    response = " ".join(essential_lines)
    
    # Adicionar primeira recomendação se houver
    if recommendations:
        response += f" Recomendação: {recommendations[0]}"
    
    # Limitar a 320 caracteres (2 segmentos SMS)
    if len(response) > 320:
        response = response[:317] + "..."
    
    return response


async def _send_error_sms(to_number: str, error: str):
    """Envia mensagem de erro via SMS"""
    error_message = f"Erro ao processar sua mensagem. Por favor, tente novamente ou ligue para suporte."
    logging.info(f"Would send error SMS to {to_number}: {error_message}")
    
    # Em produção: usar ACS SMS SDK para enviar mensagem


def _log_delivery_report(event_data: Dict[str, Any]):
    """Registra relatório de entrega de SMS"""
    data = event_data.get("data", {})
    message_id = data.get("messageId", "")
    delivery_status = data.get("deliveryStatus", "")
    
    logging.info(f"SMS delivery report - Message ID: {message_id}, Status: {delivery_status}")


@bp.route(route="acs/sms/send", methods=["POST"])
async def send_sms(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint para enviar SMS via ACS programaticamente.
    
    Body:
        {
            "to": "+5511999999999",
            "message": "message content"
        }
    """
    logging.info("Send SMS endpoint called")
    
    try:
        req_body = req.get_json()
        to_number = req_body.get("to")
        message = req_body.get("message")
        
        if not to_number or not message:
            return func.HttpResponse(
                json.dumps({"error": "to and message are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # TODO: Implementar envio via ACS SMS SDK
        logging.info(f"Would send SMS to {to_number}: {message[:50]}...")
        
        return func.HttpResponse(
            json.dumps({
                "status": "sent",
                "to": to_number,
                "message_id": "mock_message_id"
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error sending SMS: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
