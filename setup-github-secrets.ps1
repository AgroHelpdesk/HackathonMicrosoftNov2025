#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Configure GitHub Actions Secrets for Azure Deployment

.DESCRIPTION
    This script sets up the required GitHub secrets for the CI/CD pipeline:
    - AZURE_CREDENTIALS: Service principal credentials for Azure login
    - AZURE_STATIC_WEB_APPS_API_TOKEN: Deployment token for Static Web Apps

.PARAMETER GitHubRepo
    GitHub repository in format "owner/repo" (e.g., "led-21/HackathonMicrosoftNov2025")

.PARAMETER GitHubToken
    GitHub Personal Access Token with repo and workflow permissions
    Generate at: https://github.com/settings/tokens

.EXAMPLE
    .\setup-github-secrets.ps1 -GitHubRepo "owner/repo" -GitHubToken "ghp_xxxx"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$GitHubRepo,
    
    [Parameter(Mandatory=$false)]
    [string]$GitHubToken
)

$ErrorActionPreference = "Stop"

# Load configuration
$ConfigPath = Join-Path $PSScriptRoot "infrastructure\config.json"
if (-not (Test-Path $ConfigPath)) {
    Write-Error "Configuration file not found: $ConfigPath"
    exit 1
}

$config = Get-Content $ConfigPath | ConvertFrom-Json

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "GitHub Actions Setup for Azure Deployment" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# Get GitHub repository
if (-not $GitHubRepo) {
    Write-Host "`nEnter your GitHub repository (format: owner/repo):" -ForegroundColor Yellow
    Write-Host "Example: led-21/HackathonMicrosoftNov2025" -ForegroundColor Gray
    $GitHubRepo = Read-Host "Repository"
}

# Get GitHub token
if (-not $GitHubToken) {
    Write-Host "`nGitHub Personal Access Token is required." -ForegroundColor Yellow
    Write-Host "Generate one at: https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host "Required scopes: repo, workflow" -ForegroundColor Gray
    $GitHubToken = Read-Host "GitHub Token" -AsSecureString
    $GitHubToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($GitHubToken))
}

Write-Host "`n>> Checking Azure login..." -ForegroundColor Yellow
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Host "[OK] Logged in as: $($account.user.name)" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Not logged in to Azure" -ForegroundColor Red
    Write-Host "Please run: az login" -ForegroundColor Gray
    exit 1
}

# Step 1: Create Service Principal for Azure Functions Deployment
Write-Host "`n>> Creating Azure Service Principal..." -ForegroundColor Yellow

$subscriptionId = $account.id
$spName = "sp-github-$($config.functionAppName)"

$sp = az ad sp create-for-rbac `
    --name $spName `
    --role Contributor `
    --scopes "/subscriptions/$subscriptionId/resourceGroups/$($config.resourceGroupName)" `
    --sdk-auth 2>$null | ConvertFrom-Json

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Service Principal created: $spName" -ForegroundColor Green
    $azureCredentials = $sp | ConvertTo-Json -Compress
} else {
    Write-Host "[ERROR] Failed to create Service Principal" -ForegroundColor Red
    exit 1
}

# Step 2: Get Static Web App Deployment Token
Write-Host "`n>> Getting Static Web App deployment token..." -ForegroundColor Yellow

$swaToken = az staticwebapp secrets list `
    --name $config.staticWebAppName `
    --resource-group $config.resourceGroupName `
    --query "properties.apiKey" `
    --output tsv 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Static Web App token retrieved" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to get Static Web App token" -ForegroundColor Red
    exit 1
}

# Step 3: Set GitHub Secrets
Write-Host "`n>> Setting GitHub secrets..." -ForegroundColor Yellow

# Function to set GitHub secret
function Set-GitHubSecret {
    param(
        [string]$Name,
        [string]$Value,
        [string]$Repo,
        [string]$Token
    )
    
    # Encrypt the secret value using GitHub's public key
    $publicKeyUrl = "https://api.github.com/repos/$Repo/actions/secrets/public-key"
    $headers = @{
        "Authorization" = "token $Token"
        "Accept" = "application/vnd.github+json"
    }
    
    $publicKeyResponse = Invoke-RestMethod -Uri $publicKeyUrl -Headers $headers -Method Get
    $publicKey = $publicKeyResponse.key
    $keyId = $publicKeyResponse.key_id
    
    # Use libsodium to encrypt (requires sodium.dll or manual base64 encoding)
    # For simplicity, we'll use GitHub CLI if available
    $ghCliInstalled = Get-Command gh -ErrorAction SilentlyContinue
    
    if ($ghCliInstalled) {
        Write-Host "  Using GitHub CLI to set secret: $Name" -ForegroundColor Gray
        $env:GH_TOKEN = $Token
        echo $Value | gh secret set $Name --repo $Repo
    } else {
        Write-Host "  [WARNING] GitHub CLI not found. Please set secrets manually:" -ForegroundColor Yellow
        Write-Host "    gh secret set $Name --repo $Repo" -ForegroundColor Gray
        return $false
    }
    
    return $true
}

# Try to set secrets
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if ($ghInstalled) {
    $env:GH_TOKEN = $GitHubToken
    
    Write-Host "  Setting AZURE_CREDENTIALS..." -ForegroundColor Gray
    echo $azureCredentials | gh secret set AZURE_CREDENTIALS --repo $GitHubRepo
    
    Write-Host "  Setting AZURE_STATIC_WEB_APPS_API_TOKEN..." -ForegroundColor Gray
    echo $swaToken | gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --repo $GitHubRepo
    
    Write-Host "[OK] GitHub secrets configured successfully!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] GitHub CLI not installed" -ForegroundColor Yellow
    Write-Host "`nPlease install GitHub CLI and run:" -ForegroundColor Yellow
    Write-Host "  gh auth login" -ForegroundColor Gray
    Write-Host "  gh secret set AZURE_CREDENTIALS --repo $GitHubRepo" -ForegroundColor Gray
    Write-Host "  gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --repo $GitHubRepo" -ForegroundColor Gray
    
    Write-Host "`nOr set secrets manually in GitHub:" -ForegroundColor Yellow
    Write-Host "  https://github.com/$GitHubRepo/settings/secrets/actions" -ForegroundColor Cyan
    
    Write-Host "`n--- AZURE_CREDENTIALS ---" -ForegroundColor Yellow
    Write-Host $azureCredentials -ForegroundColor Gray
    
    Write-Host "`n--- AZURE_STATIC_WEB_APPS_API_TOKEN ---" -ForegroundColor Yellow
    Write-Host $swaToken -ForegroundColor Gray
}

Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`nWorkflow file created at:" -ForegroundColor Green
Write-Host "  .github/workflows/azure-deploy.yml" -ForegroundColor White

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Verify secrets are set in GitHub:" -ForegroundColor White
Write-Host "     https://github.com/$GitHubRepo/settings/secrets/actions" -ForegroundColor Cyan
Write-Host "  2. Commit and push the workflow file:" -ForegroundColor White
Write-Host "     git add .github/workflows/azure-deploy.yml" -ForegroundColor Gray
Write-Host "     git commit -m 'Add Azure deployment workflow'" -ForegroundColor Gray
Write-Host "     git push origin main" -ForegroundColor Gray
Write-Host "  3. Monitor the deployment:" -ForegroundColor White
Write-Host "     https://github.com/$GitHubRepo/actions" -ForegroundColor Cyan
