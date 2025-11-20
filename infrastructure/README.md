# Infraestrutura Azure - Agro Auto-Resolve

Este diretório contém a configuração de infraestrutura como código (IaC) usando Terraform para provisionar todos os recursos Azure necessários.

## 📋 Recursos Provisionados

- **Resource Group**: Grupo de recursos para organização
- **Storage Account**: Armazenamento de blobs para dataset e arquivos
- **Azure Functions**: API serverless
- **Cosmos DB**: Banco de dados NoSQL (serverless)
  - Container: `tickets`
  - Container: `agents`
  - Container: `metrics`
  - Container: `chat-history`
- **Azure Cognitive Search**: Busca semântica no conhecimento
- **Application Insights**: Monitoramento e telemetria

## 🚀 Pré-requisitos

1. **Azure CLI** instalado e configurado
   ```bash
   az login
   az account set --subscription "YOUR_SUBSCRIPTION_ID"
   ```

2. **Terraform** instalado (>= 1.0)
   ```bash
   terraform --version
   ```

3. **Azure OpenAI** (opcional, mas recomendado)
   - Solicite acesso ao Azure OpenAI
   - Crie um deployment do modelo GPT-4 ou GPT-3.5-turbo

## 📦 Deployment

### 1. Inicializar Terraform

```bash
cd infrastructure/terraform
terraform init
```

### 2. Configurar Variáveis

Crie um arquivo `terraform.tfvars`:

```hcl
project_name = "agroautoresolve"
environment  = "dev"
location     = "brazilsouth"

# Azure OpenAI (se disponível)
azure_openai_endpoint        = "https://YOUR-OPENAI.openai.azure.com/"
azure_openai_key            = "YOUR_OPENAI_KEY"
azure_openai_deployment_name = "gpt-4"

# CORS para frontend
cors_allowed_origins = [
  "http://localhost:5173",
  "https://your-frontend-url.com"
]
```

### 3. Planejar Deployment

```bash
terraform plan
```

### 4. Aplicar Configuração

```bash
terraform apply
```

Digite `yes` quando solicitado.

### 5. Obter Outputs

```bash
terraform output
```

Salve os outputs (connection strings, endpoints) em um local seguro.

## 🔧 Configuração Pós-Deployment

### 1. Configurar Local Settings

Copie os outputs do Terraform para `backend/local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "STORAGE_CONNECTION_STRING",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "COSMOS_DB_ENDPOINT": "COSMOS_ENDPOINT",
    "COSMOS_DB_KEY": "COSMOS_KEY",
    "COSMOS_DB_DATABASE": "agro-autoresolve",
    "SEARCH_SERVICE_ENDPOINT": "SEARCH_ENDPOINT",
    "SEARCH_SERVICE_KEY": "SEARCH_KEY",
    "SEARCH_INDEX_NAME": "knowledge-base",
    "AZURE_OPENAI_ENDPOINT": "OPENAI_ENDPOINT",
    "AZURE_OPENAI_KEY": "OPENAI_KEY",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4"
  }
}
```

### 2. Upload do Dataset

```bash
# Upload dos arquivos CSV e PDF para o blob storage
az storage blob upload-batch \
  --account-name STORAGE_ACCOUNT_NAME \
  --destination dataset \
  --source ../dataset
```

### 3. Indexar Dados

Execute o script de indexação (será criado posteriormente):

```bash
cd ../backend
python data_processing/indexer.py
```

## 💰 Custos Estimados (Desenvolvimento)

| Serviço | SKU | Custo Mensal (USD) |
|---------|-----|-------------------|
| Function App | B1 (Basic) | ~$13 |
| Cosmos DB | Serverless | ~$25 (mínimo) |
| Azure Search | Basic | ~$75 |
| Storage Account | Standard LRS | ~$2 |
| Application Insights | Pay-as-you-go | ~$5 |
| Azure OpenAI | Pay-per-use | ~$10-50 |
| **Total** | | **~$130-170** |

> **Nota**: Para produção, considere SKUs superiores e redundância geográfica.

## 🧹 Destruir Recursos

Para remover todos os recursos:

```bash
terraform destroy
```

⚠️ **ATENÇÃO**: Isso removerá TODOS os dados permanentemente!

## 📚 Referências

- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Functions](https://docs.microsoft.com/azure/azure-functions/)
- [Cosmos DB](https://docs.microsoft.com/azure/cosmos-db/)
- [Azure Cognitive Search](https://docs.microsoft.com/azure/search/)
- [Azure OpenAI](https://docs.microsoft.com/azure/cognitive-services/openai/)
