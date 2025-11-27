# AgroHelpDesk - Azure Functions

Sistema de gerenciamento de ordens de serviço (OS) para o AgroHelpDesk, implementado como Azure Functions com persistência em Cosmos DB.

## 📋 Visão Geral

Este pacote de Azure Functions fornece endpoints HTTP para criar, consultar e gerenciar ordens de serviço agrícolas, integrando-se perfeitamente com o backend e frontend do AgroHelpDesk.

### Características

- ✅ **Azure Functions v2** - Modelo de programação Python mais recente
- ✅ **Cosmos DB** - Persistência NoSQL escalável
- ✅ **Validação Pydantic** - Type safety e validação de dados
- ✅ **Logging Estruturado** - Integração com Application Insights
- ✅ **Tratamento de Erros** - Respostas consistentes e informativas
- ✅ **Autenticação** - Function-level authentication
- ✅ **Health Checks** - Endpoint de monitoramento

## 🏗️ Arquitetura

```
functions/
├── function_app.py          # Definição de todas as functions (v2 model)
├── host.json                # Configuração do Functions Host
├── requirements.txt         # Dependências Python
├── local.settings.json      # Configurações locais (não versionar)
├── models/                  # Modelos de dados Pydantic
│   ├── __init__.py
│   └── work_order.py       # Schemas de WorkOrder
├── services/                # Camada de serviços
│   ├── __init__.py
│   └── cosmos_service.py   # Operações Cosmos DB
└── utils/                   # Utilitários
    ├── __init__.py
    ├── logger.py           # Configuração de logs
    ├── validators.py       # Validadores personalizados
    └── response_builder.py # Builders de resposta HTTP
```

## 🚀 Configuração Local

### Pré-requisitos

- Python 3.10 ou superior
- [Azure Functions Core Tools v4](https://docs.microsoft.com/azure/azure-functions/functions-run-local)
- Conta Azure com Cosmos DB configurado

### 1. Instalar Dependências

```powershell
cd functions
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Edite `local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "COSMOS_ENDPOINT": "https://seu-cosmos-account.documents.azure.com:443/",
    "COSMOS_KEY": "sua-chave-cosmos-db",
    "COSMOS_DATABASE_NAME": "agrohelpdesk",
    "COSMOS_CONTAINER_NAME": "workorders",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=...",
    "LOG_LEVEL": "INFO",
    "ENABLE_DETAILED_LOGGING": "true"
  }
}
```

### 3. Criar Recursos no Cosmos DB

Execute os seguintes comandos no Azure Portal ou CLI:

```powershell
# Criar banco de dados
az cosmosdb sql database create \
  --account-name seu-cosmos-account \
  --name agrohelpdesk

# Criar container
az cosmosdb sql container create \
  --account-name seu-cosmos-account \
  --database-name agrohelpdesk \
  --name workorders \
  --partition-key-path "/partition_key" \
  --throughput 400
```

### 4. Executar Localmente

```powershell
func start
```

A função estará disponível em: `http://localhost:7071`

## 📡 Endpoints da API

### 1. Criar Ordem de Serviço

**POST** `/api/workorders`

**Headers:**
```
Content-Type: application/json
x-functions-key: <sua-function-key>
```

**Body:**
```json
{
  "title": "Falha no sistema de irrigação",
  "description": "Gotejamento irregular detectado no talhão A3. Necessária inspeção urgente.",
  "category": "irrigacao",
  "priority": "alta",
  "assigned_specialist": "Técnico de Irrigação",
  "machine_id": "IRRIG-001",
  "field_id": "A3",
  "estimated_time_hours": 4.0,
  "symptoms": "Vazão irregular, baixa pressão no setor norte",
  "requester_id": "user123",
  "requester_contact": "joao@fazenda.com"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "order_id": "OS-A1B2C3D4",
    "title": "Falha no sistema de irrigação",
    "description": "Gotejamento irregular detectado no talhão A3. Necessária inspeção urgente.",
    "category": "irrigacao",
    "priority": "alta",
    "status": "pending",
    "assigned_specialist": "Técnico de Irrigação",
    "machine_id": "IRRIG-001",
    "field_id": "A3",
    "estimated_time_hours": 4.0,
    "symptoms": "Vazão irregular, baixa pressão no setor norte",
    "created_at": "2025-11-26T10:30:00Z",
    "updated_at": "2025-11-26T10:30:00Z",
    "notes": [],
    "attachments": []
  },
  "message": "Work order OS-A1B2C3D4 created successfully",
  "timestamp": "2025-11-26T10:30:00Z"
}
```

