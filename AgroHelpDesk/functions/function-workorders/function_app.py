"""Azure Functions app for AgroHelpDesk work order management.

This module implements Azure Functions using Python v2 programming model
for handling work order operations with Cosmos DB persistence.
"""

import json
import time
from typing import Optional

import azure.functions as func
from pydantic import ValidationError

from config.settings import get_settings
from models.work_order import WorkOrderCreate
from services.cosmos_service import CosmosService, CosmosDBError
from utils.logger import get_logger, log_function_start, log_function_end, log_error
from utils.validators import validate_work_order_data
from utils.response_builder import (
    build_success_response,
    build_error_response,
    build_validation_error_response,
    build_not_found_response,
    build_server_error_response
)

# Initialize Function App
app = func.FunctionApp()
logger = get_logger(__name__)

# Initialize settings (this will also initialize Key Vault if configured)
settings = get_settings()
logger.info("Function App initialized with centralized configuration")

# Initialize Cosmos Service (singleton)
cosmos_service = CosmosService()


@app.route(
    route="workorders",
    methods=["POST"],
    auth_level=func.AuthLevel.FUNCTION
)
async def create_work_order(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new work order and save to Cosmos DB.
    
    HTTP POST /api/workorders
    
    Request Body:
    {
        "title": "Issue title",
        "description": "Detailed description",
        "category": "machinery|irrigation|planting|harvesting|inputs|soil|pest|other",
        "priority": "low|medium|high|critical",
        "assigned_specialist": "Specialist name",
        "machine_id": "Optional machine ID",
        "field_id": "Optional field ID",
        "estimated_time_hours": 2.0,
        "symptoms": "Optional symptoms",
        "requester_id": "Optional requester ID",
        "requester_contact": "Optional contact info"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "id": "uuid",
            "order_id": "OS-XXXXXXXX",
            "title": "...",
            ...
        },
        "message": "Work order created successfully",
        "timestamp": "2025-11-26T10:30:00Z"
    }
    """
    start_time = time.time()
    log_function_start(logger, "create_work_order", method=req.method)
    
    try:
        # Parse request body
        try:
            request_data = req.get_json()
        except ValueError:
            logger.warning("Invalid JSON in request body")
            return func.HttpResponse(
                **build_error_response(
                    "Invalid JSON format in request body",
                    status_code=400,
                    error_code="INVALID_JSON"
                )
            )
        
        # Validate required data
        is_valid, validation_errors = validate_work_order_data(request_data)
        if not is_valid:
            logger.warning(f"Validation failed: {validation_errors}")
            return func.HttpResponse(**build_validation_error_response(validation_errors))
        
        # Parse into Pydantic model
        try:
            work_order_create = WorkOrderCreate(**request_data)
        except ValidationError as e:
            logger.warning(f"Pydantic validation failed: {e}")
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            return func.HttpResponse(**build_validation_error_response(error_messages))
        
        # Create work order in Cosmos DB
        try:
            work_order = await cosmos_service.create_work_order(work_order_create)
            
            duration_ms = (time.time() - start_time) * 1000
            log_function_end(logger, "create_work_order", duration_ms)
            
            return func.HttpResponse(
                **build_success_response(
                    data=work_order.model_dump(mode='json'),
                    status_code=201,
                    message=f"Work order {work_order.order_id} created successfully"
                )
            )
            
        except CosmosDBError as e:
            log_error(logger, e, "Cosmos DB operation failed")
            return func.HttpResponse(
                **build_error_response(
                    f"Failed to create work order: {str(e)}",
                    status_code=500,
                    error_code="COSMOS_ERROR"
                )
            )
    
    except Exception as e:
        log_error(logger, e, "Unexpected error in create_work_order")
        return func.HttpResponse(**build_server_error_response(e))


@app.route(
    route="workorders/{order_id}",
    methods=["GET"],
    auth_level=func.AuthLevel.FUNCTION
)
async def get_work_order(req: func.HttpRequest) -> func.HttpResponse:
    """Retrieve a work order by order_id.
    
    HTTP GET /api/workorders/{order_id}
    
    Response:
    {
        "success": true,
        "data": {
            "id": "uuid",
            "order_id": "OS-XXXXXXXX",
            ...
        },
        "timestamp": "2025-11-26T10:30:00Z"
    }
    """
    start_time = time.time()
    order_id = req.route_params.get('order_id')
    
    log_function_start(logger, "get_work_order", order_id=order_id)
    
    try:
        if not order_id:
            return func.HttpResponse(
                **build_error_response(
                    "Missing order_id parameter",
                    status_code=400,
                    error_code="MISSING_PARAMETER"
                )
            )
        
        # Retrieve from Cosmos DB
        try:
            work_order = await cosmos_service.get_work_order(order_id)
            
            if not work_order:
                return func.HttpResponse(
                    **build_not_found_response(f"Work order {order_id}")
                )
            
            duration_ms = (time.time() - start_time) * 1000
            log_function_end(logger, "get_work_order", duration_ms)
            
            return func.HttpResponse(
                **build_success_response(
                    data=work_order.model_dump(mode='json')
                )
            )
            
        except CosmosDBError as e:
            log_error(logger, e, "Cosmos DB operation failed")
            return func.HttpResponse(
                **build_error_response(
                    f"Failed to retrieve work order: {str(e)}",
                    status_code=500,
                    error_code="COSMOS_ERROR"
                )
            )
    
    except Exception as e:
        log_error(logger, e, "Unexpected error in get_work_order")
        return func.HttpResponse(**build_server_error_response(e))


@app.route(
    route="workorders/{order_id}/status",
    methods=["PATCH"],
    auth_level=func.AuthLevel.FUNCTION
)
async def update_work_order_status(req: func.HttpRequest) -> func.HttpResponse:
    """Update work order status.
    
    HTTP PATCH /api/workorders/{order_id}/status
    
    Request Body:
    {
        "status": "pending|assigned|in_progress|completed|cancelled|on_hold",
        "note": "Optional status change note"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "id": "uuid",
            "order_id": "OS-XXXXXXXX",
            "status": "completed",
            ...
        },
        "message": "Status updated successfully",
        "timestamp": "2025-11-26T10:30:00Z"
    }
    """
    start_time = time.time()
    order_id = req.route_params.get('order_id')
    
    log_function_start(logger, "update_work_order_status", order_id=order_id)
    
    try:
        if not order_id:
            return func.HttpResponse(
                **build_error_response(
                    "Missing order_id parameter",
                    status_code=400,
                    error_code="MISSING_PARAMETER"
                )
            )
        
        # Parse request body
        try:
            request_data = req.get_json()
        except ValueError:
            return func.HttpResponse(
                **build_error_response(
                    "Invalid JSON format in request body",
                    status_code=400,
                    error_code="INVALID_JSON"
                )
            )
        
        # Validate status
        status = request_data.get('status')
        if not status:
            return func.HttpResponse(
                **build_error_response(
                    "Missing 'status' field",
                    status_code=400,
                    error_code="MISSING_FIELD"
                )
            )
        
        valid_statuses = ["pending", "assigned", "in_progress", "completed", "cancelled", "on_hold"]
        if status not in valid_statuses:
            return func.HttpResponse(
                **build_error_response(
                    f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    status_code=400,
                    error_code="INVALID_STATUS"
                )
            )
        
        note = request_data.get('note')
        
        # Update in Cosmos DB
        try:
            work_order = await cosmos_service.update_work_order_status(
                order_id, status, note
            )
            
            if not work_order:
                return func.HttpResponse(
                    **build_not_found_response(f"Work order {order_id}")
                )
            
            duration_ms = (time.time() - start_time) * 1000
            log_function_end(logger, "update_work_order_status", duration_ms)
            
            return func.HttpResponse(
                **build_success_response(
                    data=work_order.model_dump(mode='json'),
                    message=f"Work order {order_id} status updated to {status}"
                )
            )
            
        except CosmosDBError as e:
            log_error(logger, e, "Cosmos DB operation failed")
            return func.HttpResponse(
                **build_error_response(
                    f"Failed to update work order: {str(e)}",
                    status_code=500,
                    error_code="COSMOS_ERROR"
                )
            )
    
    except Exception as e:
        log_error(logger, e, "Unexpected error in update_work_order_status")
        return func.HttpResponse(**build_server_error_response(e))


@app.route(
    route="workorders",
    methods=["GET"],
    auth_level=func.AuthLevel.FUNCTION
)
async def list_work_orders(req: func.HttpRequest) -> func.HttpResponse:
    """List work orders with optional filters.
    
    HTTP GET /api/workorders?status=pending&category=irrigacao&priority=alta&limit=50
    
    Query Parameters:
    - status: Filter by status
    - category: Filter by category
    - priority: Filter by priority
    - limit: Maximum results (default 100, max 1000)
    
    Response:
    {
        "success": true,
        "data": [
            {
                "id": "uuid",
                "order_id": "OS-XXXXXXXX",
                ...
            },
            ...
        ],
        "count": 10,
        "timestamp": "2025-11-26T10:30:00Z"
    }
    """
    start_time = time.time()
    log_function_start(logger, "list_work_orders")
    
    try:
        # Extract query parameters
        status = req.params.get('status')
        category = req.params.get('category')
        priority = req.params.get('priority')
        
        limit = req.params.get('limit', '100')
        try:
            limit = int(limit)
            if limit < 1 or limit > 1000:
                limit = 100
        except ValueError:
            limit = 100
        
        # Query Cosmos DB
        try:
            work_orders = await cosmos_service.list_work_orders(
                status=status,
                category=category,
                priority=priority,
                limit=limit
            )
            
            duration_ms = (time.time() - start_time) * 1000
            log_function_end(logger, "list_work_orders", duration_ms)
            
            response_data = {
                "items": [wo.model_dump(mode='json') for wo in work_orders],
                "count": len(work_orders)
            }
            
            return func.HttpResponse(
                **build_success_response(data=response_data)
            )
            
        except CosmosDBError as e:
            log_error(logger, e, "Cosmos DB operation failed")
            return func.HttpResponse(
                **build_error_response(
                    f"Failed to list work orders: {str(e)}",
                    status_code=500,
                    error_code="COSMOS_ERROR"
                )
            )
    
    except Exception as e:
        log_error(logger, e, "Unexpected error in list_work_orders")
        return func.HttpResponse(**build_server_error_response(e))


@app.route(
    route="health",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint.
    
    HTTP GET /api/health
    
    Response:
    {
        "success": true,
        "data": {
            "status": "healthy",
            "service": "agrohelpdesk-functions",
            "version": "1.0.0",
            "configuration": {
                "key_vault": "enabled|disabled",
                "cosmos_db": "connected|not_initialized"
            }
        },
        "timestamp": "2025-11-26T10:30:00Z"
    }
    """
    # Get configuration status
    current_settings = get_settings()
    configuration_status = {
        "key_vault": "enabled" if current_settings.use_key_vault else "disabled",
        "cosmos_db": "connected" if cosmos_service._client else "not_initialized"
    }
    
    return func.HttpResponse(
        **build_success_response(
            data={
                "status": "healthy",
                "service": "agrohelpdesk-functions",
                "version": "1.0.0",
                "configuration": configuration_status
            }
        )
    )
