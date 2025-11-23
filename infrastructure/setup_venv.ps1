# Setup Virtual Environment for Infrastructure Scripts
# This script creates a Python virtual environment and installs dependencies

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Setting up Python Virtual Environment" -ForegroundColor Cyan
Write-Host "=" * 60

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path (Split-Path -Parent $ScriptDir) ".venv"

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Python not found. Please install Python 3.10 or higher." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $VenvPath)) {
    Write-Host "`nCreating virtual environment at $VenvPath..." -ForegroundColor Cyan
    python -m venv $VenvPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "`n✓ Virtual environment already exists at $VenvPath" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Cyan
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

if (Test-Path $ActivateScript) {
    & $ActivateScript
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
}
else {
    Write-Host "✗ Activation script not found" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`nInstalling Python dependencies..." -ForegroundColor Cyan
$RequirementsPath = Join-Path $ScriptDir "requirements.txt"

if (Test-Path $RequirementsPath) {
    python -m pip install --upgrade pip
    pip install -r $RequirementsPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✗ requirements.txt not found at $RequirementsPath" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "`nVirtual environment is now active and ready to use." -ForegroundColor White
Write-Host "`nTo activate the virtual environment in future sessions:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "`nTo run the indexing pipeline:" -ForegroundColor Yellow
Write-Host "  python .\infrastructure\create_search_index.py" -ForegroundColor Gray
Write-Host "  python .\infrastructure\index_documents.py" -ForegroundColor Gray
