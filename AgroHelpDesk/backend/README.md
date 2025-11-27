# 🧠 AgroHelpDesk Backend - Multi-Agent AI System

Intelligent backend system powered by **Semantic Kernel**, **Azure OpenAI**, and **multi-agent orchestration** for agricultural technical support automation.

## 📋 Overview

The backend implements a sophisticated multi-agent system using **Semantic Kernel** and **Azure OpenAI** to provide intelligent, automated responses to agricultural support requests.

**Current Implementation:**
- ✅ Multi-agent orchestration with Semantic Kernel
- ✅ Azure OpenAI (GPT-4o-mini) integration
- ✅ Azure Cognitive Search with RAG (AgroBrain)
- ✅ Azure Key Vault with Managed Identity (production)
- ✅ In-memory session management
- ✅ Work order creation via Azure Functions
- ✅ RESTful API with FastAPI
- ✅ Comprehensive logging and error handling

**Not Yet Implemented (Future):**
- 🔄 Azure Communication Services integration (SMS/WhatsApp)
- 🔄 Redis session persistence

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── agents/                 # AI Agent implementations
│   │   ├── field_sense.py     # Intent classification agent
│   │   ├── farm_ops.py        # Information collector agent
│   │   ├── agro_brain.py      # Knowledge expert agent
│   │   ├── runbook_master.py  # Decision maker agent
│   │   └── explain_it.py      # Transparency agent
│   ├── api/                    # API endpoints
│   │   ├── chat.py            # Chat endpoints
│   │   ├── orchestrator.py    # Agent orchestration endpoint
│   │   ├── acs_webhook.py     # ACS SMS/WhatsApp webhook
│   │   └── health.py          # Health check
│   ├── config/                 # Configuration
│   │   ├── settings.py        # Environment settings
│   │   ├── kernel_config.py   # Semantic Kernel setup
│   │   ├── agent_config.py    # Agent configurations
│   │   └── keyvault.py        # Azure Key Vault integration
│   ├── core/                   # Core business logic
│   │   ├── orchestrator.py    # Agent orchestration
│   │   ├── sk_base_agent.py   # Base agent class
│   │   ├── context_builder.py # Context management
│   │   ├── search.py          # Azure Cognitive Search
│   │   └── automation.py      # Runbook automation
│   ├── plugins/                # Semantic Kernel plugins
│   │   ├── azure_search_plugin.py
│   │   ├── work_order_plugin.py
│   │   └── runbook_plugin.py
│   ├── schemas/                # Pydantic models
│   │   ├── orchestrator_schemas.py
│   │   └── llm_responses.py
│   ├── services/               # External service integrations
│   │   ├── acs_identity.py
│   │   ├── acs_messages.py
│   │   ├── acs_threads.py
│   │   └── session_store.py
│   └── utils/                  # Utilities
│       ├── logger.py
│       ├── json_parser.py
│       ├── query_builders.py
│       └── response_builders.py
├── pyproject.toml              # Project metadata
└── requirements.txt            # Dependencies
```

## 🤖 AI Agents

### 1. FieldSense (Intent Classifier)
**Purpose**: Classify user intent and route to appropriate workflow

**Capabilities**:
- Intent detection (pest control, irrigation, machinery, etc.)
- Urgency level classification (low, medium, high, critical)
- Initial category assignment
- Context extraction

**Example**:
```python
Input: "Minha irrigação está com problema no setor A3"
Output: {
    "intent": "irrigation_issue",
    "category": "irrigation",
    "urgency": "high",
    "extracted_info": {"field_id": "A3"}
}
```

### 2. FarmOps (Information Collector)
**Purpose**: Gather missing information through conversational flow

**Capabilities**:
- Identify information gaps
- Ask contextual questions
- Validate user responses
- Structure collected data

**Example**:
```python
Missing: machine_id, symptoms
Action: Ask "Qual é o código da máquina? Quais sintomas você observa?"
```

### 3. AgroBrain (Knowledge Expert)
**Purpose**: Query knowledge bases and provide technical recommendations

**Current Status**: ✅ Fully Implemented
- Azure Cognitive Search integration with RAG (Retrieval-Augmented Generation)
- MAPA knowledge base integration
- Agrofitproducts database queries
- Vector search for semantic matching
- Semantic Kernel plugin for search orchestration

**Capabilities**:
- RAG-based knowledge retrieval from Azure Cognitive Search
- Technical recommendations based on MAPA database
- Product suggestions from Agrofitproducts catalog
- Context-aware agricultural expertise

**Example**:
```python
Query: "Como controlar ferrugem em soja?"
Response: Technical guidance from MAPA knowledge base + recommended products from Agrofitproducts
```

### 4. RunbookMaster (Decision Maker)
**Purpose**: Decide between automation and escalation

**Capabilities**:
- Risk assessment
- Runbook selection
- Work order creation
- Automation execution
- Escalation decision

**Runbooks**:
- `RB-01`: Generate pest report (Safe)
- `RB-02`: Create urgent work order (Critical)
- `RB-03`: Check inventory (Safe)
- `RB-04`: Pre-fill ART report (Critical)

**Example**:
```python
Input: Critical irrigation failure
Decision: Create work order (RB-02) + Notify specialist
```

### 5. ExplainIt (Transparency Agent)
**Purpose**: Explain agent decisions and provide audit trail

**Capabilities**:
- Step-by-step explanation
- Decision rationale
- Confidence scores
- Regulatory compliance notes
- Audit trail generation

## 🚀 Getting Started

### Prerequisites

**Required:**
- Python 3.10 or higher
- Azure OpenAI access (GPT-4o-mini deployment)
- Azure Cognitive Search (RAG for AgroBrain)

**For Production Deployment:**
- Azure Key Vault (secrets management with Managed Identity)
- Azure App Service or Container Instance (for Managed Identity)

**Optional (for future features):**
- Azure Communication Services (SMS/WhatsApp)
- Redis (persistent sessions)

### Installation

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Or using poetry
poetry install
```

