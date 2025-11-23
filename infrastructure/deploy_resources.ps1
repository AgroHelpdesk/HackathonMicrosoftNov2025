# Azure Infrastructure Deployment Script
# Reads configuration from config.json and provisions resources using Azure CLI

$ErrorActionPreference = "Stop"

# Load Configuration
$configPath = Join-Path $PSScriptRoot "config.json"
if (-not (Test-Path $configPath)) {
    Write-Error "Configuration file not found at $configPath"
    exit 1
}
$config = Get-Content $configPath | ConvertFrom-Json

# Variables
$rgName = $config.resourceGroupName
$location = $config.location

Write-Host "Starting deployment for Resource Group: $rgName in $location..." -ForegroundColor Cyan

# 1. Create Resource Group
Write-Host "Creating Resource Group..."
az group create --name $rgName --location $location

# 2. Create Storage Account (for Function App and Blob Storage)
Write-Host "Creating Storage Account: $($config.storageAccountName)..."
az storage account create `
    --name $config.storageAccountName `
    --resource-group $rgName `
    --location $location `
    --sku Standard_LRS `
    --kind StorageV2

# 3. Create Cosmos DB Account (Serverless for cost efficiency)
Write-Host "Creating Cosmos DB Account: $($config.cosmosDbAccountName)..."
az cosmosdb create `
    --name $config.cosmosDbAccountName `
    --resource-group $rgName `
    --locations regionName=$location failoverPriority=0 isZoneRedundant=False `
    --default-consistency-level Session `
    --capabilities EnableServerless

# Create Cosmos DB Database
Write-Host "Creating Cosmos DB Database: $($config.cosmosDbDatabaseName)..."
az cosmosdb sql database create `
    --account-name $config.cosmosDbAccountName `
    --resource-group $rgName `
    --name $config.cosmosDbDatabaseName

# 4. Create Azure OpenAI Service
Write-Host "Creating Azure OpenAI Service: $($config.openAiServiceName)..."
az cognitiveservices account create `
    --name $config.openAiServiceName `
    --resource-group $rgName `
    --location $location `
    --kind OpenAI `
    --sku S0 `
    --yes

# 5. Create Azure AI Search
Write-Host "Creating Azure AI Search Service: $($config.aiSearchServiceName)..."
az search service create `
    --name $config.aiSearchServiceName `
    --resource-group $rgName `
    --location $location `
    --sku basic

# 6. Create Function App (Python)
# Note: Using Consumption Plan (Serverless)
Write-Host "Creating Function App: $($config.functionAppName)..."
az functionapp create `
    --name $config.functionAppName `
    --storage-account $config.storageAccountName `
    --resource-group $rgName `
    --consumption-plan-location $location `
    --runtime python `
    --runtime-version 3.10 `
    --functions-version 4 `
    --os-type Linux

# 7. Create Azure Static Web App
Write-Host "Creating Azure Static Web App: $($config.staticWebAppName)..."
az staticwebapp create `
    --name $config.staticWebAppName `
    --resource-group $rgName `
    --location $location `
    --sku Free

Write-Host "Deployment Script Completed Successfully!" -ForegroundColor Green
Write-Host "Please verify resources in the Azure Portal."
