"""
Azure Functions App - Agro Auto-Resolve Backend
Main application with HTTP endpoints for chat API
"""

import azure.functions as func
import logging
import json
import time
from typing import Dict, Any

from models import ChatRequest, ChatResponse, AgentResponse
from services import OpenAIService, SearchService
from agents import FieldSenseAgent, AgroBrainAgent, RunbookMasterAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create function app
app = func.FunctionApp()

# Initialize services (lazy loading)
_openai_service = None
_search_service = None
_field_sense = None
_agro_brain = None
_runbook_master = None


def get_services():
    """Initialize and return services (singleton pattern)"""
    global _openai_service, _search_service, _field_sense, _agro_brain, _runbook_master
    
    if _openai_service is None:
        logger.info("Initializing services...")
        _openai_service = OpenAIService()
        _search_service = SearchService()
        _field_sense = FieldSenseAgent(_openai_service)
        _agro_brain = AgroBrainAgent(_openai_service, _search_service)
        _runbook_master = RunbookMasterAgent(_openai_service)
        logger.info("Services initialized successfully")
    
    return _openai_service, _search_service, _field_sense, _agro_brain, _runbook_master


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    logger.info("Health check requested")
    
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "Agro Auto-Resolve API",
            "version": "1.0.0"
        }),
        mimetype="application/json",
        status_code=200
    )


@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main chat endpoint
    Orchestrates the three agents to process user messages
    """
    logger.info("Chat request received")
    
    try:
        # Parse request body
        req_body = req.get_json()
        chat_request = ChatRequest(**req_body)
        
        logger.info(f"Processing message: {chat_request.message[:50]}...")
        
        # Get services
        openai_service, search_service, field_sense, agro_brain, runbook_master = get_services()
        
        # Prepare context
        context_dict = chat_request.context.dict() if chat_request.context else {}
        
        # Agent responses list
        agent_responses = []
        
        # Step 1: FieldSense - Classify intent
        logger.info("Step 1: Running FieldSense...")
        start_time = time.time()
        intent_result = field_sense.classify(chat_request.message, context_dict)
        field_sense_time = time.time() - start_time
        
        agent_responses.append(AgentResponse(
            name="FieldSense",
            data=intent_result,
            executionTime=field_sense_time
        ))
        
        # Step 2: AgroBrain - Retrieve knowledge
        logger.info("Step 2: Running AgroBrain...")
        start_time = time.time()
        knowledge_result = agro_brain.retrieve_knowledge(
            query=chat_request.message,
            intent=intent_result["intent"]
        )
        agro_brain_time = time.time() - start_time
        
        agent_responses.append(AgentResponse(
            name="AgroBrain",
            data=knowledge_result,
            executionTime=agro_brain_time
        ))
        
        # Step 3: RunbookMaster - Decide action
        logger.info("Step 3: Running RunbookMaster...")
        start_time = time.time()
        decision_result = runbook_master.decide_action(
            message=chat_request.message,
            intent=intent_result["intent"],
            knowledge_answer=knowledge_result["answer"],
            context=context_dict
        )
        runbook_master_time = time.time() - start_time
        
        agent_responses.append(AgentResponse(
            name="RunbookMaster",
            data=decision_result,
            executionTime=runbook_master_time
        ))
        
        # Build suggested actions
        suggested_actions = []
        if decision_result["action"] != "ESCALATE":
            suggested_actions.append(decision_result["description"])
        else:
            suggested_actions.append("Encaminhar para atendimento humano")
        
        # Build final response
        response = ChatResponse(
            response=knowledge_result["answer"],
            agents=agent_responses,
            suggestedActions=suggested_actions,
            ticketId=chat_request.ticket_id
        )
        
        logger.info(f"Chat processing completed successfully (total time: {field_sense_time + agro_brain_time + runbook_master_time:.2f}s)")
        
        return func.HttpResponse(
            response.model_dump_json(by_alias=True),
            mimetype="application/json",
            status_code=200
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid request format", "details": str(e)}),
            mimetype="application/json",
            status_code=400
        )
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            mimetype="application/json",
            status_code=500
        )
