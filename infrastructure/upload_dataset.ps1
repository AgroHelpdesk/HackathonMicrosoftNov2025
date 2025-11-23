<#
.SYNOPSIS
    Upload Dataset to Azure Blob Storage

.DESCRIPTION
    This script uploads all files from the dataset folder to Azure Blob Storage,
    organizing them by type (PDFs in documents/, CSVs in data/).

.PREREQUISITES
    - Azure CLI installed and logged in (az login)
    - Azure resources deployed (run deploy_resources.ps1 first)

.USAGE
    .\infrastructure\upload_dataset.ps1
#>

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigPath = Join-Path $ScriptDir "config.json"
$DatasetDir = Join-Path (Split-Path -Parent $ScriptDir) "dataset"
$ContainerName = "knowledge-base"

function Get-BlobPrefix {
    param (
        [string]$FileName
    )
    
    $extension = [System.IO.Path]::GetExtension($FileName).ToLower()
    
    switch ($extension) {
        ".pdf" { return "documents/" }
        ".csv" { return "data/" }
        default { return "other/" }
    }
}

function Send-Dataset {
    # Load configuration
    Write-Host "Loading configuration..." -ForegroundColor Cyan
    
    if (-not (Test-Path $ConfigPath)) {
        Write-Host "Error: Configuration file not found at $ConfigPath" -ForegroundColor Red
        Write-Host "Please run deploy_resources.ps1 first to create the configuration." -ForegroundColor Yellow
        exit 1
    }
    
    $config = Get-Content $ConfigPath | ConvertFrom-Json
    $storageAccountName = $config.storageAccountName
    
    # Create container if it doesn't exist
    Write-Host "Ensuring container '$ContainerName' exists..." -ForegroundColor Cyan
    
    $containerExists = az storage container exists `
        --account-name $storageAccountName `
        --name $ContainerName `
        --auth-mode login `
        --output json | ConvertFrom-Json
    
    if (-not $containerExists.exists) {
        Write-Host "Creating container '$ContainerName'..." -ForegroundColor Yellow
        az storage container create `
            --account-name $storageAccountName `
            --name $ContainerName `
            --auth-mode login `
            --output none
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Container '$ContainerName' created" -ForegroundColor Green
        }
        else {
            Write-Host "✗ Failed to create container" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "✓ Container '$ContainerName' already exists" -ForegroundColor Green
    }
    
    # Get list of files to upload
    if (-not (Test-Path $DatasetDir)) {
        Write-Host "Error: Dataset directory not found at $DatasetDir" -ForegroundColor Red
        exit 1
    }
    
    $files = Get-ChildItem -Path $DatasetDir -File
    
    if ($files.Count -eq 0) {
        Write-Host "No files found in $DatasetDir" -ForegroundColor Yellow
        return
    }
    
    Write-Host "`nFound $($files.Count) files to upload:" -ForegroundColor Cyan
    foreach ($file in $files) {
        $sizeMB = [math]::Round($file.Length / 1MB, 2)
        Write-Host "  - $($file.Name) ($sizeMB MB)" -ForegroundColor Gray
    }
    
    # Upload files
    Write-Host "`nUploading files..." -ForegroundColor Cyan
    $uploadedCount = 0
    $fileIndex = 0
    
    foreach ($file in $files) {
        $fileIndex++
        $prefix = Get-BlobPrefix -FileName $file.Name
        $blobName = "$prefix$($file.Name)"
        
        Write-Host "`n[$fileIndex/$($files.Count)] Uploading $($file.Name)..." -ForegroundColor Cyan
        Write-Host "  → Destination: $blobName" -ForegroundColor Gray
        
        try {
            az storage blob upload `
                --account-name $storageAccountName `
                --container-name $ContainerName `
                --name $blobName `
                --file $file.FullName `
                --auth-mode login `
                --overwrite `
                --output none
            
            if ($LASTEXITCODE -eq 0) {
                $blobUrl = "https://$storageAccountName.blob.core.windows.net/$ContainerName/$blobName"
                Write-Host "  ✓ Uploaded successfully" -ForegroundColor Green
                Write-Host "  URL: $blobUrl" -ForegroundColor Gray
                $uploadedCount++
            }
            else {
                Write-Host "  ✗ Error uploading $($file.Name)" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "  ✗ Error uploading $($file.Name): $_" -ForegroundColor Red
        }
    }
    
    # Summary
    Write-Host "`n$('=' * 60)" -ForegroundColor Cyan
    Write-Host "Upload Complete!" -ForegroundColor Green
    Write-Host "Successfully uploaded $uploadedCount/$($files.Count) files" -ForegroundColor White
    Write-Host "Container: $ContainerName" -ForegroundColor White
    Write-Host "Storage Account: $storageAccountName" -ForegroundColor White
    Write-Host "$('=' * 60)" -ForegroundColor Cyan
    
    # Verification command
    Write-Host "`nTo verify uploads, run:" -ForegroundColor Yellow
    Write-Host "az storage blob list --account-name $storageAccountName --container-name $ContainerName --output table --auth-mode login" -ForegroundColor Gray
}

# Main execution
try {
    Send-Dataset
}
catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    Write-Host "`nMake sure you are logged in to Azure CLI:" -ForegroundColor Yellow
    Write-Host "  az login" -ForegroundColor Gray
    exit 1
}
