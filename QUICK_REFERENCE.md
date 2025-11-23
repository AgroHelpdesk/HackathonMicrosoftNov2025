# Quick Deployment Reference

## 🚀 One-Command Deployment

```powershell
az login
.\deploy.ps1
```

## 📝 Deployment Steps (Manual)

### 1. Prerequisites
```powershell
# Check prerequisites
az --version
python --version
node --version
npm --version
az account show
```

### 2. Deploy Infrastructure
```powershell
.\infrastructure\deploy_resources.ps1
```

### 3. Configure Permissions
```powershell
# Get user object ID
$UserObjectId = az ad signed-in-user show --query id --output tsv
$SubscriptionId = (az account show | ConvertFrom-Json).id

# Storage
az role assignment create `
    --role "Storage Blob Data Contributor" `
    --assignee $UserObjectId `
    --scope "/subscriptions/$SubscriptionId/resourceGroups/rg-agro-autoresolve-dev/providers/Microsoft.Storage/storageAccounts/stagroautoresolve001"

# Search Service
az search service update `
    --name search-agro-autoresolve `
    --resource-group rg-agro-autoresolve-dev `
    --auth-options aadOrApiKey `
    --aad-auth-failure-mode http401WithBearerChallenge

az role assignment create `
    --role "Search Index Data Contributor" `
    --assignee $UserObjectId `
    --scope "/subscriptions/$SubscriptionId/resourceGroups/rg-agro-autoresolve-dev/providers/Microsoft.Search/searchServices/search-agro-autoresolve"

# Wait for propagation
Start-Sleep -Seconds 20
```

### 4. Setup Python Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r infrastructure\requirements.txt
pip install -r backend\requirements.txt
```

### 5. Upload Data
```powershell
.\infrastructure\upload_dataset.ps1
```

### 6. Create Search Index
```powershell
python infrastructure\create_search_index.py
python infrastructure\index_documents.py
```

### 7. Deploy Backend
```powershell
cd backend
func azure functionapp publish func-agro-autoresolve --python
```

### 8. Deploy Frontend
```powershell
cd web-frontend
npm install
npm run build
swa deploy ./dist --deployment-token <token>
```

## 🧹 Cleanup

```powershell
.\cleanup.ps1
```

## 📊 Verify Deployment

```powershell
# Check resources
az resource list --resource-group rg-agro-autoresolve-dev --output table

# Test backend
Invoke-RestMethod "https://func-agro-autoresolve.azurewebsites.net/api/health"

# Check search index
az search index show `
    --service-name search-agro-autoresolve `
    --name agro-knowledge-base `
    --resource-group rg-agro-autoresolve-dev
```

## 🔧 Common Commands

```powershell
# Login to Azure
az login

# Set subscription
az account set --subscription <subscription-id>

# List resource groups
az group list --output table

# Get connection strings
az cosmosdb keys list --name cosmos-agro-autoresolve --resource-group rg-agro-autoresolve-dev --type connection-strings

# Get search key
az search admin-key show --service-name search-agro-autoresolve --resource-group rg-agro-autoresolve-dev

# Get OpenAI key
az cognitiveservices account keys list --name oai-agro-autoresolve --resource-group rg-agro-autoresolve-dev

# View function app logs
func azure functionapp logstream func-agro-autoresolve

# Get Static Web App URL
az staticwebapp show --name swa-agro-autoresolve --resource-group rg-agro-autoresolve-dev --query defaultHostname
```

## 🐛 Troubleshooting

```powershell
# Fix Python dependencies
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend\requirements.txt

# Fix Node dependencies
cd web-frontend
Remove-Item -Recurse -Force node_modules
npm install

# Reinstall Azure Functions Core Tools
npm uninstall -g azure-functions-core-tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Check Azure CLI version
az upgrade

# Reset role assignments (wait 30s after)
az role assignment delete --assignee <object-id> --scope <resource-scope>
az role assignment create --role "..." --assignee <object-id> --scope <resource-scope>
```

## ⏱️ Deployment Timeline

| Step | Duration | Skippable |
|------|----------|-----------|
| Prerequisites Check | 30s | Yes |
| Infrastructure Creation | 8-10 min | Yes |
| Permission Configuration | 1 min | No |
| Python Environment Setup | 2 min | No |
| Data Upload | 1 min | Yes |
| Search Index Creation | 1 min | Yes |
| Backend Deployment | 3-5 min | Yes |
| Frontend Deployment | 2-3 min | Yes |
| **Total** | **15-20 min** | - |

## 🎯 Resource Costs (Estimated Monthly)

| Resource | SKU | Est. Cost |
|----------|-----|-----------|
| Storage Account | Standard LRS | $1-5 |
| Cosmos DB | Serverless | $1-10 |
| Azure OpenAI | Standard | $10-50 |
| AI Search | Basic | $75 |
| Function App | Consumption | $0-5 |
| Static Web App | Free | $0 |
| **Total** | | **~$87-145** |

*Costs vary based on usage. Use Azure Cost Management for accurate tracking.*
