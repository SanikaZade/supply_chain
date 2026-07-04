@echo off
echo ============================================
echo   Supply Chain Dashboard - Starting Up
echo ============================================
echo.

cd /d "%~dp0"

set PYTHON="C:\Users\Sanika\AppData\Local\Programs\Python\Python313\python.exe"

echo [1/3] Installing required packages...
%PYTHON% -m pip install --upgrade pip --quiet
%PYTHON% -m pip install flask pandas numpy scikit-learn xgboost plotly --quiet

echo [2/3] Checking for CSV data files...
if not exist "data\List_of_Orders.csv" (
    echo Generating sample data...
    %PYTHON% data\generate_data.py
) else (
    echo CSV files found. OK.
)

echo [3/3] Starting Flask server...
echo.
echo  Dashboard will be available at:
echo  --^> http://127.0.0.1:5000
echo.
echo  Press Ctrl+C to stop the server.
echo ============================================

set FLASK_APP=app.py
%PYTHON% -m flask run --port 5000 --host 0.0.0.0

pause 
