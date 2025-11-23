#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup Azure Storage Account permissions for blob access

.DESCRIPTION
    This script automates the setup of Azure Storage Account by:
    1. Checking Azure CLI authentication
    2. Getting current user's object ID
    3. Assigning necessary RBAC roles for blob storage access
    4. Optionally creating the knowledge-base container

.PARAMETER ResourceGroup
    The Azure resource group name (default: from config.json)

.PARAMETER StorageAccountName
    The Azure Storage Account name (default: from config.json)

.PARAMETER ContainerName
    The blob container name (default: knowledge-base)

.PARAMETER SkipRoleAssignment
    Skip RBAC role assignment if already configured

.EXAMPLE
    .\setup_storage_permissions.ps1
    
.EXAMPLE
    .\setup_storage_permissions.ps1 -SkipRoleAssignment
#>

[CmdletBinding()]
param(
    [string]$ResourceGroup,
    [string]$StorageAccountName,
    [string]$ContainerName = "knowledge-base",
    [switch]$SkipRoleAssignment
)

$ErrorActionPreference = "Stop"

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigPath = Join-Path $ScriptDir "config.json"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Azure Storage Account Permissions Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Load configuration
if (-not (Test-Path $ConfigPath)) {
    Write-Host "✗ Configuration file not found at $ConfigPath" -ForegroundColor Red
    Write-Host "Please run deploy_resources.ps1 first." -ForegroundColor Yellow
    exit 1
}

Write-Host "Loading configuration..." -ForegroundColor Gray
$Config = Get-Content $ConfigPath | ConvertFrom-Json

# Use config values if not provided
if (-not $ResourceGroup) {
    $ResourceGroup = $Config.resourceGroupName
}
if (-not $StorageAccountName) {
    $StorageAccountName = $Config.storageAccountName
}

Write-Host "✓ Configuration loaded" -ForegroundColor Green
Write-Host "  Resource Group: $ResourceGroup" -ForegroundColor Gray
Write-Host "  Storage Account: $StorageAccountName" -ForegroundColor Gray
Write-Host "  Container: $ContainerName" -ForegroundColor Gray
Write-Host ""

# Check Azure CLI login
Write-Host "Checking Azure CLI authentication..." -ForegroundColor Gray
try {
    $Account = az account show 2>$null | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) {
        throw "Not logged in"
    }
    Write-Host "✓ Logged in as: $($Account.user.name)" -ForegroundColor Green
    $SubscriptionId = $Account.id
    Write-Host "  Subscription: $($Account.name)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "✗ Not logged in to Azure CLI" -ForegroundColor Red
    Write-Host "Please run: az login" -ForegroundColor Yellow
    exit 1
}

# Verify storage account exists
Write-Host "Verifying storage account exists..." -ForegroundColor Gray
try {
    $StorageAccount = az storage account show `
        --name $StorageAccountName `
        --resource-group $ResourceGroup `
        2>$null | ConvertFrom-Json
    
    if ($LASTEXITCODE -ne 0) {
        throw "Storage account not found"
    }
    
    Write-Host "✓ Storage account found" -ForegroundColor Green
    Write-Host "  Location: $($StorageAccount.location)" -ForegroundColor Gray
    Write-Host "  SKU: $($StorageAccount.sku.name)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "✗ Storage account not found: $StorageAccountName in resource group: $ResourceGroup" -ForegroundColor Red
    Write-Host "Please run deploy_resources.ps1 first to create the storage account." -ForegroundColor Yellow
    exit 1
}

# Get current user's object ID
if (-not $SkipRoleAssignment) {
    Write-Host "Getting current user's object ID..." -ForegroundColor Gray
    try {
        $UserObjectId = az ad signed-in-user show --query id --output tsv 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to get user object ID"
        }
        Write-Host "✓ User Object ID: $UserObjectId" -ForegroundColor Green
        Write-Host ""
    } catch {
        Write-Host "✗ Failed to get user object ID" -ForegroundColor Red
        exit 1
    }

    # Construct resource scope
    $ResourceScope = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.Storage/storageAccounts/$StorageAccountName"

    # Assign Storage Blob Data Contributor role
    Write-Host "Assigning Storage Blob Data Contributor role..." -ForegroundColor Gray
    try {
        $Role1 = az role assignment create `
            --role "Storage Blob Data Contributor" `
            --assignee $UserObjectId `
            --scope $ResourceScope `
            2>$null | ConvertFrom-Json
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Role assigned successfully" -ForegroundColor Green
        } else {
            Write-Host "⚠ Role may already be assigned (skipping)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ Role assignment may already exist (continuing)" -ForegroundColor Yellow
    }

    # Assign Storage Blob Data Reader role (for redundancy)
    Write-Host "Assigning Storage Blob Data Reader role..." -ForegroundColor Gray
    try {
        $Role2 = az role assignment create `
            --role "Storage Blob Data Reader" `
            --assignee $UserObjectId `
            --scope $ResourceScope `
            2>$null | ConvertFrom-Json
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Role assigned successfully" -ForegroundColor Green
        } else {
            Write-Host "⚠ Role may already be assigned (skipping)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ Role assignment may already exist (continuing)" -ForegroundColor Yellow
    }
    Write-Host ""

    # Wait for role assignments to propagate
    Write-Host "Waiting for role assignments to propagate..." -ForegroundColor Gray
    Start-Sleep -Seconds 15
    Write-Host "✓ Permissions ready" -ForegroundColor Green
    Write-Host ""
}

# Check if container exists and create if needed
Write-Host "Checking blob container: $ContainerName..." -ForegroundColor Gray
try {
    $ContainerExists = az storage container exists `
        --name $ContainerName `
        --account-name $StorageAccountName `
        --auth-mode login `
        2>$null | ConvertFrom-Json
    
    if ($ContainerExists.exists) {
        Write-Host "✓ Container already exists" -ForegroundColor Green
    } else {
        Write-Host "⚠ Container does not exist. Creating..." -ForegroundColor Yellow
        
        az storage container create `
            --name $ContainerName `
            --account-name $StorageAccountName `
            --auth-mode login `
            --public-access off `
            2>$null | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Container created successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to create container" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "⚠ Unable to verify container (it may not exist yet)" -ForegroundColor Yellow
    Write-Host "You can create it manually or upload files to create it automatically." -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Storage account is now configured with proper permissions." -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Upload documents to the container: $ContainerName" -ForegroundColor White
Write-Host "   .\infrastructure\upload_dataset.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Index the documents in Azure AI Search:" -ForegroundColor White
Write-Host "   python infrastructure\index_documents.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Or upload directly via Azure Portal" -ForegroundColor White
