#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Cleanup and Delete All Azure Resources

.DESCRIPTION
    This script removes all Azure resources created for the Agro Auto-Resolve application.
    It will delete the entire resource group and all resources within it.

.PARAMETER Force
    Skip confirmation prompts

.PARAMETER KeepResourceGroup
    Delete resources but keep the resource group

.EXAMPLE
    .\cleanup.ps1
    
.EXAMPLE
    .\cleanup.ps1 -Force
#>

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$KeepResourceGroup
)

$ErrorActionPreference = "Stop"

# Script paths
$InfraDir = Join-Path $PSScriptRoot "infrastructure"
$ConfigPath = Join-Path $InfraDir "config.json"

function Write-Section {
    param([string]$Message)
    Write-Host "`n$('=' * 80)" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "$('=' * 80)" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Load configuration
if (-not (Test-Path $ConfigPath)) {
    Write-ErrorMsg "Configuration file not found: $ConfigPath"
    Write-Host "Nothing to clean up." -ForegroundColor Gray
    exit 0
}

$config = Get-Content $ConfigPath | ConvertFrom-Json
$resourceGroupName = $config.resourceGroupName

Write-Section "Azure Resources Cleanup"

Write-Host "`nThis script will delete the following:" -ForegroundColor Yellow
Write-Host "  - Resource Group:      $resourceGroupName" -ForegroundColor White
Write-Host "  - Storage Account:     $($config.storageAccountName)" -ForegroundColor White
Write-Host "  - Cosmos DB:           $($config.cosmosDbAccountName)" -ForegroundColor White
Write-Host "  - Azure OpenAI:        $($config.openAiServiceName)" -ForegroundColor White
Write-Host "  - AI Search:           $($config.aiSearchServiceName)" -ForegroundColor White
Write-Host "  - Function App:        $($config.functionAppName)" -ForegroundColor White
Write-Host "  - Static Web App:      $($config.staticWebAppName)" -ForegroundColor White
Write-Host "  - All data and configurations" -ForegroundColor White

if (-not $Force) {
    Write-Host "`n" -NoNewline
    Write-Warning "This action cannot be undone!"
    $confirmation = Read-Host "Are you sure you want to delete all resources? (yes/no)"
    
    if ($confirmation -ne "yes") {
        Write-Host "`nCleanup cancelled." -ForegroundColor Gray
        exit 0
    }
}

Write-Host "`n" -ForegroundColor White

# Check if logged in
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Gray
}
catch {
    Write-ErrorMsg "Not logged in to Azure"
    Write-Host "Please run: az login" -ForegroundColor Gray
    exit 1
}

# Check if resource group exists
Write-Host "Checking if resource group exists..." -ForegroundColor Gray
$rgExists = az group exists --name $resourceGroupName

if ($rgExists -eq "false") {
    Write-Host "Resource group '$resourceGroupName' does not exist." -ForegroundColor Gray
    Write-Success "Nothing to clean up"
    exit 0
}

if ($KeepResourceGroup) {
    Write-Section "Deleting Individual Resources"
    
    # Delete Static Web App
    Write-Host "Deleting Static Web App..." -ForegroundColor Yellow
    try {
        az staticwebapp delete `
            --name $($config.staticWebAppName) `
            --resource-group $resourceGroupName `
            --yes `
            --output none 2>$null
        Write-Success "Static Web App deleted"
    }
    catch {
        Write-Host "  (resource may not exist)" -ForegroundColor Gray
    }
    
    # Delete Function App
    Write-Host "Deleting Function App..." -ForegroundColor Yellow
    try {
        az functionapp delete `
            --name $($config.functionAppName) `
            --resource-group $resourceGroupName `
            --output none 2>$null
        Write-Success "Function App deleted"
    }
    catch {
        Write-Host "  (resource may not exist)" -ForegroundColor Gray
    }
    
    # Delete AI Search
    Write-Host "Deleting AI Search service..." -ForegroundColor Yellow
    try {
        az search service delete `
            --name $($config.aiSearchServiceName) `
            --resource-group $resourceGroupName `
            --yes `
            --output none 2>$null
        Write-Success "AI Search service deleted"
    }
    catch {
        Write-Host "  (resource may not exist)" -ForegroundColor Gray
    }
    
    # Delete Document Intelligence
    Write-Host "Deleting Document Intelligence service..." -ForegroundColor Yellow
    try {
        az cognitiveservices account delete `
            --name $($config.documentIntelligenceServiceName) `
            --resource-group $resourceGroupName `
            --output none 2>$null
        Write-Success "Document Intelligence service deleted"
    }
    catch {
        Write-Host "  (resource may not exist)" -ForegroundColor Gray
    }
    
    # Delete Azure OpenAI
    Write-Host "Deleting Azure OpenAI service..." -ForegroundColor Yellow
    try {
        az cognitiveservices account delete `
            --name $($config.openAiServiceName) `
            --resource-group $resourceGroupName `
            --output none 2>$null
        Write-Success "Azure OpenAI service deleted"
    }
    catch {
        Write-Host "  (resource may not exist)" -ForegroundColor Gray
    }
    
    # Delete Cosmos DB
    Write-Host "Deleting Cosmos DB account..." -ForegroundColor Yellow
    try {
        az cosmosdb delete `
            --name $($config.cosmosDbAccountName) `
            --resource-group $resourceGroupName `
            --yes `
            --output none 2>$null
        Write-Success "Cosmos DB account deleted"
    }
    catch {
        Write-Host "  (resource may not exist)" -ForegroundColor Gray
    }
    
    # Delete Storage Account
    Write-Host "Deleting Storage Account..." -ForegroundColor Yellow
    try {
        az storage account delete `
            --name $($config.storageAccountName) `
            --resource-group $resourceGroupName `
            --yes `
            --output none 2>$null
        Write-Success "Storage Account deleted"
    }
    catch {
        Write-Host "  (resource may not exist)" -ForegroundColor Gray
    }
    
    Write-Success "All resources deleted, resource group preserved"
}
else {
    Write-Section "Deleting Resource Group"
    
    Write-Host "Deleting resource group: $resourceGroupName" -ForegroundColor Yellow
    Write-Host "(This may take several minutes...)" -ForegroundColor Gray
    
    try {
        az group delete `
            --name $resourceGroupName `
            --yes `
            --no-wait
        
        Write-Success "Resource group deletion initiated"
        Write-Host "`nThe deletion is running in the background." -ForegroundColor Gray
        Write-Host "Monitor progress with: az group show --name $resourceGroupName" -ForegroundColor Gray
    }
    catch {
        Write-ErrorMsg "Failed to delete resource group: $_"
        exit 1
    }
}

Write-Section "Cleanup Complete"

Write-Host "`n[SUCCESS] Cleanup completed successfully!" -ForegroundColor Green
Write-Host "`nTo verify deletion:" -ForegroundColor Yellow
Write-Host "  az group show --name $resourceGroupName" -ForegroundColor Gray
Write-Host "`nTo see all your resource groups:" -ForegroundColor Yellow
Write-Host "  az group list --output table" -ForegroundColor Gray
