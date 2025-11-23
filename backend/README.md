# Agro Auto-Resolve Backend API

Azure Functions backend for the Agro Auto-Resolve application, implementing the Chat API with three AI agents.

## Architecture

The backend uses Azure Functions (Python) with three specialized agents:

1. **FieldSense**: Intent classification agent
   - Classifies user requests into categories (Phytosanitary, Mechanical, Stock, General)
   - Uses Azure OpenAI GPT-4o with structured prompts

2. **AgroBrain**: Knowledge retrieval agent (RAG)
   - Searches Azure AI Search index for relevant documents
   - Generates contextual answers using retrieved knowledge
   - Provides source citations

3. **RunbookMaster**: Decision-making agent
   - Analyzes intent and knowledge to determine appropriate actions
   - Selects runbooks (RB-01 to RB-04) based on situation
   - Assesses risk levels (Safe/Critical)

## Project Structure

```
backend/
├── function_app.py          # Main Azure Functions app
├── agents/
│   ├── field_sense.py       # Intent classification
│   ├── agro_brain.py        # RAG knowledge retrieval
│   └── runbook_master.py    # Decision logic
├── services/
│   ├── openai_service.py    # Azure OpenAI client
│   └── search_service.py    # Azure AI Search client
├── models/
│   └── chat_models.py       # Request/Response models
├── requirements.txt         # Python dependencies
├── host.json               # Azure Functions config
└── local.settings.json     # Local development settings
```

## API Endpoints

### POST /api/chat

Main chat endpoint that processes user messages through all three agents.

**Request:**
```json
{
  "message": "Estou vendo manchas nas folhas do milho",
  "ticketId": "optional-ticket-id",
  "context": {
    "plotId": "P-001",
    "crop": "Milho"
  }
}
```

**Response:**
```json
{
  "response": "Baseado nos sintomas descritos...",
  "agents": [
    {
      "name": "FieldSense",
      "data": {
        "intent": "Phytosanitary",
        "confidence": 0.95,
        "reasoning": "..."
      },
      "executionTime": 0.5
    },
    {
      "name": "AgroBrain",
      "data": {
        "answer": "...",
        "sources": [...],
        "relevance": 0.88
      },
      "executionTime": 1.2
    },
    {
      "name": "RunbookMaster",
      "data": {
        "action": "RB-01",
        "description": "Generate pest report",
        "riskLevel": "Safe",
        "reasoning": "...",
        "requiresApproval": false
      },
      "executionTime": 0.6
    }
  ],
  "suggestedActions": ["Generate detailed pest report"],
  "ticketId": "optional-ticket-id"
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Agro Auto-Resolve API",
  "version": "1.0.0"
}
```

## Local Development

### Prerequisites

1. Python 3.10+
2. Azure Functions Core Tools
3. Azure CLI (logged in)

### Setup

1. Install dependencies:
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

2. Update `local.settings.json` with your Azure service endpoints

3. Start the function locally:
   ```powershell
   func start
   ```

4. Test the API:
   ```powershell
   # Health check
   curl http://localhost:7071/api/health
   
   # Chat endpoint
   curl -X POST http://localhost:7071/api/chat `
     -H "Content-Type: application/json" `
     -d '{"message": "Preciso de ajuda com pragas no milho"}'
   ```

## Environment Variables

Required environment variables (set in `local.settings.json` for local dev):

- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT`: GPT-4o deployment name
- `AZURE_OPENAI_API_VERSION`: API version (e.g., "2024-02-15-preview")
- `AZURE_SEARCH_ENDPOINT`: Azure AI Search endpoint URL
- `AZURE_SEARCH_INDEX_NAME`: Search index name (default: "agro-knowledge-base")

## Deployment

Deploy to Azure using Azure Functions Core Tools:

```powershell
func azure functionapp publish func-agro-autoresolve
```

Or use the Azure Portal / VS Code extension for deployment.

## Testing

Test individual agents:

```python
from services import OpenAIService, SearchService
from agents import FieldSenseAgent

# Initialize
openai_service = OpenAIService()
field_sense = FieldSenseAgent(openai_service)

# Test classification
result = field_sense.classify("Estou vendo manchas nas folhas")
print(result)
```

## Troubleshooting

### Authentication Errors

Make sure you're logged in to Azure CLI:
```powershell
az login
az account set --subscription <your-subscription-id>
```

### Missing Environment Variables

Check that all required environment variables are set in `local.settings.json`

### OpenAI API Errors

Verify that:
- Azure OpenAI deployment exists
- Deployment name matches the environment variable
- You have access to the OpenAI resource
