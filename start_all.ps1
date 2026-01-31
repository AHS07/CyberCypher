# Shadow-SHERPA Hybrid Start Script
# Starts all 4 servers required for the full pipeline

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Shadow-SHERPA Hybrid - Development Startup    " -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = $PSScriptRoot

# Check if Ollama is running
Write-Host "[1/5] Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
    Write-Host "  ✓ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ollama not running! Starting ollama serve..." -ForegroundColor Red
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
    Start-Sleep -Seconds 3
}

# Start Legacy Mock Server (port 8001)
Write-Host "[2/5] Starting Legacy Mock Server (port 8001)..." -ForegroundColor Yellow
$legacyProcess = Start-Process -FilePath "python" -ArgumentList "server_legacy.py" -WorkingDirectory "$ProjectRoot\engine" -PassThru -WindowStyle Minimized
Write-Host "  ✓ Legacy server started (PID: $($legacyProcess.Id))" -ForegroundColor Green

# Start Headless Mock Server (port 8002)
Write-Host "[3/5] Starting Headless Mock Server (port 8002)..." -ForegroundColor Yellow
$headlessProcess = Start-Process -FilePath "python" -ArgumentList "server_headless.py" -WorkingDirectory "$ProjectRoot\engine" -PassThru -WindowStyle Minimized
Write-Host "  ✓ Headless server started (PID: $($headlessProcess.Id))" -ForegroundColor Green

# Start Orchestrator (port 8000)
Write-Host "[4/5] Starting Orchestrator (port 8000)..." -ForegroundColor Yellow
$orchestratorProcess = Start-Process -FilePath "cmd" -ArgumentList "/c", "cd /d $ProjectRoot\orchestrator && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -PassThru -WindowStyle Minimized
Write-Host "  ✓ Orchestrator starting (PID: $($orchestratorProcess.Id))" -ForegroundColor Green

# Start Dashboard (port 3000)
Write-Host "[5/5] Starting Dashboard (port 3000)..." -ForegroundColor Yellow
$dashboardProcess = Start-Process -FilePath "cmd" -ArgumentList "/c", "cd /d $ProjectRoot\dashboard && npm run dev" -PassThru -WindowStyle Minimized
Write-Host "  ✓ Dashboard starting (PID: $($dashboardProcess.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  All servers started successfully!              " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor White
Write-Host "  • Legacy Mock:    http://localhost:8001" -ForegroundColor Gray
Write-Host "  • Headless Mock:  http://localhost:8002" -ForegroundColor Gray
Write-Host "  • Orchestrator:   http://localhost:8000" -ForegroundColor Gray
Write-Host "  • Dashboard:      http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "To run a shadow replay test:" -ForegroundColor White
Write-Host '  cd engine && python shadow_engine.py --payload ''{"item": "laptop", "price": 50000}''' -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to stop all servers..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup
Write-Host ""
Write-Host "Stopping servers..." -ForegroundColor Yellow
Stop-Process -Id $legacyProcess.Id -ErrorAction SilentlyContinue
Stop-Process -Id $headlessProcess.Id -ErrorAction SilentlyContinue
Stop-Process -Id $orchestratorProcess.Id -ErrorAction SilentlyContinue
Stop-Process -Id $dashboardProcess.Id -ErrorAction SilentlyContinue
Write-Host "All servers stopped." -ForegroundColor Green
