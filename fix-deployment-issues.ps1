#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Fix Common Deployment Issues

.DESCRIPTION
    This script fixes the most common issues found after deployment:
    1. Creates missing storage container
    2. Installs missing frontend dependencies
    3. Uploads dataset files
    4. Creates and populates search index

.EXAMPLE
    .\fix-deployment-issues.ps1
#>

$ErrorActionPreference = "Stop"

$ConfigPath = Join-Path $PSScriptRoot "infrastructure\config.json"
$config = Get-Content $ConfigPath | ConvertFrom-Json

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Fixing Deployment Issues" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# ============================================================================
# Issue 1: Missing Storage Container
# ============================================================================
Write-Host "`n>> Checking storage container..." -ForegroundColor Yellow

$containerExists = az storage container exists --account-name $config.storageAccountName --name knowledge-base --auth-mode login --query "exists" --output tsv 2>$null

if ($containerExists -eq "true") {
    Write-Host "[OK] Storage container exists" -ForegroundColor Green
}
else {
    Write-Host "[FIX] Creating storage container..." -ForegroundColor Yellow
    
    az storage container create --account-name $config.storageAccountName --name knowledge-base --auth-mode login --output none
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Storage container created" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Failed to create storage container" -ForegroundColor Red
    }
}

# ============================================================================
# Issue 2: Missing Frontend Dependencies
# ============================================================================
Write-Host "`n>> Checking frontend dependencies..." -ForegroundColor Yellow

$msalInstalled = npm list @azure/msal-browser --prefix web-frontend 2>&1 | Select-String "@azure/msal-browser"

if ($msalInstalled) {
    Write-Host "[OK] @azure/msal-browser is installed" -ForegroundColor Green
}
else {
    Write-Host "[FIX] Installing missing dependencies..." -ForegroundColor Yellow
    
    Push-Location web-frontend
    npm install @azure/msal-browser
    Pop-Location
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Dependencies installed" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    }
}

# ============================================================================
# Issue 3: Upload Dataset Files
# ============================================================================
Write-Host "`n>> Checking dataset files in storage..." -ForegroundColor Yellow

$blobList = az storage blob list --account-name $config.storageAccountName --container-name knowledge-base --auth-mode login --output json 2>$null | ConvertFrom-Json
$blobCount = if ($blobList) { $blobList.Count } else { 0 }

if ($blobCount -gt 0) {
    Write-Host "[OK] Dataset files uploaded ($blobCount files)" -ForegroundColor Green
}
else {
    Write-Host "[FIX] Uploading dataset files..." -ForegroundColor Yellow
    
    $datasetPath = Join-Path $PSScriptRoot "dataset"
    $files = Get-ChildItem -Path $datasetPath -File
    
    foreach ($file in $files) {
        Write-Host "  Uploading: $($file.Name)" -ForegroundColor Gray
        
        $result = az storage blob upload --account-name $config.storageAccountName --container-name knowledge-base --name $file.Name --file $file.FullName --auth-mode login --overwrite --output json 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "    [WARNING] Failed to upload $($file.Name)" -ForegroundColor Yellow
        }
    }
    
    $blobList = az storage blob list --account-name $config.storageAccountName --container-name knowledge-base --auth-mode login --output json 2>$null | ConvertFrom-Json
    $blobCount = if ($blobList) { $blobList.Count } else { 0 }
    
    Write-Host "[OK] Uploaded $blobCount files" -ForegroundColor Green
}

# ============================================================================
# Issue 4: Search Index Population
# ============================================================================
Write-Host "`n>> Checking search index..." -ForegroundColor Yellow

# Activate venv
$VenvActivate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $VenvActivate) {
    & $VenvActivate
}

# Check document count
$indexInfo = az search index show --service-name $config.aiSearchServiceName --name $config.searchIndexName --resource-group $config.resourceGroupName --output json 2>$null | ConvertFrom-Json
$docCount = if ($indexInfo.statistics) { $indexInfo.statistics.documentCount } else { 0 }

if ($docCount -gt 0) {
    Write-Host "[OK] Search index has $docCount documents" -ForegroundColor Green
}
else {
    Write-Host "[FIX] Indexing documents..." -ForegroundColor Yellow
    
    Push-Location infrastructure
    python index_documents.py
    Pop-Location
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Documents indexed" -ForegroundColor Green
    }
    else {
        Write-Host "[WARNING] Document indexing completed with warnings" -ForegroundColor Yellow
    }
}

# ============================================================================
# Issue 5: Verify Deployments
# ============================================================================
Write-Host "`n>> Verifying deployments..." -ForegroundColor Yellow

# Check backend
Write-Host "  Testing backend API..." -ForegroundColor Gray
$backendUrl = "https://$($config.functionAppName).azurewebsites.net/api/health"
try {
    $response = Invoke-WebRequest -Uri $backendUrl -Method Get -TimeoutSec 10 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Backend is responding" -ForegroundColor Green
    }
}
catch {
    Write-Host "[WARNING] Backend not responding yet (may still be starting up)" -ForegroundColor Yellow
}

# Check frontend
Write-Host "  Testing frontend..." -ForegroundColor Gray
$swa = az staticwebapp show --name $config.staticWebAppName --resource-group $config.resourceGroupName --output json 2>$null | ConvertFrom-Json
$frontendUrl = if ($swa) { $swa.defaultHostname } else { $null }

if ($frontendUrl) {
    Write-Host "[OK] Frontend: https://$frontendUrl" -ForegroundColor Green
}
else {
    Write-Host "[WARNING] Frontend URL not available" -ForegroundColor Yellow
}

# ============================================================================
# Summary
# ============================================================================
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "Fix Complete!" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan

Write-Host "`nApplication URLs:" -ForegroundColor Yellow
Write-Host "  Backend:  $backendUrl" -ForegroundColor White
if ($frontendUrl) {
    Write-Host "  Frontend: https://$frontendUrl" -ForegroundColor White
}

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Test backend: curl $backendUrl" -ForegroundColor Gray
if ($frontendUrl) {
    Write-Host "  2. Open frontend: https://$frontendUrl" -ForegroundColor Gray
}
Write-Host "  3. Monitor logs in Azure Portal" -ForegroundColor Gray

Write-Host ""
