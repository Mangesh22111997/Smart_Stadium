@echo off
REM Smart Stadium System - Streamlit Startup Script

echo.
echo ============================================
echo  🏟️ Smart Stadium - Streamlit Portal
echo ============================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found!
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .\.venv\Scripts\activate.bat

REM Install dependencies
echo Installing/updating Streamlit dependencies...
pip install -r streamlit_app\requirements.txt --quiet

REM Start Streamlit
echo.
echo ✅ Starting Streamlit application...
echo.
echo 🌐 Open your browser to: http://localhost:8501
echo.
echo ⚠️  Make sure FastAPI backend is running on http://localhost:8000
echo    Run in another terminal: python -m uvicorn app.main:app --reload
echo.

cd streamlit_app
streamlit run app.py

pause
