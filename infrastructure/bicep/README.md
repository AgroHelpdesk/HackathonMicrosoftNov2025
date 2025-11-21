# Bicep Infrastructure Deployment

Este diretório contém os arquivos Bicep para provisionar a infraestrutura Azure do projeto Agro Auto-Resolve.

## 📋 Recursos Provisionados

- **Resource Group**: Grupo de recursos para organização
- **Storage Account**: Armazenamento de blobs para dataset e arquivos
- **Azure Functions**: API serverless (Python 3.11)
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

2. **Bicep CLI** (incluído no Azure CLI >= 2.20.0)
   ```bash
   az bicep version
   # Se necessário, atualize:
   az bicep upgrade
   ```

3. **Azure OpenAI** (opcional, mas recomendado)
   - Solicite acesso ao Azure OpenAI
   - Crie um deployment do modelo GPT-4 ou GPT-3.5-turbo

## 📦 Deployment

### 1. Criar Resource Group

```bash
az group create \
  --name rg-agroautoresolve-dev \
  --location brazilsouth
```

### 2. Validar Template Bicep

```bash
az deployment group validate \
  --resource-group rg-agroautoresolve-dev \
  --template-file main.bicep \
  --parameters parameters.dev.json
```

### 3. Preview de Mudanças (What-If)

```bash
az deployment group what-if \
  --resource-group rg-agroautoresolve-dev \
  --template-file main.bicep \
  --parameters parameters.dev.json
```

### 4. Deploy da Infraestrutura

```bash
az deployment group create \
  --resource-group rg-agroautoresolve-dev \
  --template-file main.bicep \
  --parameters parameters.dev.json \
  --name agro-deployment-$(date +%Y%m%d-%H%M%S)
```

### 5. Deploy com Parâmetros Customizados

Se você tiver Azure OpenAI configurado:

```bash
az deployment group create \
  --resource-group rg-agroautoresolve-dev \
  --template-file main.bicep \
  --parameters parameters.dev.json \
  --parameters azureOpenAiEndpoint="https://YOUR-OPENAI.openai.azure.com/" \
  --parameters azureOpenAiKey="YOUR_KEY"
```

### 6. Obter Outputs

```bash
az deployment group show \
  --resource-group rg-agroautoresolve-dev \
  --name agro-deployment-YYYYMMDD-HHMMSS \
  --query properties.outputs
```

## 🔧 Configuração Pós-Deployment

### 1. Salvar Connection Strings

Salve os outputs do deployment em um local seguro. Você precisará deles para configurar o backend.

### 2. Upload do Dataset

```bash
# Upload dos arquivos CSV e PDF para o blob storage
az storage blob upload-batch \
  --account-name stagroautoresolvedev \
  --destination dataset \
  --source ../../dataset \
  --auth-mode login
```

### 3. Configurar Backend

Copie os outputs para `backend/local.settings.json`:

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

## 🔄 Atualizar Infraestrutura

Para atualizar recursos existentes, simplesmente execute o deploy novamente:

```bash
az deployment group create \
  --resource-group rg-agroautoresolve-dev \
  --template-file main.bicep \
  --parameters parameters.dev.json
```

Bicep é **idempotente** - ele só criará/atualizará recursos que mudaram.

## 📊 Ambientes

### Development (dev)
- SKU econômico (B1 para Functions, Basic para Search)
- Ideal para desenvolvimento e testes
- Custo estimado: ~$115/mês

```bash
az deployment group create \
  --resource-group rg-agroautoresolve-dev \
  --template-file main.bicep \
  --parameters parameters.dev.json
```

### Production (prod)
- SKU de produção (P1v2 para Functions, Standard para Search)
- Alta disponibilidade e performance
- Custo estimado: ~$250-300/mês

```bash
az deployment group create \
  --resource-group rg-agroautoresolve-prod \
  --template-file main.bicep \
  --parameters parameters.prod.json
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
az group delete \
  --name rg-agroautoresolve-dev \
  --yes --no-wait
```

⚠️ **ATENÇÃO**: Isso removerá TODOS os dados permanentemente!

## 🛠️ Comandos Úteis

### Listar Deployments

```bash
az deployment group list \
  --resource-group rg-agroautoresolve-dev \
  --output table
```

### Ver Logs de Deployment

```bash
az deployment operation group list \
  --resource-group rg-agroautoresolve-dev \
  --name agro-deployment-YYYYMMDD-HHMMSS
```

### Exportar Template ARM

```bash
az bicep build --file main.bicep
```

### Decompile ARM para Bicep

```bash
az bicep decompile --file template.json
```

## 📚 Referências

- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Azure Functions](https://docs.microsoft.com/azure/azure-functions/)
- [Cosmos DB](https://docs.microsoft.com/azure/cosmos-db/)
- [Azure Cognitive Search](https://docs.microsoft.com/azure/search/)
- [Azure OpenAI](https://docs.microsoft.com/azure/cognitive-services/openai/)

## 🆚 Bicep vs Terraform

### Vantagens do Bicep

✅ **Nativo do Azure** - Suporte de primeira classe da Microsoft  
✅ **Sem State File** - Azure gerencia o estado automaticamente  
✅ **IntelliSense** - Melhor experiência no VS Code  
✅ **Sintaxe Simples** - Mais legível que HCL  
✅ **Day-0 Support** - Novos recursos Azure disponíveis imediatamente  
✅ **Decompilação** - Converte ARM templates existentes  

### Quando usar Terraform

- Infraestrutura multi-cloud (AWS + Azure + GCP)
- Time já experiente com Terraform
- Necessidade de providers da comunidade
