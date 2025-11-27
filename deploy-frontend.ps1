#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Deploy frontend to Azure Static Web Apps

.DESCRIPTION
    This script builds and deploys the React frontend application to Azure Static Web Apps.
    It handles dependency installation, build process, and deployment automatically.

.PARAMETER SkipBuild
    Skip the build process and deploy existing dist folder

.PARAMETER SkipDependencies
    Skip npm install step (use if dependencies are already installed)

.EXAMPLE
    .\deploy-frontend.ps1
    Full deployment with dependency installation and build

.EXAMPLE
    .\deploy-frontend.ps1 -SkipDependencies
    Deploy with existing dependencies

.EXAMPLE
    .\deploy-frontend.ps1 -SkipBuild
    Deploy existing build without rebuilding
#>

param(
    [switch]$SkipBuild,
    [switch]$SkipDependencies
)

# Error handling
$ErrorActionPreference = "Stop"

# Colors and formatting
function Write-Step {
    param([string]$Message)
    Write-Host "`n>> $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  $Message" -ForegroundColor Gray
}

# Header
Write-Host "`n" -NoNewline
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "Frontend Deployment Script" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan

# ============================================================================
# 1. Validate Prerequisites
# ============================================================================
Write-Step "Validating prerequisites..."

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Success "Node.js: $nodeVersion"
}
catch {
    Write-Error-Message "Node.js is not installed or not in PATH"
    Write-Host "Install from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version
    Write-Success "npm: v$npmVersion"
}
catch {
    Write-Error-Message "npm is not installed"
    exit 1
}

# Check Azure CLI
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Success "Azure CLI: $($azVersion.'azure-cli')"
}
catch {
    Write-Error-Message "Azure CLI is not installed or not in PATH"
    Write-Host "Install from: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    exit 1
}

# Check Azure login
Write-Step "Checking Azure authentication..."
$account = az account show 2>$null
if (-not $account) {
    Write-Error-Message "Not logged in to Azure"
    Write-Host "Please run: az login" -ForegroundColor Yellow
    exit 1
}
$accountInfo = $account | ConvertFrom-Json
Write-Success "Logged in as: $($accountInfo.user.name)"
Write-Info "Subscription: $($accountInfo.name)"

# ============================================================================
# 2. Load Configuration
# ============================================================================
Write-Step "Loading configuration..."

$configPath = Join-Path $PSScriptRoot "infrastructure\config.json"
if (-not (Test-Path $configPath)) {
    Write-Error-Message "Configuration file not found: $configPath"
    Write-Host "Run .\deploy.ps1 first to create Azure resources" -ForegroundColor Yellow
    exit 1
}

$config = Get-Content $configPath | ConvertFrom-Json
Write-Success "Configuration loaded"
Write-Info "Static Web App: $($config.staticWebAppName)"
Write-Info "Resource Group: $($config.resourceGroupName)"

# ============================================================================
# 3. Verify Azure Resources
# ============================================================================
Write-Step "Verifying Azure Static Web App..."

$tempErr = [System.IO.Path]::GetTempFileName()
$swaJson = cmd /c "az staticwebapp show --name $($config.staticWebAppName) --resource-group $($config.resourceGroupName) --output json 2>$tempErr"
Remove-Item $tempErr -ErrorAction SilentlyContinue
$swa = $swaJson | ConvertFrom-Json

if (-not $swa -or -not $swa.defaultHostname) {
    Write-Error-Message "Static Web App not found: $($config.staticWebAppName)"
    Write-Host "Run .\deploy.ps1 first to create Azure resources" -ForegroundColor Yellow
    exit 1
}

Write-Success "Static Web App found"
if ($swa.properties) {
    Write-Info "Status: $($swa.properties.provisioningState)"
}
Write-Info "URL: https://$($swa.defaultHostname)"

# ============================================================================
# 4. Get Deployment Token
# ============================================================================
Write-Step "Retrieving deployment token..."

$tempErr = [System.IO.Path]::GetTempFileName()
$token = cmd /c "az staticwebapp secrets list --name $($config.staticWebAppName) --resource-group $($config.resourceGroupName) --query properties.apiKey --output tsv 2>$tempErr"
Remove-Item $tempErr -ErrorAction SilentlyContinue
$token = $token.Trim()

if (-not $token -or $token.Length -lt 10) {
    Write-Error-Message "Failed to retrieve deployment token"
    exit 1
}

Write-Success "Deployment token retrieved"

# ============================================================================
# 5. Navigate to Frontend Directory
# ============================================================================
$frontendPath = Join-Path $PSScriptRoot "web-frontend"
if (-not (Test-Path $frontendPath)) {
    Write-Error-Message "Frontend directory not found: $frontendPath"
    exit 1
}