### Configuration

1. **Copy environment template**:
```powershell
cp .env.example .env
```

2. **Configure `.env`**:
```bash
# Azure OpenAI (Required)
OPENAI-ENDPOINT=https://YOUR_RESOURCE.openai.azure.com/
OPENAI-KEY=your_openai_key_here
OPENAI-DEPLOYMENT=gpt-4o-mini
OPENAI-API-VERSION=2024-02-15-preview

# Azure Functions - Work Orders (Required)
FUNCTIONS-URL=http://localhost:7071

# Azure Cognitive Search - RAG (Required for AgroBrain)
AZURE-SEARCH-ENDPOINT=https://YOUR_RESOURCE.search.windows.net
AZURE-SEARCH-KEY=your_search_key_here
AZURE-SEARCH-INDEX=agrohelpdesk-kb

# Application (Required)
ENVIRONMENT=development
LOG-LEVEL=INFO

# Azure Key Vault (Implemented - Disabled for local dev, enabled in production)
USE-KEY-VAULT=false  # Set to true in production with Managed Identity
# AZURE-KEY-VAULT-URL=https://your-keyvault.vault.azure.net/

# Optional - Future Features (Not Currently Used)
# ACS-ENDPOINT=https://YOUR_RESOURCE.communication.azure.com
# ACS-ACCESS-KEY=your_acs_access_key_here
# REDIS-URL=redis://localhost:6379/0
```

### Running Locally

```powershell
# Start the server
uvicorn app.main:app --reload

# Or with auto-reload on code changes
python -m app.main
```

The API will be available at: `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## 📡 API Endpoints

### Chat Endpoints

#### Start Session
```http
POST /api/chat/start-session
Content-Type: application/json

Response:
{
  "session_id": "uuid",
  "status": "active",
  "created_at": "2025-11-27T10:00:00Z"
}
```

#### Send Message
```http
POST /api/chat/message
Content-Type: application/json

{
  "session_id": "uuid",
  "message": "Minha irrigação está falhando",
  "user_id": "user123"
}

Response:
{
  "session_id": "uuid",
  "reply": "Agent response",
  "agent_type": "FieldSense",
  "flow_state": "collecting_info",
  "context": {...}
}
```

#### Get History
```http
GET /api/chat/history/{session_id}

Response:
{
  "session_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "Message",
      "timestamp": "..."
    }
  ]
}
```

#### Close Session
```http
POST /api/chat/close-session/{session_id}

