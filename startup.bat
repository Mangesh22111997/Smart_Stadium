@echo off
REM Smart Stadium System - Automated Startup Script (Windows)
REM Starts both backend and frontend services

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║       Smart Stadium System - Automated Startup                 ║
echo ║       Backend + Frontend Services                              ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Set colors
for /F %%A in ('echo prompt $H ^| cmd') do set "BS=%%A"

REM Get project directory
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo [1/3] Checking Python environment...
if exist ".venv\Scripts\activate.bat" (
    echo ✓ Virtual environment found
    call .venv\Scripts\activate.bat
) else (
    echo ✗ Virtual environment not found
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt 2>nul
)

echo.
echo [2/3] Starting Backend Server (Port 8000)...
echo Starting: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
start /B cmd /c "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

REM Wait for backend to start
echo ⏳ Waiting for backend to initialize (5 seconds)...
timeout /t 5 /nobreak

echo.
echo [3/3] Starting Frontend (Streamlit on Port 8501)...
echo Starting: streamlit run frontend.py
start cmd /c "streamlit run frontend.py"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                 Services Starting...                           ║
echo ║                                                                ║
echo ║  Backend:  http://127.0.0.1:8000                             ║
echo ║  Frontend: http://127.0.0.1:8501                             ║
echo ║                                                                ║
echo ║  Press Ctrl+C to stop services                               ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Keep this window open
pause
