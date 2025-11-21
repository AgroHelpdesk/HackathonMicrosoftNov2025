"""
Agents API - Endpoints para gerenciar e consultar agentes
"""
import azure.functions as func
import logging
import json

from agents.orchestrator import AgentOrchestrator

bp = func.Blueprint()

# Inicializar orquestrador
orchestrator = AgentOrchestrator()


@bp.route(route="agents", methods=["GET"])
def get_agents(req: func.HttpRequest) -> func.HttpResponse:
    """
    Lista todos os agentes disponíveis.
    
    Returns:
        Lista de agentes com suas informações
    """
    logging.info("Get agents endpoint called")
    
    try:
        agents_info = orchestrator.get_agent_info()
        
        return func.HttpResponse(
            json.dumps({"agents": agents_info}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error getting agents: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@bp.route(route="agents/metrics", methods=["GET"])
def get_agent_metrics(req: func.HttpRequest) -> func.HttpResponse:
    """
    Retorna métricas de todos os agentes.
    
    Returns:
        Métricas de processamento de cada agente
    """
    logging.info("Get agent metrics endpoint called")
    
    try:
        metrics = orchestrator.get_agent_metrics()
        
        return func.HttpResponse(
            json.dumps(metrics),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error getting agent metrics: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@bp.route(route="agents/runbooks", methods=["GET"])
def get_runbooks(req: func.HttpRequest) -> func.HttpResponse:
    """
    Retorna catálogo de runbooks disponíveis.
    
    Returns:
        Catálogo completo de runbooks
    """
    logging.info("Get runbooks endpoint called")
    
    try:
        catalog = orchestrator.get_runbook_catalog()
        
        return func.HttpResponse(
            json.dumps(catalog),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error getting runbooks: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


@bp.route(route="agents/process", methods=["POST"])
async def process_with_agents(req: func.HttpRequest) -> func.HttpResponse:
    """
    Processa uma mensagem através do sistema de agentes.
    
    Body:
        {
            "message": "user message",
            "user_id": "optional user id",
            "images": ["optional image urls"],
            "metadata": {}
        }
    
    Returns:
        Resultado completo do processamento pelos agentes
    """
    logging.info("Process with agents endpoint called")
    
    try:
        req_body = req.get_json()
        
        message = req_body.get("message")
        if not message:
            return func.HttpResponse(
                json.dumps({"error": "message is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        user_id = req_body.get("user_id")
        images = req_body.get("images", [])
        metadata = req_body.get("metadata", {})
        
        # Processar através do orquestrador
        result = await orchestrator.process_message(
            message=message,
            user_id=user_id,
            images=images,
            metadata=metadata
        )
        
        return func.HttpResponse(
            json.dumps(result, default=str),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error processing with agents: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
