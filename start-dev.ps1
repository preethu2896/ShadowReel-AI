# ShadowReel AI - Quick Start
# Run this script from the repo root on Windows (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ShadowReel AI - Development Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# -- Step 1: Start Docker services (Postgres + Redis) --
Write-Host "[1/4] Starting PostgreSQL + Redis via Docker..." -ForegroundColor Yellow
docker compose up postgres redis -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker failed. Make sure Docker Desktop is running." -ForegroundColor Red
    exit 1
}

Write-Host "Waiting for services to be healthy..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# -- Step 2: Start FastAPI backend --
Write-Host "[2/4] Starting FastAPI backend on :8000..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "$using:PSScriptRoot\backend"
    & .\venv\Scripts\Activate.ps1
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

Start-Sleep -Seconds 3

# -- Step 3: Start Celery worker --
Write-Host "[3/4] Starting Celery worker..." -ForegroundColor Yellow
$celeryJob = Start-Job -ScriptBlock {
    Set-Location "$using:PSScriptRoot\backend"
    & .\venv\Scripts\Activate.ps1
    celery -A workers.celery_app worker --loglevel=info --concurrency=2 -Q generation --pool=solo
}

# -- Step 4: Start Next.js frontend --
Write-Host "[4/4] Starting Next.js frontend on :3000..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "$using:PSScriptRoot\frontend"
    npm run dev
}

Write-Host ""
Write-Host "All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend  -> http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend   -> http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs  -> http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  ComfyUI   -> http://localhost:8188  (start manually)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop all services."

try {
    Wait-Job $backendJob, $celeryJob, $frontendJob
} finally {
    Stop-Job $backendJob, $celeryJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $celeryJob, $frontendJob -ErrorAction SilentlyContinue
    Write-Host "Services stopped." -ForegroundColor Gray
}
