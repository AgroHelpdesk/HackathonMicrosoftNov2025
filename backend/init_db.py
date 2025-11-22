"""
Initialize database with mock data.
"""
from database import engine, Base, SessionLocal, Ticket, TicketStep, Agent, Runbook, Metric, Plot, Message
from datetime import datetime
import json

# Mock Data (copied from main.py)
AGENTS_DATA = [
  { "id": 'field-sense', "name": 'FieldSense', "role": 'Intent Agent' },
  { "id": 'farm-ops', "name": 'FarmOps', "role": 'Info Collector' },
  { "id": 'agro-brain', "name": 'AgroBrain', "role": 'Knowledge Agent' },
  { "id": 'runbook-master', "name": 'RunbookMaster', "role": 'Decision Agent' },
  { "id": 'explain-it', "name": 'ExplainIt', "role": 'Transparency Agent' }
]

TICKETS_DATA = [
  {
    "id": 'T-001',
    "type": 'Field Diagnosis',
    "summary": 'Leaf photos with spots, possible fungus',
    "channel": 'WhatsApp',
    "location": 'Plot 22',
    "crop": 'Soybean',
    "stage": 'V5',
    "images": ['/images/leaf-1.jpg'],
    "steps": [
      { "agent": 'field-sense', "text": 'Identified phytosanitary intention', "ts": '2025-11-14T08:05:00' },
      { "agent": 'farm-ops', "text": 'Requested crop, age and additional photo', "ts": '2025-11-14T08:06:12' }
    ],
    "status": 'open',
    "decision": None,
    "messages": [
        { "sender": 'user', "text": 'I found some caterpillars in plot 22. Can you see what it is?', "ts": '2025-11-14T08:00:00' },
        { "sender": 'agent', "text": 'Sure, can you send me a photo?', "ts": '2025-11-14T08:01:00' },
        { "sender": 'user', "text": '[Photo sent]', "ts": '2025-11-14T08:02:00' },
        { "sender": 'agent', "text": 'I analyzed the photo and identified Helicoverpa armigera caterpillar. Since your crop is at V5 stage and the weather allows inspection, I recommend monitoring 3 more points in the plot. Here is the automatic report with current risk and suggested locations to check. I also notified agronomist Maria, who will review the case.', "ts": '2025-11-14T08:05:00' }
    ]
  },
  {
    "id": 'T-002',
    "type": 'Equipment Failure',
    "summary": 'Harvester vibrating',
    "channel": 'WhatsApp',
    "location": 'Plot 12',
    "crop": 'Corn',
    "images": ['/images/machine-1.jpg'],
    "steps": [
      { "agent": 'field-sense', "text": 'Mechanical failure detected', "ts": '2025-11-14T06:02:11' },
      { "agent": 'farm-ops', "text": 'Collected telemetry and last service', "ts": '2025-11-14T06:03:33' }
    ],
    "status": 'open',
    "decision": 'escalate',
    "messages": [
        { "sender": 'user', "text": 'My harvester is vibrating strongly in plot 12.', "ts": '2025-11-14T06:00:00' },
        { "sender": 'agent', "text": 'Understood. I will check your machine now.', "ts": '2025-11-14T06:01:00' },
        { "sender": 'agent', "text": 'Carlos, I checked the telemetry of CH670-02 and confirmed vibration above the limit. This may indicate wear or something stuck in the rotor. For safety, stop the machine now. I activated mechanic João Lima, who has already received your location and failure data. I will notify when he is on the way.', "ts": '2025-11-14T06:05:00' }
    ]
  },
  {
    "id": 'T-003',
    "type": 'Input Stock',
    "summary": 'Low urea in warehouse',
    "channel": 'ERP',
    "location": 'North Warehouse',
    "crop": 'Various',
    "images": [],
    "steps": [
      { "agent": 'field-sense', "text": 'Stock request', "ts": '2025-11-13T12:01:01' },
      { "agent": 'agro-brain', "text": 'Checking consumption and forecast', "ts": '2025-11-13T12:02:10' }
    ],
    "status": 'resolved',
    "decision": 'auto-order',
    "messages": []
  }
]

RUNBOOKS_DATA = [
  {
    "id": 'RB-01',
    "name": 'Generate Pest Report',
    "description": 'Analyzes image and produces preliminary report with georeferenced points',
    "safe": True
  },
  {
    "id": 'RB-02',
    "name": 'Open Urgent Work Order',
    "description": 'Creates a work order and notifies on-duty mechanic',
    "safe": False
  },
  {
    "id": 'RB-03',
    "name": 'Stock Inquiry',
    "description": 'Checks balance and suggests automatic replenishment',
    "safe": True
  },
  {
    "id": 'RB-04',
    "name": 'Pre-fill ART',
    "description": 'Generates preliminary PDF for signature',
    "safe": False
  }
]

METRICS_DATA = {
  "reduction": 65,
  "avgResolutionTime": 12,
  "accuracy": 92,
  "escalated": 8,
  "topSymptoms": [
    { "machine": 'Harvester', "symptom": 'Vibration', "percentage": 45 },
    { "machine": 'Planter', "symptom": 'Sensor Failure', "percentage": 30 },
    { "machine": 'Sprayer', "symptom": 'Leakage', "percentage": 15 }
  ]
}

PLOTS_DATA = [
  { "id": 'T-22', "crop": 'Soybean', "status": 'Pest Alert', "lat": -22.5, "lng": -47.5 },
  { "id": 'T-12', "crop": 'Corn', "status": 'Maintenance', "lat": -22.6, "lng": -47.6 },
  { "id": 'T-07', "crop": 'Cotton', "status": 'Normal', "lat": -22.7, "lng": -47.7 }
]

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(Agent).first():
        print("Database already initialized.")
        db.close()
        return

    print("Seeding data...")
    
    # Agents
    for agent in AGENTS_DATA:
        db.add(Agent(**agent))
    
    # Runbooks
    for runbook in RUNBOOKS_DATA:
        db.add(Runbook(**runbook))
        
    # Metrics
    db.add(Metric(
        reduction=METRICS_DATA['reduction'],
        avgResolutionTime=METRICS_DATA['avgResolutionTime'],
        accuracy=METRICS_DATA['accuracy'],
        escalated=METRICS_DATA['escalated'],
        topSymptoms=METRICS_DATA['topSymptoms']
    ))
    
    # Plots
    for plot in PLOTS_DATA:
        db.add(Plot(**plot))
        
    # Tickets
    for ticket_data in TICKETS_DATA:
        steps_data = ticket_data.pop('steps', [])
        messages_data = ticket_data.pop('messages', [])
        
        ticket = Ticket(**ticket_data)
        db.add(ticket)
        db.flush() # Get ID
        
        for step in steps_data:
            db.add(TicketStep(ticket_id=ticket.id, **step))
            
        for msg in messages_data:
            db.add(Message(ticket_id=ticket.id, **msg))
            
    db.commit()
    db.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
