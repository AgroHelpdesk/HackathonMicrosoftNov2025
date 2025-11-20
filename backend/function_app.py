"""
Azure Functions App - Agro Auto-Resolve Backend
"""
import azure.functions as func
import logging
import json
from datetime import datetime

# Importar funções
from functions.tickets import bp as tickets_bp
from functions.chat import bp as chat_bp
from functions.agents import bp as agents_bp
from functions.search import bp as search_bp

# Criar app
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Registrar blueprints
app.register_functions(tickets_bp)
app.register_functions(chat_bp)
app.register_functions(agents_bp)
app.register_functions(search_bp)


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    logging.info('Health check requested')
    
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "agro-autoresolve-backend",
            "version": "1.0.0"
        }),
        mimetype="application/json",
        status_code=200
    )


@app.route(route="", methods=["GET"])
def root(req: func.HttpRequest) -> func.HttpResponse:
    """Root endpoint"""
    return func.HttpResponse(
        json.dumps({
            "message": "Agro Auto-Resolve API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/health",
                "tickets": "/api/tickets",
                "chat": "/api/chat",
                "agents": "/api/agents",
                "search": "/api/search"
            }
        }),
        mimetype="application/json",
        status_code=200
    )
