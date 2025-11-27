#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Complete Azure Deployment for Agro Auto-Resolve Application

.DESCRIPTION
    This master script orchestrates the complete deployment of the Agro Auto-Resolve application:
    1. Validates prerequisites (Azure CLI, Python, Node.js)
    2. Creates all Azure resources
    3. Configures authentication and permissions
    4. Uploads datasets to blob storage
    5. Creates and populates AI Search index
    6. Deploys backend Azure Functions
    7. Deploys frontend Static Web App
    8. Configures application settings

.PARAMETER SkipPrerequisites
    Skip prerequisite checks

.PARAMETER SkipResourceCreation
    Skip Azure resource creation (assumes resources already exist)

.PARAMETER SkipDataUpload
    Skip dataset upload to blob storage

.PARAMETER SkipIndexing
    Skip AI Search index creation and document indexing

.PARAMETER SkipBackendDeploy
    Skip backend Azure Functions deployment

.PARAMETER SkipFrontendDeploy
    Skip frontend Static Web App deployment

.EXAMPLE
    .\deploy.ps1
    
.EXAMPLE
    .\deploy.ps1 -SkipPrerequisites -SkipResourceCreation
#>

[CmdletBinding()]
param(
    [switch]$SkipPrerequisites,
    [switch]$SkipResourceCreation,
    [switch]$SkipDataUpload,
    [switch]$SkipIndexing,
    [switch]$SkipBackendDeploy,
    [switch]$SkipFrontendDeploy
)

$ErrorActionPreference = "Stop"
$OriginalLocation = Get-Location

# Refresh PATH environment variable to pick up recently installed tools
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# Script paths
$RootDir = $PSScriptRoot
$InfraDir = Join-Path $RootDir "infrastructure"
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "web-frontend"
$DatasetDir = Join-Path $RootDir "dataset"
$ConfigPath = Join-Path $InfraDir "config.json"
$VenvPath = Join-Path $RootDir ".venv"
$VenvActivate = Join-Path $VenvPath "Scripts\Activate.ps1"

# Activate Python virtual environment if it exists
if (Test-Path $VenvActivate) {
    & $VenvActivate
}

# Color functions
function Write-Section {
    param([string]$Message)
    $line = '=' * 80
    Write-Host "`n$line" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "$line" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message)
    Write-Host "`n>> $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "  $Message" -ForegroundColor Gray
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Cleanup function
function Invoke-Cleanup {
    Set-Location $OriginalLocation
}

# Register cleanup on exit
trap {
    Invoke-Cleanup
    break
}

# ============================================================================
# STEP 1: Prerequisites Check
# ============================================================================
if (-not $SkipPrerequisites) {
    Write-Section "STEP 1: Checking Prerequisites"
    
    # Check Azure CLI
    Write-Step "Checking Azure CLI..."
    try {
        $azVersion = az version --output json 2>$null | ConvertFrom-Json
        Write-Success "Azure CLI version $($azVersion.'azure-cli')"
    }
    catch {
        Write-ErrorMsg "Azure CLI is not installed"
        Write-Info "Install from: https://aka.ms/InstallAzureCLI"
        exit 1
    }
    
    # Check Python
    Write-Step "Checking Python..."
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "$pythonVersion"
    }
    catch {
        Write-ErrorMsg "Python is not installed"
        Write-Info "Install from: https://www.python.org/downloads/"
        exit 1
    }
    
    # Check Node.js
    Write-Step "Checking Node.js..."
    try {
        $nodeVersion = node --version
        Write-Success "Node.js $nodeVersion"
    }
    catch {
        Write-ErrorMsg "Node.js is not installed"
        Write-Info "Install from: https://nodejs.org/"
        exit 1
    }
    
    # Check npm
    Write-Step "Checking npm..."
    try {
        $npmVersion = npm --version
        Write-Success "npm $npmVersion"
    }
    catch {
        Write-ErrorMsg "npm is not installed"
        exit 1
    }
    
    # Check Azure Login
    Write-Step "Checking Azure authentication..."
    try {
        $account = az account show 2>$null | ConvertFrom-Json
        Write-Success "Logged in as: $($account.user.name)"
        Write-Info "Subscription: $($account.name) ($($account.id))"
        $SubscriptionId = $account.id
    }
    catch {
        Write-ErrorMsg "Not logged in to Azure"
        Write-Info "Please run: az login"
        exit 1
    }
    
    Write-Success "All prerequisites met"
}