### 2. Consultar Ordem de Serviço

**GET** `/api/workorders/{order_id}`

**Example:** `GET /api/workorders/OS-A1B2C3D4`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "order_id": "OS-A1B2C3D4",
    ...
  },
  "timestamp": "2025-11-26T10:30:00Z"
}
```

### 3. Atualizar Status da OS

**PATCH** `/api/workorders/{order_id}/status`

**Body:**
```json
{
  "status": "in_progress",
  "note": "Técnico João iniciou a inspeção do sistema"
}
```

**Status válidos:**
- `pending` - Aguardando atribuição
- `assigned` - Atribuída a técnico
- `in_progress` - Em andamento
- `completed` - Concluída
- `cancelled` - Cancelada
- `on_hold` - Em espera

**Response (200):**
```json
{
  "success": true,
  "data": {
    "order_id": "OS-A1B2C3D4",
    "status": "in_progress",
    ...
  },
  "message": "Work order OS-A1B2C3D4 status updated to in_progress",
  "timestamp": "2025-11-26T10:30:00Z"
}
```

### 4. Listar Ordens de Serviço

**GET** `/api/workorders?status=pending&category=irrigacao&priority=alta&limit=50`

**Query Parameters:**
- `status` (opcional) - Filtrar por status
- `category` (opcional) - Filtrar por categoria
- `priority` (opcional) - Filtrar por prioridade
- `limit` (opcional) - Máximo de resultados (padrão: 100, máx: 1000)

**Response (200):**
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
  },
  "timestamp": "2025-11-26T10:30:00Z"
}
```

### 5. Health Check

**GET** `/api/health`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "agrohelpdesk-functions",
    "version": "1.0.0",
    "cosmos_db": "connected"
  },
  "timestamp": "2025-11-26T10:30:00Z"
}
```

## 🔧 Modelos de Dados

### WorkOrderCategory
```python
class WorkOrderCategory(str, Enum):
    MAQUINARIO = "maquinario"
    IRRIGACAO = "irrigacao"
    PLANTIO = "plantio"
    COLHEITA = "colheita"
    INSUMOS = "insumos"
    SOLO = "solo"
    PRAGA = "praga"
    OUTRO = "outro"
