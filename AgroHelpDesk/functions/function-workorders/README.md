# ⚡ AgroHelpDesk Work Orders - Azure Functions

Azure Functions v2 application for managing agricultural work orders with **Cosmos DB** persistence, **Pydantic** validation, and comprehensive error handling.

## 📋 Overview

This Azure Functions app provides serverless HTTP endpoints for creating, querying, and managing agricultural work orders (OS - Ordem de Serviço). It integrates seamlessly with the AgroHelpDesk backend and supports automated work order creation from the AI agents.

## ✨ Features

- ✅ **Azure Functions v2** - Latest Python programming model
- ✅ **Cosmos DB Persistence** - Scalable NoSQL storage
- ✅ **Azure Key Vault Integration** - Secure secrets management
- ✅ **Managed Identity Support** - Passwordless authentication
- ✅ **Pydantic Validation** - Type-safe data models
- ✅ **Structured Logging** - Application Insights integration
- ✅ **Error Handling** - Consistent error responses
- ✅ **Health Checks** - Monitoring endpoint
- ✅ **Function Authentication** - Secure endpoints

## 🏗️ Architecture

```
function-workorders/
├── function_app.py          # All function definitions (v2 model)
├── host.json                # Functions Host configuration
├── requirements.txt         # Python dependencies
├── local.settings.json      # Local settings (gitignored)
├── local.settings.example.json  # Settings template
├── .funcignore             # Deployment exclusions
├── config/
│   ├── __init__.py
│   ├── settings.py         # Centralized configuration
│   └── keyvault.py         # Key Vault integration
├── models/
│   ├── __init__.py
│   └── work_order.py       # Pydantic schemas
├── services/
│   ├── __init__.py
│   └── cosmos_service.py   # Cosmos DB operations
└── utils/
    ├── __init__.py
    ├── logger.py           # Logging configuration
    ├── validators.py       # Data validators
    └── response_builder.py # HTTP response builders
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Azure Functions Core Tools v4](https://docs.microsoft.com/azure/azure-functions/functions-run-local)
- Azure account with Cosmos DB

### Installation

```powershell
# Navigate to directory
cd functions/function-workorders

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Copy settings template**:
```powershell
cp local.settings.example.json local.settings.json
```

2. **Configure `local.settings.json`**:

#### Option A: Using Environment Variables (Development)
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "USE_KEY_VAULT": "false",
    "COSMOS_ENDPOINT": "https://your-cosmos-account.documents.azure.com:443/",
    "COSMOS_KEY": "your_cosmos_key",
    "COSMOS_DATABASE_NAME": "agrohelpdesk",
    "COSMOS_CONTAINER_NAME": "workorders",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=...",
    "LOG_LEVEL": "INFO",
    "ENABLE_DETAILED_LOGGING": "true"
  }
}
```

#### Option B: Using Azure Key Vault (Production)
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "USE_KEY_VAULT": "true",
    "AZURE_KEY_VAULT_URL": "https://your-keyvault.vault.azure.net/",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=...",
    "LOG_LEVEL": "INFO"
  }
}
```

**Key Vault Setup**: Store these secrets in your Azure Key Vault:
- `COSMOS-ENDPOINT`
- `COSMOS-KEY`
- `COSMOS-DATABASE-NAME`
- `COSMOS-CONTAINER-NAME`

3. **Create Cosmos DB resources**:
```powershell
# Create database
az cosmosdb sql database create \
  --account-name your-cosmos-account \
  --name agrohelpdesk

# Create container
az cosmosdb sql container create \
  --account-name your-cosmos-account \
  --database-name agrohelpdesk \
  --name workorders \
  --partition-key-path "/partition_key" \
  --throughput 400
```

### Run Locally

```powershell
func start
```

Functions will be available at: `http://localhost:7071`

## 📡 API Endpoints

### 1. Create Work Order

**POST** `/api/workorders`

**Request**:
```json
{
  "title": "Irrigation system failure",
  "description": "Irregular dripping detected in field A3",
  "category": "irrigation",
  "priority": "high",
  "assigned_specialist": "Irrigation Technician",
  "machine_id": "IRRIG-001",
  "field_id": "A3",
  "estimated_time_hours": 4.0,
  "symptoms": "Irregular flow, low pressure",
  "requester_id": "user123",
  "requester_contact": "john@farm.com"
}
```

