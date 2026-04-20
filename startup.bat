@echo off
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo      Smart Stadium System — Local Dev Startup
echo ==========================================
echo.

cd /d "%~dp0"

REM —— Virtual environment ——
if exist ".venv\Scripts\activate.bat" (
    echo [OK] Virtual environment found
    call .venv\Scripts\activate.bat
) else (
    echo [..] Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

REM —— Install dependencies ——
pip install -q --upgrade pip
pip install -q -r requirements.backend.txt
pip install -q -r requirements.frontend.txt

REM —— Check .env ——
if not exist ".env" (
    echo [ERROR] .env file not found. Copy .env.example and fill in your values.
    pause
    exit /b 1
)
echo [OK] .env file found

REM —— Start backend ——
echo.
echo [2/3] Starting Backend on http://localhost:8000 ...
start "Stadium Backend" cmd /k "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 5 /nobreak > nul
echo [OK] Backend window opened

REM —— Start frontend ——
echo.
echo [3/3] Starting Frontend on http://localhost:8501 ...
set API_BASE_URL=http://localhost:8000
start "Stadium Frontend" cmd /k "streamlit run streamlit_app/app.py --server.port 8501 --server.address 127.0.0.1"

echo.
echo ------------------------------------------
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo   Frontend : http://localhost:8501
echo ------------------------------------------
echo.
echo Both services started in separate windows.
pause
