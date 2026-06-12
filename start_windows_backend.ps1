param(
    [int]$Port = 3001,
    [switch]$KeepDockerBackend
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root 'backend'
$python = Join-Path $backend '.venv\Scripts\python.exe'
$envFile = Join-Path $root '.env'
$pidFile = Join-Path $root '.tmp\windows-backend.pid'
$stdoutLog = Join-Path $root '.tmp\windows-backend.out.log'
$stderrLog = Join-Path $root '.tmp\windows-backend.err.log'

if (!(Test-Path $python)) {
    throw "Python virtualenv not found: $python. Run setup_and_run.ps1 first."
}

if (!(Test-Path $envFile)) {
    throw "Configuration file not found: $envFile"
}

Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if (!$line -or $line.StartsWith('#') -or !$line.Contains('=')) {
        return
    }

    $name, $value = $line.Split('=', 2)
    [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim(), 'Process')
}

if ($env:DATABASE_URL) {
    $env:DATABASE_URL = $env:DATABASE_URL -replace '@db:', '@127.0.0.1:'
}

$env:BACKEND_RUNTIME = 'windows'
$env:PYTHONPATH = $backend

Push-Location $root
try {
    docker compose up -d db | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not start PostgreSQL with Docker.'
    }

    $databaseDeadline = (Get-Date).AddSeconds(60)
    do {
        $databaseStatus = docker inspect --format '{{.State.Health.Status}}' sociallead_fb_db 2>$null
        if ($databaseStatus -eq 'healthy') {
            break
        }
        Start-Sleep -Seconds 1
    } while ((Get-Date) -lt $databaseDeadline)

    if ($databaseStatus -ne 'healthy') {
        throw 'PostgreSQL did not become healthy within 60 seconds.'
    }

    if (!$KeepDockerBackend) {
        docker compose stop backend | Out-Null
    }

    docker compose up -d --no-deps frontend | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not start frontend with Docker.'
    }
} finally {
    Pop-Location
}

if (Test-Path $pidFile) {
    $existingPid = Get-Content $pidFile -ErrorAction SilentlyContinue
    if ($existingPid -and (Get-Process -Id $existingPid -ErrorAction SilentlyContinue)) {
        Write-Host "Windows backend is already running with PID $existingPid." -ForegroundColor Yellow
        exit 0
    }
}

New-Item -ItemType Directory -Force (Split-Path -Parent $pidFile) | Out-Null

$process = Start-Process `
    -FilePath $python `
    -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', "$Port" `
    -WorkingDirectory $backend `
    -WindowStyle Hidden `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru

Set-Content -LiteralPath $pidFile -Value $process.Id

$deadline = (Get-Date).AddSeconds(30)
do {
    Start-Sleep -Milliseconds 500
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/v1/health" -TimeoutSec 2
        if ($health.ok) {
            Write-Host "Windows backend is running at http://localhost:$Port (PID $($process.Id))." -ForegroundColor Green
            exit 0
        }
    } catch {
        if ($process.HasExited) {
            $details = Get-Content $stderrLog -Raw -ErrorAction SilentlyContinue
            throw "Windows backend stopped during startup.`n$details"
        }
    }
} while ((Get-Date) -lt $deadline)

throw "Windows backend was not ready within 30 seconds. See: $stderrLog"