**Response (201)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "order_id": "OS-A1B2C3D4",
    "title": "Irrigation system failure",
    "status": "pending",
    "created_at": "2025-11-27T10:30:00Z",
    ...
  },
  "message": "Work order OS-A1B2C3D4 created successfully",
  "timestamp": "2025-11-27T10:30:00Z"
}
```

### 2. Get Work Order

**GET** `/api/workorders/{order_id}`

**Example**: `GET /api/workorders/OS-A1B2C3D4`

**Response (200)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "order_id": "OS-A1B2C3D4",
    ...
  },
  "timestamp": "2025-11-27T10:30:00Z"
}
```

### 3. Update Work Order Status

**PATCH** `/api/workorders/{order_id}/status`

**Request**:
```json
{
  "status": "in_progress",
  "note": "Technician John started inspection"
}
```

**Valid Statuses**:
- `pending` - Awaiting assignment
- `assigned` - Assigned to technician
- `in_progress` - Work in progress
- `completed` - Work completed
- `cancelled` - Cancelled
- `on_hold` - On hold

**Response (200)**:
```json
{
  "success": true,
  "data": {
    "order_id": "OS-A1B2C3D4",
    "status": "in_progress",
    ...
  },
  "message": "Work order OS-A1B2C3D4 status updated to in_progress"
}
```

### 4. List Work Orders

**GET** `/api/workorders?status=pending&category=irrigation&limit=50`

**Query Parameters**:
- `status` (optional) - Filter by status
- `category` (optional) - Filter by category
- `priority` (optional) - Filter by priority
- `limit` (optional) - Max results (default: 100, max: 1000)

**Response (200)**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "order_id": "OS-A1B2C3D4",
        ...
      }
    ],
    "count": 10
  }
}
```

### 5. Health Check

**GET** `/api/health`

**Response (200)**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "agrohelpdesk-functions",
    "version": "1.0.0",
    "cosmos_db": "connected"
  }
}
```

## 🔧 Data Models

### Work Order Categories

```python
class WorkOrderCategory(str, Enum):
    MACHINERY = "machinery"        # Equipment issues
    IRRIGATION = "irrigation"      # Irrigation problems
    PLANTING = "planting"         # Planting operations
    HARVESTING = "harvesting"     # Harvest operations
    INPUTS = "inputs"             # Agricultural inputs
    SOIL = "soil"                 # Soil management
    PEST = "pest"                 # Pest control
    OTHER = "other"               # Other categories
```

### Priority Levels

```python
class WorkOrderPriority(str, Enum):
    LOW = "low"                   # Low priority
    MEDIUM = "medium"             # Medium priority (default)
    HIGH = "high"                 # High priority
    CRITICAL = "critical"         # Critical - immediate attention
```

### Work Order Status

```python
class WorkOrderStatus(str, Enum):
    PENDING = "pending"           # Awaiting assignment
    ASSIGNED = "assigned"         # Assigned to technician
    IN_PROGRESS = "in_progress"   # Work in progress
    COMPLETED = "completed"       # Completed
    CANCELLED = "cancelled"       # Cancelled
    ON_HOLD = "on_hold"          # On hold
```

## 🧪 Testing

### Local Testing with curl

```powershell
# Create work order
curl -X POST http://localhost:7071/api/workorders `
  -H "Content-Type: application/json" `
  -d '{
    "title": "Irrigation test",
    "description": "Test work order creation",
    "category": "irrigation",
    "priority": "medium",
    "assigned_specialist": "Test Technician"
  }'

# Get work order
curl http://localhost:7071/api/workorders/OS-XXXXXXXX

# List work orders
curl "http://localhost:7071/api/workorders?status=pending&limit=10"

# Update status
curl -X PATCH http://localhost:7071/api/workorders/OS-XXXXXXXX/status `
  -H "Content-Type: application/json" `
  -d '{"status": "in_progress", "note": "Started work"}'
```

### Using Postman/Insomnia

Configure collection with:
- Base URL: `http://localhost:7071/api`
- Headers: `Content-Type: application/json`

