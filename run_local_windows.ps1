Write-Host "=== SocialLead FB Groups Fullstack - Local Windows Setup ===" -ForegroundColor Cyan
Copy-Item .env.example .env -ErrorAction SilentlyContinue

Write-Host "\n[1/3] Backend setup" -ForegroundColor Yellow
Set-Location backend
if (!(Test-Path .env)) { Copy-Item ..\.env .env }
if (!(Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload"
Set-Location ..

Write-Host "\n[2/3] Frontend setup" -ForegroundColor Yellow
Set-Location frontend
if (!(Test-Path .env)) { "VITE_API_BASE_URL=http://localhost:3001" | Out-File -Encoding utf8 .env }
npm install
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev"
Set-Location ..

Write-Host "\n[3/3] Done" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend docs: http://localhost:3001/docs"
Write-Host "Login FB profile: cd backend; .\.venv\Scripts\activate; python scripts\login_cdp_playwright.py"
