@echo off
REM START_SERVICES_FIXED.bat - Start API (8000) and UI (8501) with proper configuration
REM Fixes: Ensures correct ports, clears Streamlit cache, uses correct config

setlocal enabledelayedexpansion

REM Get the project directory
cd /d "%~dp0"

echo ========================================
echo Starting Sports_See Services (FIXED)
echo ========================================
echo.
echo API Port:  8000 (FastAPI standard)
echo UI Port:   8501 (Streamlit standard)
echo.

REM Kill any existing processes on these ports
echo [Step 1/5] Checking for stray processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501"') do (
    echo Killing process on port 8501 (PID: %%a)
    taskkill /PID %%a /F 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8500"') do (
    echo Killing process on port 8500 (PID: %%a)
    taskkill /PID %%a /F 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    echo Killing process on port 8000 (PID: %%a)
    taskkill /PID %%a /F 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8800"') do (
    echo Killing process on port 8800 (PID: %%a)
    taskkill /PID %%a /F 2>nul
)

REM Clear Streamlit cache to force reload with correct config
echo [Step 2/5] Clearing Streamlit cache...
if exist "%USERPROFILE%\.streamlit" (
    rmdir /S /Q "%USERPROFILE%\.streamlit\cache" 2>nul
    echo Streamlit cache cleared
)

REM Create logs directory if it doesn't exist
echo [Step 3/5] Creating logs directory...
if not exist "logs" mkdir logs
echo Logs directory ready

REM Start API on port 8000 (background, no window)
echo [Step 4/5] Starting FastAPI on port 8000...
start /B "" poetry run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 > logs\api.log 2>&1
echo API starting...

REM Wait for API to fully start
timeout /t 5 /nobreak >nul 2>&1

REM Start UI on port 8501 (background, no window)
echo [Step 5/5] Starting Streamlit UI on port 8501...
start /B "" poetry run streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0 --logger.level=error > logs\ui.log 2>&1
echo UI starting...

timeout /t 3 /nobreak >nul 2>&1

echo.
echo ========================================
echo Services Started Successfully
echo ========================================
echo.
echo Access URLs:
echo   UI:        http://localhost:8501
echo   API Docs:  http://localhost:8000/docs
echo   API Health: http://localhost:8000/health
echo.
echo Log Files:
echo   API Log:   logs\api.log
echo   UI Log:    logs\ui.log
echo.
echo To stop services:
echo   taskkill /F /IM python.exe
echo   taskkill /F /IM streamlit.exe
echo.
echo Services running in background!
echo.
pause