## 🚢 Deployment

### Deploy to Azure

```powershell
# Login to Azure
az login

# Create Function App
az functionapp create \
  --resource-group your-resource-group \
  --name agrohelpdesk-functions \
  --storage-account yourstorage \
  --functions-version 4 \
  --runtime python \
  --runtime-version 3.10 \
  --os-type Linux \
  --consumption-plan-location brazilsouth

# Configure app settings
az functionapp config appsettings set \
  --name agrohelpdesk-functions \
  --resource-group your-resource-group \
  --settings \
    COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/ \
    COSMOS_KEY=your_key \
    COSMOS_DATABASE_NAME=agrohelpdesk \
    COSMOS_CONTAINER_NAME=workorders

# Deploy
func azure functionapp publish agrohelpdesk-functions
```

### CI/CD with GitHub Actions

```yaml
name: Deploy Functions

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: |
          cd functions/function-workorders
          pip install -r requirements.txt
      - uses: Azure/functions-action@v1
        with:
          app-name: agrohelpdesk-functions
          package: functions/function-workorders
```

## 🔒 Security

### Authentication

Functions use `AuthLevel.FUNCTION` (except health check):

**Local**: No authentication required  
**Production**: Require function key

Get function key:
```powershell
az functionapp keys list \
  --name agrohelpdesk-functions \
  --resource-group your-resource-group
```

Use in requests:
```http
GET /api/workorders
x-functions-key: your_function_key
```

Or in query string:
```
GET /api/workorders?code=your_function_key
```

### Managed Identity (Production)

Enable for Cosmos DB access:

```powershell
# Enable Managed Identity
az functionapp identity assign \
  --name agrohelpdesk-functions \
  --resource-group your-resource-group

# Grant Cosmos DB permissions
az cosmosdb sql role assignment create \
  --account-name your-cosmos-account \
  --resource-group your-resource-group \
  --role-definition-name "Cosmos DB Built-in Data Contributor" \
  --principal-id <managed-identity-principal-id> \
  --scope "/"

# Set environment variable
az functionapp config appsettings set \
  --name agrohelpdesk-functions \
  --resource-group your-resource-group \
  --settings USE_MANAGED_IDENTITY=true
```

## 📊 Monitoring

### Application Insights

Configure connection string:

```json
{
  "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=...;IngestionEndpoint=..."
}
```

View logs:
```powershell
# Real-time logs
func azure functionapp logstream agrohelpdesk-functions

# In Azure Portal
# Function App > Monitor > Logs
```

### Metrics to Monitor

- Execution time
- Success/failure rate
- Request throughput
- Cosmos DB latency
- Error rates by endpoint

## 🐛 Troubleshooting

### Common Issues

**1. Cosmos DB connection failed**
- Verify `COSMOS_ENDPOINT` and `COSMOS_KEY`
- Check database and container exist
- Review firewall rules

**2. Validation errors**
- Check required fields: `title`, `description`, `category`, `assigned_specialist`
- Verify enum values for `category`, `priority`, `status`

**3. Performance issues**
- Review Cosmos DB indexes
- Consider increasing RU/s
- Enable query caching

**4. Function not starting**
- Check Python version (3.10+)
- Verify `host.json` configuration
- Review Application Insights logs

## 📚 Dependencies

```
azure-functions==1.18.0
azure-cosmos==4.5.1
azure-identity==1.15.0
pydantic==2.5.0
pydantic-settings==2.1.0
```

## 🔧 Configuration Reference

### host.json

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

## 📖 Best Practices

1. **Use Pydantic** for all data validation
2. **Enable Application Insights** for monitoring
3. **Use Managed Identity** in production
4. **Implement retry logic** for Cosmos DB operations
5. **Log all errors** with context
6. **Version your APIs** for backward compatibility
7. **Use environment variables** for all configuration
8. **Implement health checks** for monitoring

## 📚 Further Reading

- [Azure Functions Python Developer Guide](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Cosmos DB Python SDK](https://docs.microsoft.com/azure/cosmos-db/sql/sql-api-sdk-python)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Azure Functions Best Practices](https://docs.microsoft.com/azure/azure-functions/functions-best-practices)

---

**Built with ⚡ for serverless scalability**
