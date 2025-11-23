# Agro Auto-Resolve - Deployment Guide

Complete automated deployment solution for the Agro Auto-Resolve agricultural service desk application.

## 🎯 Overview

This deployment automation creates and configures all Azure resources, uploads data, and deploys both backend and frontend applications using PowerShell scripts.

## 📋 Prerequisites

Before running the deployment, ensure you have:

- **Azure CLI** (latest version) - [Install](https://aka.ms/InstallAzureCLI)
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** and npm - [Download](https://nodejs.org/)
- **Azure Functions Core Tools** - `npm install -g azure-functions-core-tools@4`
- **Azure Static Web Apps CLI** - `npm install -g @azure/static-web-apps-cli`
- **Active Azure subscription** with appropriate permissions

## 🚀 Quick Start

### Complete Deployment (Recommended)

Run the master deployment script to set up everything:

```powershell
# Login to Azure
az login

# Run complete deployment
.\deploy.ps1
```

This single command will:
1. ✅ Validate prerequisites
2. ✅ Create all Azure resources
3. ✅ Configure permissions and authentication
4. ✅ Upload datasets to blob storage
5. ✅ Create and populate AI Search index
6. ✅ Deploy backend Azure Functions
7. ✅ Deploy frontend Static Web App

**Estimated time:** 15-20 minutes

### Partial Deployment

Skip specific steps if already completed:

```powershell
# Skip resource creation (if already exists)
.\deploy.ps1 -SkipResourceCreation

# Skip data upload
.\deploy.ps1 -SkipDataUpload

# Skip indexing
.\deploy.ps1 -SkipIndexing

# Skip backend deployment
.\deploy.ps1 -SkipBackendDeploy

# Skip frontend deployment
.\deploy.ps1 -SkipFrontendDeploy

# Combine multiple skips
.\deploy.ps1 -SkipPrerequisites -SkipResourceCreation -SkipDataUpload
```

## 📁 Project Structure

```
HackathonMicrosoftNov2025/
├── deploy.ps1                      # Master deployment script
├── cleanup.ps1                     # Resource cleanup script
├── infrastructure/
│   ├── config.json                 # Azure resource configuration
│   ├── deploy_resources.ps1        # Azure resources provisioning
│   ├── upload_dataset.ps1          # Dataset upload to blob storage
│   ├── create_search_index.py      # AI Search index creation
│   ├── index_documents.py          # Document indexing
│   ├── setup_search_service.ps1    # Search service permissions
│   ├── setup_storage_permissions.ps1 # Storage permissions
│   └── requirements.txt            # Python dependencies
├── backend/
│   ├── function_app.py            # Azure Functions
│   ├── requirements.txt           # Backend dependencies
│   └── ...
├── web-frontend/
│   ├── src/                       # React application
│   ├── package.json               # Frontend dependencies
│   └── ...
└── dataset/
    ├── *.pdf                      # PDF documents
    └── *.csv                      # CSV data files
```

## 🔧 Individual Scripts

### 1. Infrastructure Deployment

Create all Azure resources:

```powershell
cd infrastructure
.\deploy_resources.ps1
```

**Creates:**
- Resource Group
- Storage Account
- Cosmos DB (Serverless)
- Azure OpenAI Service (with GPT-4o deployment)
- Azure AI Search (Basic tier)
- Document Intelligence Service
- Azure Functions (Consumption plan)
- Static Web App (Free tier)

### 2. Configure Permissions

Set up RBAC permissions for storage and search:

```powershell
# Storage permissions
.\infrastructure\setup_storage_permissions.ps1

# Search service permissions
.\infrastructure\setup_search_service.ps1
```

### 3. Upload Dataset

Upload documents and CSV files to blob storage:

```powershell
.\infrastructure\upload_dataset.ps1
```

Files are organized as:
- PDFs → `documents/` folder
- CSVs → `data/` folder

### 4. Create Search Index

Create and populate the AI Search index:

```powershell
cd infrastructure

# Activate virtual environment
..\.venv\Scripts\Activate.ps1

# Create index
python create_search_index.py

# Index documents
python index_documents.py
```

### 5. Deploy Backend

Deploy Azure Functions backend:

```powershell
cd backend
func azure functionapp publish <function-app-name> --python
```

### 6. Deploy Frontend

Build and deploy the React frontend:

```powershell
cd web-frontend

# Install dependencies
npm install

# Build
npm run build

# Deploy to Static Web App
swa deploy ./dist --deployment-token <token>
```

## 🌐 Configuration

Edit `infrastructure/config.json` to customize resource names and locations:

```json
{
  "location": "eastus2",
  "resourceGroupName": "rg-agro-autoresolve-dev",
  "storageAccountName": "stagroautoresolve001",
  "cosmosDbAccountName": "cosmos-agro-autoresolve",
  "cosmosDbDatabaseName": "AgroServiceDesk",
  "openAiServiceName": "oai-agro-autoresolve",
  "aiSearchServiceName": "search-agro-autoresolve",
  "searchIndexName": "agro-knowledge-base",
  "documentIntelligenceServiceName": "di-agro-autoresolve",
  "staticWebAppName": "swa-agro-autoresolve",
  "functionAppName": "func-agro-autoresolve"
}
```

## 🧪 Testing

### Test Backend API

```powershell
# Health check
Invoke-RestMethod "https://<function-app-name>.azurewebsites.net/api/health"

# Test chat endpoint
$body = @{
    message = "Como controlar pragas?"
    userId = "test-user"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
    -Uri "https://<function-app-name>.azurewebsites.net/api/chat" `
    -Body $body `
    -ContentType "application/json"
```

### Test Frontend

Open browser to: `https://<static-web-app-url>.azurestaticapps.net`

## 🔍 Monitoring

### View Logs

```powershell
# Function App logs
func azure functionapp logstream <function-app-name>

# Activity logs
az monitor activity-log list `
    --resource-group rg-agro-autoresolve-dev `
    --output table

# Application Insights
az monitor app-insights component show `
    --app <function-app-name> `
    --resource-group rg-agro-autoresolve-dev
```

### Resource Status

```powershell
# List all resources
az resource list `
    --resource-group rg-agro-autoresolve-dev `
    --output table

# Check specific resource
az <service> show `
    --name <resource-name> `
    --resource-group rg-agro-autoresolve-dev
```

## 🧹 Cleanup

### Delete All Resources

```powershell
# Delete entire resource group
.\cleanup.ps1

# Delete without confirmation
.\cleanup.ps1 -Force

# Delete resources but keep resource group
.\cleanup.ps1 -KeepResourceGroup
```

**Warning:** This permanently deletes all data and resources!

## 🐛 Troubleshooting

### Common Issues

**1. Azure CLI Not Logged In**
```powershell
az login
az account show
```

**2. Insufficient Permissions**
- Ensure your account has Contributor or Owner role on the subscription
- Check RBAC assignments: `az role assignment list --assignee <email>`

**3. Resource Name Conflicts**
- Storage account names must be globally unique
- Update `config.json` with unique names

**4. Python Virtual Environment Issues**
```powershell
# Recreate virtual environment
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r infrastructure/requirements.txt
pip install -r backend/requirements.txt
```

**5. Node.js/npm Issues**
```powershell
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
cd web-frontend
Remove-Item -Recurse -Force node_modules
npm install
```

**6. Function App Not Starting**
- Check Python version compatibility (3.10 required)
- Verify all dependencies in `requirements.txt`
- Check application settings in Azure Portal

**7. CSV Parsing Errors**
- CSVs use semicolon (`;`) delimiter
- Ensure proper encoding (UTF-8 or Latin-1)
- Check for embedded semicolons in text fields

### Get Help

```powershell
# View detailed help for deployment script
Get-Help .\deploy.ps1 -Full

# View deployment logs
Get-Content .\deployment.log
```

## 📚 Additional Resources

- [Azure Functions Python Developer Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Static Web Apps Documentation](https://learn.microsoft.com/azure/static-web-apps/)
- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)
- [Azure Cosmos DB Documentation](https://learn.microsoft.com/azure/cosmos-db/)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/ai-services/openai/)

## 🎯 Next Steps

After successful deployment:

1. ✅ Configure custom domain for Static Web App
2. ✅ Set up Application Insights for monitoring
3. ✅ Configure Azure AD authentication
4. ✅ Set up CI/CD with GitHub Actions
5. ✅ Configure backup and disaster recovery
6. ✅ Implement cost monitoring and alerts
7. ✅ Review and optimize resource SKUs for production

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Azure Portal diagnostics
3. Check application logs
4. Contact the development team

---

**Last Updated:** November 2025
**Version:** 1.0.0
