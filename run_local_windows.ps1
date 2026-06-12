Write-Host "=== SocialLead FB Groups Fullstack - Windows Browser Mode ===" -ForegroundColor Cyan

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "`n[1/3] Starting PostgreSQL and frontend in Docker..." -ForegroundColor Yellow
docker compose up -d db
if ($LASTEXITCODE -ne 0) {
    throw 'Could not start PostgreSQL with Docker.'
}
docker compose up -d --no-deps frontend
if ($LASTEXITCODE -ne 0) {
    throw 'Could not start frontend with Docker.'
}

Write-Host "`n[2/3] Starting backend directly on Windows..." -ForegroundColor Yellow
& (Join-Path $root 'start_windows_backend.ps1')

Write-Host "`n[3/3] Done" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend docs: http://localhost:3001/docs"
Write-Host "The login button can now open Chrome directly on Windows."
