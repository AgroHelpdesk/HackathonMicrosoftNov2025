"""
Tickets Functions - Gerenciamento de tickets
"""
import azure.functions as func
import logging
import json
import os
from datetime import datetime
from azure.cosmos import CosmosClient, exceptions
from typing import Optional

# Criar blueprint
bp = func.Blueprint()

# Configuração Cosmos DB
COSMOS_ENDPOINT = os.getenv('COSMOS_DB_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_DB_KEY')
DATABASE_NAME = os.getenv('COSMOS_DB_DATABASE', 'agro-autoresolve')
CONTAINER_NAME = 'tickets'

def get_cosmos_container():
    """Obtém o container do Cosmos DB"""
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.get_database_client(DATABASE_NAME)
    return database.get_container_client(CONTAINER_NAME)


@bp.route(route="tickets", methods=["GET"])
def get_tickets(req: func.HttpRequest) -> func.HttpResponse:
    """Lista todos os tickets"""
    logging.info('GET /api/tickets')
    
    try:
        container = get_cosmos_container()
        
        # Query parameters
        status = req.params.get('status')
        limit = int(req.params.get('limit', 100))
        
        # Build query
        if status:
            query = f"SELECT * FROM c WHERE c.status = @status ORDER BY c.created_at DESC OFFSET 0 LIMIT {limit}"
            parameters = [{"name": "@status", "value": status}]
        else:
            query = f"SELECT * FROM c ORDER BY c.created_at DESC OFFSET 0 LIMIT {limit}"
            parameters = None
        
        # Execute query
        items = list(container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        ))
        
        return func.HttpResponse(
            json.dumps(items, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
    
    except Exception as e:
        logging.error(f"Error getting tickets: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@bp.route(route="tickets/{ticket_id}", methods=["GET"])
def get_ticket(req: func.HttpRequest) -> func.HttpResponse:
    """Obtém um ticket específico"""
    ticket_id = req.route_params.get('ticket_id')
    logging.info(f'GET /api/tickets/{ticket_id}')
    
    try:
        container = get_cosmos_container()
        item = container.read_item(item=ticket_id, partition_key=ticket_id)
        
        return func.HttpResponse(
            json.dumps(item, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
    
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse(
            json.dumps({"error": "Ticket not found"}),
            mimetype="application/json",
            status_code=404
        )
    except Exception as e:
        logging.error(f"Error getting ticket: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@bp.route(route="tickets", methods=["POST"])
def create_ticket(req: func.HttpRequest) -> func.HttpResponse:
    """Cria um novo ticket"""
    logging.info('POST /api/tickets')
    
    try:
        # Parse request body
        req_body = req.get_json()
        
        # Generate ticket ID
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        ticket_id = f"T-{timestamp}"
        
        # Create ticket
        ticket = {
            "id": ticket_id,
            "type": req_body.get("type", "General"),
            "summary": req_body.get("summary", ""),
            "channel": req_body.get("channel", "API"),
            "location": req_body.get("location"),
            "crop": req_body.get("crop"),
            "stage": req_body.get("stage"),
            "images": req_body.get("images", []),
            "steps": [],
            "status": "open",
            "decision": None,
            "resolution": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": req_body.get("metadata", {})
        }
        
        # Save to Cosmos DB
        container = get_cosmos_container()
        container.create_item(body=ticket)
        
        return func.HttpResponse(
            json.dumps(ticket, ensure_ascii=False),
            mimetype="application/json",
            status_code=201
        )
    
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error creating ticket: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )


@bp.route(route="tickets/{ticket_id}", methods=["PATCH"])
def update_ticket(req: func.HttpRequest) -> func.HttpResponse:
    """Atualiza um ticket"""
    ticket_id = req.route_params.get('ticket_id')
    logging.info(f'PATCH /api/tickets/{ticket_id}')
    
    try:
        container = get_cosmos_container()
        
        # Get existing ticket
        ticket = container.read_item(item=ticket_id, partition_key=ticket_id)
        
        # Parse updates
        req_body = req.get_json()
        
        # Update fields
        if 'status' in req_body:
            ticket['status'] = req_body['status']
        if 'decision' in req_body:
            ticket['decision'] = req_body['decision']
        if 'resolution' in req_body:
            ticket['resolution'] = req_body['resolution']
        if 'steps' in req_body:
            ticket['steps'].extend(req_body['steps'])
        if 'metadata' in req_body:
            ticket['metadata'].update(req_body['metadata'])
        
        ticket['updated_at'] = datetime.utcnow().isoformat()
        
        # Save
        container.replace_item(item=ticket_id, body=ticket)
        
        return func.HttpResponse(
            json.dumps(ticket, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )
    
    except exceptions.CosmosResourceNotFoundError:
        return func.HttpResponse(
            json.dumps({"error": "Ticket not found"}),
            mimetype="application/json",
            status_code=404
        )
    except Exception as e:
        logging.error(f"Error updating ticket: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