```

### WorkOrderPriority
```python
class WorkOrderPriority(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"
```

### WorkOrderStatus
```python
class WorkOrderStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
```

## 🧪 Testando Localmente

### Usar curl

```powershell
# Criar OS
curl -X POST http://localhost:7071/api/workorders `
  -H "Content-Type: application/json" `
  -d '{
    "title": "Teste de irrigação",
    "description": "Teste de criação de OS",
    "category": "irrigacao",
    "priority": "media",
    "assigned_specialist": "Técnico Teste"
  }'

# Consultar OS
curl http://localhost:7071/api/workorders/OS-XXXXXXXX

# Listar OSs
curl "http://localhost:7071/api/workorders?status=pending&limit=10"
```

### Usar Postman ou Insomnia

Importe a collection de exemplos ou configure manualmente:
- Base URL: `http://localhost:7071/api`
- Headers: `Content-Type: application/json`

## 🚢 Deploy no Azure

### Opção 1: Azure Functions Core Tools

```powershell
# Login no Azure
az login

# Criar Function App (Flex Consumption - recomendado)
az functionapp create `
  --resource-group seu-resource-group `
  --name agrohelpdesk-functions `
  --storage-account seustorage `
  --functions-version 4 `
  --runtime python `
  --runtime-version 3.10 `
  --os-type Linux `
  --consumption-plan-location brazilsouth

# Configurar variáveis de ambiente
az functionapp config appsettings set `
  --name agrohelpdesk-functions `
  --resource-group seu-resource-group `
  --settings `
    COSMOS_ENDPOINT=https://seu-cosmos.documents.azure.com:443/ `
    COSMOS_KEY=sua-chave `
    COSMOS_DATABASE_NAME=agrohelpdesk `
    COSMOS_CONTAINER_NAME=workorders

# Deploy
func azure functionapp publish agrohelpdesk-functions
```

### Opção 2: VS Code Azure Functions Extension

1. Instale a extensão "Azure Functions" no VS Code
2. Clique em "Deploy to Function App" no painel do Azure
3. Selecione ou crie uma Function App
4. Configure as variáveis de ambiente no portal Azure

### Opção 3: Azure DevOps / GitHub Actions

Configure CI/CD pipeline usando os templates fornecidos pela Microsoft.

## 🔒 Segurança

### Autenticação

As functions usam `AuthLevel.FUNCTION` por padrão, exceto o health check:

- Obtenha a function key no Azure Portal: Function App > Functions > App keys
- Inclua no header: `x-functions-key: <sua-key>` ou query string: `?code=<sua-key>`

### Managed Identity (Recomendado para Produção)

Configure Managed Identity para acesso ao Cosmos DB:

```powershell
# Habilitar Managed Identity
az functionapp identity assign `
  --name agrohelpdesk-functions `
  --resource-group seu-resource-group

# Conceder permissões no Cosmos DB
az cosmosdb sql role assignment create `
  --account-name seu-cosmos-account `
  --resource-group seu-resource-group `
  --role-definition-name "Cosmos DB Built-in Data Contributor" `
  --principal-id <managed-identity-principal-id> `
  --scope "/"

# Configurar variável de ambiente
az functionapp config appsettings set `
  --name agrohelpdesk-functions `
  --resource-group seu-resource-group `
  --settings USE_MANAGED_IDENTITY=true
```

## 📊 Monitoramento

### Application Insights

Configure o connection string no `local.settings.json` e nas configurações da Function App:

```json
{
  "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=...;IngestionEndpoint=..."
}
```

### Logs

```powershell
# Ver logs em tempo real
func azure functionapp logstream agrohelpdesk-functions

# No Azure Portal
# Function App > Monitor > Logs
```

### Métricas

- Tempo de execução
- Taxa de sucesso/falha
- Throughput de requisições
- Latência do Cosmos DB

## 🐛 Troubleshooting

### Erro: "Cosmos DB connection failed"

- Verifique `COSMOS_ENDPOINT` e `COSMOS_KEY`
- Confirme que o database e container existem
- Verifique regras de firewall no Cosmos DB

### Erro: "Validation failed"

- Confira os campos obrigatórios: `title`, `description`, `category`, `assigned_specialist`
- Verifique valores válidos para `category`, `priority`, `status`

### Performance lenta

- Revise índices no Cosmos DB
- Considere aumentar RU/s (throughput)
- Habilite cache de resultados

## 📚 Referências

- [Azure Functions Python Developer Guide](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Cosmos DB Python SDK](https://docs.microsoft.com/azure/cosmos-db/sql/sql-api-sdk-python)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Azure Functions Best Practices](https://docs.microsoft.com/azure/azure-functions/functions-best-practices)

## 🤝 Contribuindo

1. Siga as melhores práticas de Azure Functions Python v2
2. Mantenha validação com Pydantic
3. Adicione testes unitários
4. Documente alterações no README
5. Use logging estruturado

## 📄 Licença

Este projeto faz parte do AgroHelpDesk Hackathon.

---

**Desenvolvido com ❤️ para o AgroHelpDesk**