# ============================================================================
# STEP 2: Create Azure Resources
# ============================================================================
if (-not $SkipResourceCreation) {
    Write-Section "STEP 2: Creating Azure Resources"
    
    Write-Step "Deploying infrastructure..."
    Set-Location $InfraDir
    
    try {
        & .\deploy_resources.ps1
        Write-Success "Infrastructure deployment completed"
    }
    catch {
        Write-ErrorMsg "Infrastructure deployment failed: $_"
        exit 1
    }
    
    Set-Location $RootDir
}

# Load configuration
Write-Step "Loading configuration..."
if (-not (Test-Path $ConfigPath)) {
    Write-ErrorMsg "Configuration file not found: $ConfigPath"
    Write-Info "Please ensure deploy_resources.ps1 has been run"
    exit 1
}

$config = Get-Content $ConfigPath | ConvertFrom-Json
Write-Success "Configuration loaded"
Write-Info "Resource Group: $($config.resourceGroupName)"
Write-Info "Location: $($config.location)"

# Get current user
$account = az account show 2>$null | ConvertFrom-Json
$SubscriptionId = $account.id
$UserObjectId = az ad signed-in-user show --query id --output tsv

# ============================================================================
# STEP 3: Configure Permissions
# ============================================================================
Write-Section "STEP 3: Configuring Permissions"

# Storage permissions
Write-Step "Assigning Storage Blob Data Contributor role..."
try {
    $storageScope = "/subscriptions/$SubscriptionId/resourceGroups/$($config.resourceGroupName)/providers/Microsoft.Storage/storageAccounts/$($config.storageAccountName)"
    
    az role assignment create `
        --role "Storage Blob Data Contributor" `
        --assignee $UserObjectId `
        --scope $storageScope `
        --output none 2>$null
    
    Write-Success "Storage permissions configured"
}
catch {
    Write-Info "Storage role may already be assigned (continuing)"
}

