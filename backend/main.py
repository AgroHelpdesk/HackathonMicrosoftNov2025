from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime
from sqlalchemy.orm import Session
from database import get_db, Ticket, Agent, Runbook, Metric, Plot, Message
from agents.orchestrator import AgentOrchestrator
from routers import functions_emulation

app = FastAPI(title="Agro Auto-Resolve API")

# Include Emulation Router
app.include_router(functions_emulation.router)

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Orchestrator
orchestrator = AgentOrchestrator()

# --- Models ---

class ChatRequest(BaseModel):
    message: str
    ticketId: Optional[str] = None

class TicketResponse(BaseModel):
    id: str
    type: str
    summary: str
    channel: str
    location: str
    crop: str
    stage: Optional[str]
    images: List[str]
    status: str
    decision: Optional[str]
    steps: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]

    class Config:
        from_attributes = True

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Agro Auto-Resolve API is running"}

@app.get("/api/tickets")
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    # Manually format to include steps and messages properly if needed, 
    # or rely on Pydantic ORM mode if relationships are set up correctly.
    # For simplicity here, we return the objects and let FastAPI/Pydantic handle serialization
    return tickets

@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.get("/api/agents")
def get_agents(db: Session = Depends(get_db)):
    return db.query(Agent).all()

@app.get("/api/runbooks")
def get_runbooks(db: Session = Depends(get_db)):
    return db.query(Runbook).all()

@app.get("/api/metrics")
def get_metrics(db: Session = Depends(get_db)):
    return db.query(Metric).first()

@app.get("/api/plots")
def get_plots(db: Session = Depends(get_db)):
    return db.query(Plot).all()

@app.post("/api/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Save User Message
    user_msg = Message(
        ticket_id=request.ticketId,
        sender='user',
        text=request.message,
        ts=datetime.datetime.utcnow().isoformat()
    )
    db.add(user_msg)
    db.commit()
    
    # 2. Process with Orchestrator
    result = await orchestrator.process_message(
        message=request.message,
        user_id="user_123", # Mock user ID
        metadata={"ticket_id": request.ticketId} if request.ticketId else {}
    )
    
    response_text = ""
    if result["success"]:
        # Construct a friendly response based on the result
        if result.get("explanation"):
            response_text = result["explanation"]
        elif result.get("decision"):
             response_text = f"Decision made: {result['decision']}"
        else:
            # Fallback if no explanation
            response_text = "Processed successfully."
            
            # Add recommendations if available
            if result.get("recommendations"):
                response_text += "\n\nRecommendations:\n" + "\n".join([f"- {r}" for r in result["recommendations"]])

    else:
        response_text = f"Error processing request: {result.get('error')}"

    # 3. Save Agent Response
    agent_msg = Message(
        ticket_id=request.ticketId,
        sender='agent',
        text=response_text,
        ts=datetime.datetime.utcnow().isoformat()
    )
    db.add(agent_msg)
    db.commit()
        
    return {
        "response": response_text,
        "agent": "Orchestrator", # Or specific agent if we want to show who answered
        "ts": agent_msg.ts,
        "full_result": result # Return full result for debugging/transparency UI
    }

if __name__ == "__main__":
    import uvicorn
    # Initialize DB on startup if needed, or rely on init_db.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
