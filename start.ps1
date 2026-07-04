# Supply Chain Dashboard - PowerShell Launcher
# Double-click this file OR right-click > "Run with PowerShell"

$PYTHON = "C:\Users\Sanika\AppData\Local\Programs\Python\Python313\python.exe"
$PROJECT = "C:\Users\Sanika\Downloads\supply_chain_project\supply_chain"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Supply Chain Dashboard - Starting Up" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PROJECT

Write-Host "[1/3] Installing required packages..." -ForegroundColor Yellow
& $PYTHON -m pip install flask pandas numpy scikit-learn xgboost plotly --quiet
Write-Host "  Packages ready!" -ForegroundColor Green

Write-Host "[2/3] Checking CSV data files..." -ForegroundColor Yellow
if (Test-Path "data\List of Orders.csv") {
    Write-Host "  CSV files found. OK." -ForegroundColor Green
} else {
    Write-Host "  Generating sample data..." -ForegroundColor Yellow
    & $PYTHON "data\generate_data.py"
}

Write-Host "[3/3] Starting Flask server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Dashboard URL --> http://127.0.0.1:5000" -ForegroundColor Green
Write-Host ""
Write-Host "  Press Ctrl+C to stop the server." -ForegroundColor Gray
Write-Host "============================================" -ForegroundColor Cyan

$env:FLASK_APP = "app.py"
& $PYTHON -m flask run --port 5000 --host 0.0.0.0
