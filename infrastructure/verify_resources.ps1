# Azure Resource Verification Script
# Verifies that all required Azure resources exist and are properly configured

$ErrorActionPreference = "Stop"

# Load Configuration
$configPath = Join-Path $PSScriptRoot "config.json"
if (-not (Test-Path $configPath)) {
    Write-Error "Configuration file not found at $configPath"
    exit 1
}
$config = Get-Content $configPath | ConvertFrom-Json

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Azure Resource Verification" -ForegroundColor Cyan
Write-Host "=" * 80
Write-Host ""

$rgName = $config.resourceGroupName
$allResourcesExist = $true

# Helper function to check resource
function Test-AzureResource {
    param(
        [string]$ResourceType,
        [string]$ResourceName,
        [scriptblock]$CheckCommand
    )
    
    Write-Host "Checking $ResourceType`: $ResourceName..." -NoNewline
    
    try {
        $result = & $CheckCommand
        if ($LASTEXITCODE -eq 0 -and $result) {
            Write-Host " ✓" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host " ✗ NOT FOUND" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host " ✗ ERROR: $_" -ForegroundColor Red
        return $false
    }
}

# 1. Resource Group
$exists = Test-AzureResource -ResourceType "Resource Group" -ResourceName $rgName -CheckCommand {
    az group show --name $rgName --output json 2>$null
}
$allResourcesExist = $allResourcesExist -and $exists

# 2. Storage Account
$exists = Test-AzureResource -ResourceType "Storage Account" -ResourceName $config.storageAccountName -CheckCommand {
    az storage account show --name $config.storageAccountName --resource-group $rgName --output json 2>$null
}
$allResourcesExist = $allResourcesExist -and $exists

# 2b. Check knowledge-base container
Write-Host "Checking Blob Container: knowledge-base..." -NoNewline
try {
    $containerExists = az storage container exists `
        --account-name $config.storageAccountName `
        --name "knowledge-base" `
        --auth-mode login `
        --output json 2>$null | ConvertFrom-Json
    
    if ($containerExists.exists) {
        Write-Host " ✓" -ForegroundColor Green
    }
    else {
        Write-Host " ✗ NOT FOUND" -ForegroundColor Yellow
        Write-Host "  Note: Run upload_dataset.ps1 to create container and upload files" -ForegroundColor Yellow
    }
}
catch {
    Write-Host " ✗ ERROR" -ForegroundColor Red
}

# 3. Cosmos DB
$exists = Test-AzureResource -ResourceType "Cosmos DB Account" -ResourceName $config.cosmosDbAccountName -CheckCommand {
    az cosmosdb show --name $config.cosmosDbAccountName --resource-group $rgName --output json 2>$null
}
$allResourcesExist = $allResourcesExist -and $exists

# 3b. Check Cosmos DB Database
$exists = Test-AzureResource -ResourceType "Cosmos DB Database" -ResourceName $config.cosmosDbDatabaseName -CheckCommand {
    az cosmosdb sql database show `
        --account-name $config.cosmosDbAccountName `
        --resource-group $rgName `
        --name $config.cosmosDbDatabaseName `
        --output json 2>$null
}
$allResourcesExist = $allResourcesExist -and $exists

# 4. Azure OpenAI
$exists = Test-AzureResource -ResourceType "Azure OpenAI Service" -ResourceName $config.openAiServiceName -CheckCommand {
    az cognitiveservices account show --name $config.openAiServiceName --resource-group $rgName --output json 2>$null
}
$allResourcesExist = $allResourcesExist -and $exists

# 4b. Check GPT-4o deployment
Write-Host "Checking OpenAI Deployment: gpt-4o..." -NoNewline
try {
    $deployment = az cognitiveservices account deployment show `
        --name $config.openAiServiceName `
        --resource-group $rgName `
        --deployment-name "gpt-4o" `
        --output json 2>$null
    
    if ($LASTEXITCODE -eq 0 -and $deployment) {
        Write-Host " ✓" -ForegroundColor Green
    }
    else {
        Write-Host " ✗ NOT FOUND" -ForegroundColor Red
        Write-Host "  Note: Deploy GPT-4o model manually or re-run deploy_resources.ps1" -ForegroundColor Yellow
        $allResourcesExist = $false
    }
}
catch {
    Write-Host " ✗ ERROR" -ForegroundColor Red
    $allResourcesExist = $false
}

# 5. Azure AI Search
$exists = Test-AzureResource -ResourceType "Azure AI Search" -ResourceName $config.aiSearchServiceName -CheckCommand {
    az search service show --name $config.aiSearchServiceName --resource-group $rgName --output json 2>$null
}
$allResourcesExist = $allResourcesExist -and $exists

# 5b. Check Search Index
Write-Host "Checking Search Index: $($config.searchIndexName)..." -NoNewline
try {
    $index = az search index show `
        --name $config.searchIndexName `
        --service-name $config.aiSearchServiceName `
        --resource-group $rgName `
        --output json 2>$null
    
    if ($LASTEXITCODE -eq 0 -and $index) {
        Write-Host " ✓" -ForegroundColor Green
    }
    else {
        Write-Host " ✗ NOT FOUND" -ForegroundColor Yellow
        Write-Host "  Note: Run create_search_index.py to create the index" -ForegroundColor Yellow
    }
}
catch {
    Write-Host " ✗ ERROR" -ForegroundColor Red
}

# 6. Document Intelligence (optional)
$exists = Test-AzureResource -ResourceType "Document Intelligence" -ResourceName $config.documentIntelligenceServiceName -CheckCommand {
    az cognitiveservices account show --name $config.documentIntelligenceServiceName --resource-group $rgName --output json 2>$null
}
if (-not $exists) {
    Write-Host "  Note: Document Intelligence is optional for PDF processing" -ForegroundColor Yellow
}

# 7. Function App
$exists = Test-AzureResource -ResourceType "Function App" -ResourceName $config.functionAppName -CheckCommand {
    az functionapp show --name $config.functionAppName --resource-group $rgName --output json 2>$null
}
$allResourcesExist = $allResourcesExist -and $exists

# 8. Static Web App
$exists = Test-AzureResource -ResourceType "Static Web App" -ResourceName $config.staticWebAppName -CheckCommand {
    az staticwebapp show --name $config.staticWebAppName --resource-group $rgName --output json 2>$null
}
$allResourcesExist = $allResourcesExist -and $exists

# Summary
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
if ($allResourcesExist) {
    Write-Host "✓ All required Azure resources exist!" -ForegroundColor Green
}
else {
    Write-Host "✗ Some resources are missing or not configured" -ForegroundColor Red
    Write-Host ""
    Write-Host "To create missing resources, run:" -ForegroundColor Yellow
    Write-Host "  .\infrastructure\deploy_resources.ps1" -ForegroundColor Gray
}
Write-Host "=" * 80 -ForegroundColor Cyan
