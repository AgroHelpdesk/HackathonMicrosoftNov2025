#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup Azure AI Search service with proper authentication and permissions

.DESCRIPTION
    This script automates the setup of Azure AI Search service by:
    1. Checking Azure CLI authentication
    2. Getting current user's object ID
    3. Assigning necessary RBAC roles
    4. Enabling Azure AD authentication on the search service
    5. Creating the search index

.PARAMETER ResourceGroup
    The Azure resource group name (default: from config.json)

.PARAMETER SearchServiceName
    The Azure AI Search service name (default: from config.json)

.PARAMETER SkipRoleAssignment
    Skip RBAC role assignment if already configured

.EXAMPLE
    .\setup_search_service.ps1
    
.EXAMPLE
    .\setup_search_service.ps1 -SkipRoleAssignment
#>

[CmdletBinding()]
param(
    [string]$ResourceGroup,
    [string]$SearchServiceName,
    [switch]$SkipRoleAssignment
)

$ErrorActionPreference = "Stop"

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigPath = Join-Path $ScriptDir "config.json"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Azure AI Search Service Setup" -ForegroundColor Cyan
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
if (-not $SearchServiceName) {
    $SearchServiceName = $Config.aiSearchServiceName
}

Write-Host "✓ Configuration loaded" -ForegroundColor Green
Write-Host "  Resource Group: $ResourceGroup" -ForegroundColor Gray
Write-Host "  Search Service: $SearchServiceName" -ForegroundColor Gray
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

# Verify search service exists
Write-Host "Verifying search service exists..." -ForegroundColor Gray
try {
    $SearchService = az search service show `
        --name $SearchServiceName `
        --resource-group $ResourceGroup `
        2>$null | ConvertFrom-Json
    
    if ($LASTEXITCODE -ne 0) {
        throw "Service not found"
    }
    
    Write-Host "✓ Search service found" -ForegroundColor Green
    Write-Host "  Location: $($SearchService.location)" -ForegroundColor Gray
    Write-Host "  Status: $($SearchService.status)" -ForegroundColor Gray
    Write-Host "  SKU: $($SearchService.sku.name)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "✗ Search service '$SearchServiceName' not found in resource group '$ResourceGroup'" -ForegroundColor Red
    Write-Host "Please run deploy_resources.ps1 first to create the service." -ForegroundColor Yellow
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
    $ResourceScope = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.Search/searchServices/$SearchServiceName"

    # Assign Search Index Data Contributor role
    Write-Host "Assigning 'Search Index Data Contributor' role..." -ForegroundColor Gray
    try {
        $Role1 = az role assignment create `
            --role "Search Index Data Contributor" `
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

    # Assign Search Service Contributor role
    Write-Host "Assigning 'Search Service Contributor' role..." -ForegroundColor Gray
    try {
        $Role2 = az role assignment create `
            --role "Search Service Contributor" `
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
}

# Enable Azure AD authentication
Write-Host "Enabling Azure AD authentication on search service..." -ForegroundColor Gray
try {
    $AuthUpdate = az search service update `
        --name $SearchServiceName `
        --resource-group $ResourceGroup `
        --auth-options aadOrApiKey `
        --aad-auth-failure-mode http401WithBearerChallenge `
        2>$null | ConvertFrom-Json
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Azure AD authentication enabled" -ForegroundColor Green
        Write-Host "  Auth Mode: $($AuthUpdate.authOptions.aadOrApiKey.aadAuthFailureMode)" -ForegroundColor Gray
        Write-Host ""
    }
} catch {
    Write-Host "⚠ Azure AD authentication may already be enabled" -ForegroundColor Yellow
    Write-Host ""
}

# Wait for role assignments to propagate
if (-not $SkipRoleAssignment) {
    Write-Host "Waiting for role assignments to propagate..." -ForegroundColor Gray
    Start-Sleep -Seconds 15
    Write-Host "✓ Ready to create index" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment and run Python script
Write-Host "Creating search index..." -ForegroundColor Gray
Write-Host ""

$VenvPath = Join-Path (Split-Path $ScriptDir -Parent) ".venv\Scripts\Activate.ps1"
$PythonScript = Join-Path $ScriptDir "create_search_index.py"

if (Test-Path $VenvPath) {
    # Activate venv and run script
    & $VenvPath
    python $PythonScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "Setup Complete!" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "1. Run the indexing script to populate the index:" -ForegroundColor White
        Write-Host "   python infrastructure\index_documents.py" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "2. Or use the upload script for CSV data:" -ForegroundColor White
        Write-Host "   .\infrastructure\upload_dataset.ps1" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "✗ Index creation failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ Virtual environment not found at $VenvPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Creating virtual environment and installing dependencies..." -ForegroundColor Yellow
    
    # Create venv
    $VenvDir = Join-Path (Split-Path $ScriptDir -Parent) ".venv"
    python -m venv $VenvDir
    
    # Activate and install
    & "$VenvDir\Scripts\Activate.ps1"
    python -m pip install --upgrade pip
    pip install -r (Join-Path $ScriptDir "requirements.txt")
    
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
    Write-Host ""
    Write-Host "Please run this script again to create the search index." -ForegroundColor Yellow
}
