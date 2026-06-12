# Complete Setup & Run - SocialLead FB Groups Scraper
# For Windows PowerShell

$ErrorActionPreference = "Continue"

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🚀 SocialLead Facebook Groups Scraper - Windows Setup            ║" -ForegroundColor Cyan
Write-Host "║      Version 2.0.0                                                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Get script location
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green

# Check Node.js
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green

# ==================== BACKEND SETUP ====================
Write-Host "`n[1/3] 🐍 Setting up Backend (Python)..." -ForegroundColor Yellow

$backendDir = "$scriptDir\backend"
$venvDir = "$backendDir\.venv"
$envFile = "$backendDir\.env"

# Check if venv exists
if (!(Test-Path $venvDir)) {
    Write-Host "  Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create venv" -ForegroundColor Red
        exit 1
    }
}

# Activate venv
Write-Host "  Activating virtual environment..." -ForegroundColor Cyan
& "$venvDir\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Could not activate venv" -ForegroundColor Yellow
}

# Install dependencies
Write-Host "  Installing Python dependencies..." -ForegroundColor Cyan
pip install -r "$backendDir\requirements.txt" --quiet 2>&1 | Where-Object { $_ -match "error|ERROR" }
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some errors during pip install (may be non-critical)" -ForegroundColor Yellow
}

# Install Playwright browsers
Write-Host "  Installing Playwright browsers..." -ForegroundColor Cyan
python -m playwright install chromium --with-deps 2>&1 | Select-String -Pattern "installed|Downloading" | Select-Object -First 5
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Playwright setup complete" -ForegroundColor Green
}

# Copy .env if not exists
if (!(Test-Path $envFile)) {
    Write-Host "  Copying .env configuration..." -ForegroundColor Cyan
    Copy-Item "$backendDir\.env.example" $envFile -ErrorAction SilentlyContinue
    if (Test-Path "$scriptDir\.env") {
        Copy-Item "$scriptDir\.env" $envFile
    }
}
Write-Host "✅ Backend ready" -ForegroundColor Green

# ==================== FRONTEND SETUP ====================
Write-Host "`n[2/3] 📦 Setting up Frontend (Node.js)..." -ForegroundColor Yellow

$frontendDir = "$scriptDir\frontend"
$nodeModules = "$frontendDir\node_modules"

if (!(Test-Path $nodeModules)) {
    Write-Host "  Installing npm dependencies..." -ForegroundColor Cyan
    Set-Location $frontendDir
    npm install --legacy-peer-deps --silent 2>&1 | Where-Object { $_ -match "error|ERROR" }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Some errors during npm install" -ForegroundColor Yellow
    }
    Set-Location $scriptDir
}

# Create .env for frontend if not exists
$frontendEnv = "$frontendDir\.env"
if (!(Test-Path $frontendEnv)) {
    Write-Host "  Creating frontend .env..." -ForegroundColor Cyan
    "VITE_API_BASE_URL=http://localhost:3001" | Out-File -Encoding utf8 $frontendEnv
}

Write-Host "✅ Frontend ready" -ForegroundColor Green

# ==================== DATABASE SETUP ====================
Write-Host "`n[3/3] 💾 Initializing Database..." -ForegroundColor Yellow

Set-Location $backendDir

# Initialize database
Write-Host "  Creating SQLite database..." -ForegroundColor Cyan
python -c "from app.db.session import init_db; init_db(); print('✅ Database initialized')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Database initialization skipped or already exists" -ForegroundColor Yellow
}

Write-Host "✅ Database ready" -ForegroundColor Green

# ==================== STARTUP ====================
Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                      🎉 Setup Complete!                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. 🔐 Login Facebook (run in new terminal):"
Write-Host "     cd backend" -ForegroundColor Gray
Write-Host "     .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "     python scripts\login_cdp_playwright.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. 🚀 Start Backend (run in new terminal):"
Write-Host "     cd backend" -ForegroundColor Gray
Write-Host "     .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "     uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. 🌐 Start Frontend (run in new terminal):"
Write-Host "     cd frontend" -ForegroundColor Gray
Write-Host "     npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. 🔍 Access Application:"
Write-Host "     Frontend:  http://localhost:3000" -ForegroundColor Green
Write-Host "     Backend:   http://localhost:3001" -ForegroundColor Green
Write-Host "     API Docs:  http://localhost:3001/docs" -ForegroundColor Green
Write-Host ""
Write-Host "📖 More info: Open QUICK_START.md" -ForegroundColor Cyan
Write-Host ""

# Offer to start backend
Write-Host "Would you like to start the Backend now? (y/n)" -ForegroundColor Cyan
$response = Read-Host
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "Starting Backend on http://localhost:3001..." -ForegroundColor Green
    Set-Location "$scriptDir\backend"
    uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
} else {
    Write-Host "Setup complete! Run the steps above to start." -ForegroundColor Green
}
