"""
Azure Functions App - Agro Auto-Resolve Backend
"""
import azure.functions as func
import logging
import json

# Import blueprints
from functions.tickets import bp as tickets_bp
from functions.chat import bp as chat_bp
from functions.acs_chat import bp as acs_chat_bp
from functions.acs_sms import bp as acs_sms_bp
from functions.agents_api import bp as agents_bp

# Initialize Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Register blueprints
app.register_functions(tickets_bp)
app.register_functions(chat_bp)
app.register_functions(acs_chat_bp)
app.register_functions(acs_sms_bp)
app.register_functions(agents_bp)

logging.info("Function App initialized with 5 blueprints")


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    logging.info("Health check endpoint called")
    
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "Agro Auto-Resolve API",
            "version": "2.0.0",
            "blueprints": ["tickets", "chat", "acs_chat", "acs_sms", "agents"]
        }),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="/", auth_level=func.AuthLevel.ANONYMOUS)
def root(req: func.HttpRequest) -> func.HttpResponse:
    """Root endpoint with API information"""
    logging.info("Root endpoint called")
    
    return func.HttpResponse(
        json.dumps({
            "name": "Agro Auto-Resolve API",
            "version": "2.0.0",
            "description": "Auto-Resolve Service Desk Agrícola with Multi-Agent System",
            "endpoints": {
                "health": "/api/health",
                "tickets": "/api/tickets",
                "chat": "/api/chat",
                "acs_chat_webhook": "/api/acs/chat/webhook",
                "acs_sms_webhook": "/api/acs/sms/webhook",
                "agents": "/api/agents",
                "agent_metrics": "/api/agents/metrics",
                "runbooks": "/api/agents/runbooks"
            }
        }),
        status_code=200,
        mimetype="application/json"
    )
