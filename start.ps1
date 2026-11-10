Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Launching Task Manager Application   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Start Backend API in a separate terminal window
Write-Host "[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; .\venv\Scripts\activate; Write-Host 'Backend running at http://127.0.0.1:8000 (Docs at /docs)' -ForegroundColor Green; uvicorn app.main:app --reload --port 8000"

# Start Frontend Dev Server in a separate terminal window
Write-Host "[2/2] Starting React + Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; Write-Host 'Frontend dev server running at http://localhost:5173' -ForegroundColor Green; npm run dev"

# Wait for servers to initialize and open the browser
Start-Sleep -Seconds 3
Write-Host "Opening web application in default browser..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host "Both servers are running in dedicated terminal windows." -ForegroundColor Cyan