# Search service permissions
Write-Step "Configuring Azure AI Search permissions..."
try {
    $searchScope = "/subscriptions/$SubscriptionId/resourceGroups/$($config.resourceGroupName)/providers/Microsoft.Search/searchServices/$($config.aiSearchServiceName)"
    
    # Enable Azure AD authentication
    az search service update `
        --name $($config.aiSearchServiceName) `
        --resource-group $($config.resourceGroupName) `
        --auth-options aadOrApiKey `
        --aad-auth-failure-mode http401WithBearerChallenge `
        --output none 2>$null
    
    # Assign roles
    az role assignment create `
        --role "Search Index Data Contributor" `
        --assignee $UserObjectId `
        --scope $searchScope `
        --output none 2>$null
    
    az role assignment create `
        --role "Search Service Contributor" `
        --assignee $UserObjectId `
        --scope $searchScope `
        --output none 2>$null
    
    Write-Success "Search service permissions configured"
}
catch {
    Write-Info "Search roles may already be assigned (continuing)"
}

Write-Step "Waiting for role assignments to propagate..."
Start-Sleep -Seconds 20
Write-Success "Permissions ready"

# ============================================================================
# STEP 4: Setup Python Environment
# ============================================================================
Write-Section "STEP 4: Setting Up Python Environment"

Write-Step "Creating virtual environment..."
if (-not (Test-Path (Join-Path $RootDir ".venv"))) {
    python -m venv (Join-Path $RootDir ".venv")
    Write-Success "Virtual environment created"
}
else {
    Write-Info "Virtual environment already exists"
}

Write-Step "Activating virtual environment..."
$VenvActivate = Join-Path $RootDir ".venv\Scripts\Activate.ps1"
& $VenvActivate

Write-Step "Installing infrastructure dependencies..."
pip install -q -r (Join-Path $InfraDir "requirements.txt")
Write-Success "Infrastructure dependencies installed"

Write-Step "Installing backend dependencies..."
pip install -q -r (Join-Path $BackendDir "requirements.txt")
Write-Success "Backend dependencies installed"

# ============================================================================
# STEP 5: Upload Dataset
# ============================================================================
if (-not $SkipDataUpload) {
    Write-Section "STEP 5: Uploading Dataset"
    
    Write-Step "Uploading files to blob storage..."
    Set-Location $InfraDir
    
    try {
        & .\upload_dataset.ps1
        Write-Success "Dataset uploaded successfully"
    }
    catch {
        Write-ErrorMsg "Dataset upload failed: $_"
        Write-Info "Continuing with deployment..."
    }
    
    Set-Location $RootDir
}

# ============================================================================
# STEP 6: Create and Populate Search Index
# ============================================================================
if (-not $SkipIndexing) {
    Write-Section "STEP 6: Creating and Populating Search Index"
    
    Write-Step "Creating search index..."
    Set-Location $InfraDir
    
    try {
        python create_search_index.py
        Write-Success "Search index created"
    }
    catch {
        Write-ErrorMsg "Search index creation failed: $_"
    }
    
    Write-Step "Indexing documents..."
    try {
        python index_documents.py
        Write-Success "Documents indexed"
    }
    catch {
        Write-ErrorMsg "Document indexing failed: $_"
        Write-Info "You can run this manually later: python infrastructure/index_documents.py"
    }
    
    Set-Location $RootDir
}

# ============================================================================
# STEP 7: Deploy Backend (Azure Functions)
# ============================================================================
if (-not $SkipBackendDeploy) {
    Write-Section "STEP 7: Deploying Backend (Azure Functions)"
    
    Write-Step "Configuring function app settings..."
    
    # Get connection strings and keys
    $cosmosConnString = az cosmosdb keys list `
        --name $($config.cosmosDbAccountName) `
        --resource-group $($config.resourceGroupName) `
        --type connection-strings `
        --query "connectionStrings[0].connectionString" `
        --output tsv
    
    $searchKey = az search admin-key show `
        --service-name $($config.aiSearchServiceName) `
        --resource-group $($config.resourceGroupName) `
        --query primaryKey `
        --output tsv
    
    $openaiEndpoint = "https://$($config.openAiServiceName).openai.azure.com/"
    $openaiKey = az cognitiveservices account keys list `
        --name $($config.openAiServiceName) `
        --resource-group $($config.resourceGroupName) `
        --query key1 `
        --output tsv
    
    # Configure app settings
    Write-Step "Setting application configuration..."
    az functionapp config appsettings set `
        --name $($config.functionAppName) `
        --resource-group $($config.resourceGroupName) `
        --settings `
        "COSMOS_CONNECTION_STRING=$cosmosConnString" `
        "COSMOS_DATABASE_NAME=$($config.cosmosDbDatabaseName)" `
        "SEARCH_ENDPOINT=https://$($config.aiSearchServiceName).search.windows.net" `
        "SEARCH_KEY=$searchKey" `
        "SEARCH_INDEX_NAME=$($config.searchIndexName)" `
        "OPENAI_ENDPOINT=$openaiEndpoint" `
        "OPENAI_API_KEY=$openaiKey" `
        "OPENAI_DEPLOYMENT_NAME=gpt-4o" `
        --output none
    
    Write-Success "App settings configured"
    
    Write-Step "Deploying function app..."
    Set-Location $BackendDir
    
    try {
        func azure functionapp publish $($config.functionAppName) --python
        Write-Success "Backend deployed successfully"
        
        $functionUrl = "https://$($config.functionAppName).azurewebsites.net"
        Write-Info "Function App URL: $functionUrl"
    }
    catch {
        Write-ErrorMsg "Backend deployment failed: $_"
        Write-Info "You can deploy manually later with: func azure functionapp publish $($config.functionAppName)"
    }
    
    Set-Location $RootDir
}

# ============================================================================
# STEP 8: Install Frontend Dependencies
# ============================================================================
Write-Section "STEP 8: Installing Frontend Dependencies"

Write-Step "Installing frontend npm packages..."
Set-Location $FrontendDir

try {
    npm install
    Write-Success "Frontend dependencies installed"
}
catch {
    Write-ErrorMsg "Failed to install frontend dependencies: $_"
}

Set-Location $RootDir

