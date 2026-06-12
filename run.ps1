# Quick Run - Start Backend & Frontend Together
# Windows PowerShell

Write-Host "🚀 Starting SocialLead FB Groups..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Start Backend in new window
Write-Host "Starting Backend (port 3001)..." -ForegroundColor Yellow
$backendCmd = @"
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

Start-Sleep -Seconds 3

# Start Frontend in new window
Write-Host "Starting Frontend (port 3000)..." -ForegroundColor Yellow
$frontendCmd = @"
cd frontend
npm run dev
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

Write-Host ""
Write-Host "✅ Both services started!" -ForegroundColor Green
Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:   http://localhost:3001" -ForegroundColor Cyan
Write-Host "   API Docs:  http://localhost:3001/docs" -ForegroundColor Cyan