Response:
{
  "ok": true,
  "message": "Session closed"
}
```

### Orchestrator Endpoint

```http
POST /api/orchestrator/process
Content-Type: application/json

{
  "user_message": "Need help with irrigation",
  "session_id": "uuid",
  "user_id": "user123"
}

Response:
{
  "final_response": "Complete agent response",
  "agent_chain": ["FieldSense", "FarmOps", "AgroBrain", "RunbookMaster"],
  "decisions": [...],
  "context": {...}
}
```

### Health Check

```http
GET /api/health

Response:
{
  "status": "healthy",
  "service": "agrohelpdesk-backend",
  "version": "1.0.0",
  "timestamp": "2025-11-27T10:00:00Z"
}
```

### ACS Webhook (SMS/WhatsApp)

**Status**: 🔄 Configured but not active

```http
POST /api/acs/webhook
Content-Type: application/json

Azure Communication Services webhook payload
```

This endpoint is prepared for future SMS/WhatsApp integration.

## 🧪 Testing

### Run Tests

```powershell
# All tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test file
pytest tests/test_agents.py

# Verbose output
pytest -v
```

### Test Structure

```
tests/
├── test_agents.py           # Agent unit tests
├── test_orchestrator.py     # Orchestration tests
├── test_api.py              # API endpoint tests
└── conftest.py              # Test fixtures
```

## 📊 Monitoring & Logging

### Structured Logging

The backend uses structured logging with different levels:

```python
from app.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Processing request", extra={"session_id": session_id})
logger.error("Failed to process", exc_info=True)
```

### Application Insights

Configure Application Insights connection string:

```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit `.env` files
- Use Azure Key Vault in production
- Rotate secrets regularly

### 2. API Authentication
```python
# Add to endpoints
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/protected")
async def protected_route(credentials = Depends(security)):
    # Validate token
    pass
```

### 3. CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🚢 Deployment

### Azure App Service

```powershell
# Create App Service
az webapp up \
  --name agrohelpdesk-backend \
  --runtime "PYTHON:3.10" \
  --sku B1

# Configure app settings
az webapp config appsettings set \
  --name agrohelpdesk-backend \
  --settings @appsettings.json
```

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```powershell
docker build -t agrohelpdesk-backend .
docker run -p 8000:8000 --env-file .env agrohelpdesk-backend
```

## 📚 Dependencies

Key dependencies:
- `fastapi` - Modern web framework
- `semantic-kernel` - AI orchestration
- `pydantic` - Data validation
- `pydantic-settings` - Configuration management
- `azure-communication-sms` - SMS integration
- `azure-search-documents` - Cognitive Search
- `azure-identity` - Azure authentication
- `uvicorn` - ASGI server

## 🔧 Troubleshooting

### Common Issues

1. **OpenAI Connection Failed**
   - Verify `OPENAI-ENDPOINT` and `OPENAI-KEY`
   - Check Azure OpenAI deployment name
   - Ensure API version is correct

2. **Module Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`
   - Check Python version (3.10+)

3. **Agent Not Responding**
   - Check logs for errors
   - Verify Semantic Kernel configuration
   - Test with simple prompts first

## 📖 Further Reading

- [Semantic Kernel Documentation](https://learn.microsoft.com/semantic-kernel)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai)
- [Pydantic Documentation](https://docs.pydantic.dev)

## 🔮 Future Enhancements

### Communication Integration
- **WhatsApp/SMS**: Azure Communication Services integration
- **Teams Bot**: Microsoft Teams channel support
- **Voice**: Speech-to-text for field workers

### Knowledge Enhancement
- **Enhanced Vector Search**: Advanced semantic capabilities
- **Knowledge Graph**: Relationship mapping between concepts
- **Multi-source Integration**: Additional knowledge bases beyond MAPA

### Infrastructure
- **Redis**: Distributed session management
- **WebSocket**: Real-time message streaming
- **Monitoring**: Enhanced Application Insights dashboards

### Advanced Features
- **Multi-language**: Support for English, Spanish
- **Offline Mode**: Cache responses for low connectivity
- **Analytics**: Advanced metrics and reporting

---

**Built with 🤖 using Semantic Kernel and Azure AI**
