@echo off
REM START_CLEAN.bat - Clean startup with verification
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ================================================
echo          CLEAN SERVICE STARTUP
echo ================================================
echo.

echo [1/7] Killing any existing processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM streamlit.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/7] Clearing old logs...
if exist "logs" (
    del /Q logs\*.log 2>nul
    echo     Logs cleared
)

echo [3/7] Clearing Streamlit cache...
if exist "%USERPROFILE%\.streamlit\cache" (
    rmdir /S /Q "%USERPROFILE%\.streamlit\cache" 2>nul
)
if exist "%APPDATA%\streamlit\cache" (
    rmdir /S /Q "%APPDATA%\streamlit\cache" 2>nul
)
echo     Streamlit cache cleared

echo [4/7] Creating fresh logs directory...
if not exist "logs" mkdir logs
echo     Logs directory ready

echo [5/7] Starting FastAPI on port 8000...
start /B "" poetry run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 > logs\api.log 2>&1
echo     API starting (port 8000)...

timeout /t 6 /nobreak >nul

echo [6/7] Starting Streamlit UI on port 8501...
start /B "" poetry run streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0 --logger.level=error > logs\ui.log 2>&1
echo     UI starting (port 8501)...

timeout /t 4 /nobreak >nul

echo [7/7] Verifying services...
echo.

REM Check if ports are listening
netstat -ano | findstr ":8000 " >nul && (
    echo     ✓ API listening on port 8000
) || (
    echo     ✗ API NOT listening on port 8000
    echo       Check: logs\api.log
)

netstat -ano | findstr ":8501 " >nul && (
    echo     ✓ UI listening on port 8501
) || (
    echo     ✗ UI NOT listening on port 8501
    echo       Check: logs\ui.log
)

echo.
echo ================================================
echo          STARTUP COMPLETE
echo ================================================
echo.
echo Access:
echo   UI:        http://localhost:8501
echo   API:       http://localhost:8000/docs
echo   Health:    http://localhost:8000/health
echo.
echo Logs:
echo   API:  %CD%\logs\api.log
echo   UI:   %CD%\logs\ui.log
echo.
echo Stop services:
echo   taskkill /F /IM python.exe
echo   taskkill /F /IM streamlit.exe
echo.
pause