Push-Location $frontendPath

try {
    # ============================================================================
    # 6. Install Dependencies
    # ============================================================================
    if (-not $SkipDependencies) {
        Write-Step "Installing dependencies..."
        
        npm install --legacy-peer-deps
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Message "Failed to install dependencies"
            exit 1
        }
        
        Write-Success "Dependencies installed"
    }
    else {
        Write-Step "Skipping dependency installation (--SkipDependencies)"
    }

    # ============================================================================
    # 7. Ensure Required MSAL Packages
    # ============================================================================
    Write-Step "Verifying authentication packages..."
    
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    $hasMsalBrowser = $packageJson.dependencies.'@azure/msal-browser'
    $hasMsalReact = $packageJson.dependencies.'@azure/msal-react'
    
    if (-not $hasMsalBrowser -or -not $hasMsalReact) {
        Write-Info "Installing MSAL packages..."
        npm install @azure/msal-browser @azure/msal-react --legacy-peer-deps
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Message "Failed to install MSAL packages"
            exit 1
        }
        Write-Success "MSAL packages installed"
    }
    else {
        Write-Success "MSAL packages already installed"
    }

    # ============================================================================
    # 8. Build Frontend
    # ============================================================================
    if (-not $SkipBuild) {
        Write-Step "Building frontend..."
        
        # Remove old build
        if (Test-Path "dist") {
            Remove-Item -Recurse -Force "dist"
        }
        
        # Set API URL for build
        $functionUrl = "https://$($config.functionAppName).azurewebsites.net/api"
        $env:VITE_API_BASE_URL = $functionUrl
        Write-Info "Setting VITE_API_BASE_URL=$functionUrl"
        
        npm run build
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Message "Build failed"
            exit 1
        }
        
        if (-not (Test-Path "dist")) {
            Write-Error-Message "Build completed but dist folder not found"
            exit 1
        }
        
        Write-Success "Build completed successfully"
    }
    else {
        Write-Step "Skipping build (--SkipBuild)"
        
        if (-not (Test-Path "dist")) {
            Write-Error-Message "dist folder not found. Cannot skip build."
            exit 1
        }
    }

    # ============================================================================
    # 9. Deploy to Azure Static Web Apps
    # ============================================================================
    Write-Step "Deploying to Azure Static Web Apps..."
    
    $deployCmd = "npx @azure/static-web-apps-cli deploy ./dist --deployment-token $token --env production"
    Invoke-Expression $deployCmd
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Message "Deployment failed"
        exit 1
    }
    
    Write-Success "Deployment completed"

    # ============================================================================
    # 10. Verify Deployment
    # ============================================================================
    Write-Step "Verifying deployment..."
    
    $frontendUrl = "https://$($swa.defaultHostname)"
    
    Start-Sleep -Seconds 3
    
    try {
        $response = Invoke-WebRequest -Uri $frontendUrl -Method Get -TimeoutSec 10 -UseBasicParsing
        Write-Success "Frontend is accessible (Status: $($response.StatusCode))"
    }
    catch {
        Write-Info "Frontend may take a few moments to become available"
    }

    # ============================================================================
    # Success Summary
    # ============================================================================
    Write-Host "`n" -NoNewline
    Write-Host ("=" * 80) -ForegroundColor Green
    Write-Host "FRONTEND DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host ("=" * 80) -ForegroundColor Green
    
    Write-Host "`nDEPLOYMENT DETAILS:" -ForegroundColor Yellow
    Write-Host "  Static Web App: $($config.staticWebAppName)" -ForegroundColor White
    Write-Host "  Resource Group: $($config.resourceGroupName)" -ForegroundColor White
    Write-Host "  Region: $($config.location)" -ForegroundColor White
    
    Write-Host "`nAPPLICATION URL:" -ForegroundColor Yellow
    Write-Host "  $frontendUrl" -ForegroundColor Cyan
    
    Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
    Write-Host "  1. Open frontend in browser: $frontendUrl" -ForegroundColor Gray
    Write-Host "  2. Test application functionality" -ForegroundColor Gray
    Write-Host "  3. Set up CI/CD with: .\setup-github-secrets.ps1" -ForegroundColor Gray
    
    Write-Host "`nADDITIONAL COMMANDS:" -ForegroundColor Yellow
    Write-Host "  View logs:     az staticwebapp show --name $($config.staticWebAppName) -g $($config.resourceGroupName)" -ForegroundColor Gray
    Write-Host "  Redeploy:      .\deploy-frontend.ps1" -ForegroundColor Gray
    Write-Host "  Quick deploy:  .\deploy-frontend.ps1 -SkipDependencies" -ForegroundColor Gray
    
    Write-Host ""
}
finally {
    Pop-Location
}