# ============================================================================
# STEP 9: Deploy Frontend (Static Web App)
# ============================================================================
if (-not $SkipFrontendDeploy) {
    Write-Section "STEP 9: Deploying Frontend (Static Web App)"
    
    Write-Step "Getting Static Web App deployment token..."
    $swaToken = az staticwebapp secrets list `
        --name $($config.staticWebAppName) `
        --resource-group $($config.resourceGroupName) `
        --query "properties.apiKey" `
        --output tsv
    
    if (-not $swaToken) {
        Write-ErrorMsg "Failed to get Static Web App deployment token"
    }
    else {
        Write-Step "Building frontend..."
        Set-Location $FrontendDir
        
        try {
            npm run build
            Write-Success "Frontend built successfully"
            
            Write-Step "Deploying to Static Web App..."
            
            # Install SWA CLI if not present
            if (-not (Get-Command swa -ErrorAction SilentlyContinue)) {
                Write-Info "Installing Azure Static Web Apps CLI..."
                npm install -g @azure/static-web-apps-cli
            }
            
            swa deploy ./dist `
                --deployment-token $swaToken `
                --app-location "/" `
                --output-location "dist"
            
            Write-Success "Frontend deployed successfully"
            
            $swaUrl = az staticwebapp show `
                --name $($config.staticWebAppName) `
                --resource-group $($config.resourceGroupName) `
                --query "defaultHostname" `
                --output tsv
            
            Write-Info "Static Web App URL: https://$swaUrl"
        }
        catch {
            Write-ErrorMsg "Frontend deployment failed: $_"
            Write-Info "You can deploy manually later"
        }
        
        Set-Location $RootDir
    }
}

# ============================================================================
# STEP 10: Configure CORS
# ============================================================================
Write-Section "STEP 10: Configuring CORS"

Write-Step "Configuring CORS for Function App..."

$swaUrl = az staticwebapp show `
    --name $($config.staticWebAppName) `
    --resource-group $($config.resourceGroupName) `
    --query "defaultHostname" `
    --output tsv 2>$null

if ($swaUrl) {
    $fullSwaUrl = "https://$swaUrl"
    Write-Info "Adding $fullSwaUrl to allowed origins..."
    
    az functionapp cors add `
        --name $($config.functionAppName) `
        --resource-group $($config.resourceGroupName) `
        --allowed-origins $fullSwaUrl `
        --output none
        
    Write-Success "Added Static Web App to CORS"
}

# Add localhost for development
Write-Info "Adding localhost to allowed origins..."
az functionapp cors add `
    --name $($config.functionAppName) `
    --resource-group $($config.resourceGroupName) `
    --allowed-origins "http://localhost:5173" "http://localhost:4173" `
    --output none

Write-Success "CORS configured successfully"

# ============================================================================
# DEPLOYMENT COMPLETE
# ============================================================================
Write-Section "DEPLOYMENT COMPLETE!"

Write-Host "`n=== Deployment Summary ===" -ForegroundColor Cyan
$line = '-' * 80
Write-Host $line -ForegroundColor Gray

Write-Host "`n=== Azure Resources ===" -ForegroundColor Yellow
Write-Host "  Resource Group:      $($config.resourceGroupName)" -ForegroundColor White
Write-Host "  Location:            $($config.location)" -ForegroundColor White
Write-Host "  Storage Account:     $($config.storageAccountName)" -ForegroundColor White
Write-Host "  Cosmos DB:           $($config.cosmosDbAccountName)" -ForegroundColor White
Write-Host "  Azure OpenAI:        $($config.openAiServiceName)" -ForegroundColor White
Write-Host "  AI Search:           $($config.aiSearchServiceName)" -ForegroundColor White
Write-Host "  Function App:        $($config.functionAppName)" -ForegroundColor White
Write-Host "  Static Web App:      $($config.staticWebAppName)" -ForegroundColor White

Write-Host "`n=== Application URLs ===" -ForegroundColor Yellow
$functionUrl = "https://$($config.functionAppName).azurewebsites.net"
Write-Host "  Backend API:         $functionUrl" -ForegroundColor White

$swaUrl = az staticwebapp show `
    --name $($config.staticWebAppName) `
    --resource-group $($config.resourceGroupName) `
    --query "defaultHostname" `
    --output tsv 2>$null

if ($swaUrl) {
    Write-Host "  Frontend App:        https://$swaUrl" -ForegroundColor White
}

Write-Host "`n=== Next Steps ===" -ForegroundColor Yellow
Write-Host "  1. Test the backend API: $functionUrl/api/health" -ForegroundColor White
Write-Host "  2. Open the frontend application in your browser" -ForegroundColor White
Write-Host "  3. Monitor application in Azure Portal" -ForegroundColor White
Write-Host "  4. Review logs: az monitor activity-log list --resource-group $($config.resourceGroupName)" -ForegroundColor White

Write-Host "`n[SUCCESS] Deployment completed successfully!" -ForegroundColor Green
Write-Host $line -ForegroundColor Gray

# Cleanup
Invoke-Cleanup
