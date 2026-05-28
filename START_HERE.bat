@echo off
cd /d "%~dp0\streamlit_app"
title Soop Starter

echo.
echo ========================================================
echo   Soop Starter Dashboard
echo ========================================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
python -c "import streamlit, folium, plotly, lightgbm, networkx" 2>nul
if errorlevel 1 (
    echo.
    echo First run - installing dependencies. Takes 2-3 minutes...
    echo.
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Dependency install failed.
        pause
        exit /b 1
    )
)

echo [2/3] Checking GEMINI_API_KEY...
if "%GEMINI_API_KEY%"=="" (
    if exist ..\.env (
        echo Loading from .env file...
        for /f "tokens=2 delims==" %%a in ('findstr "GEMINI_API_KEY" ..\.env') do set GEMINI_API_KEY=%%a
    ) else (
        echo [WARN] GEMINI_API_KEY not set. AI features disabled.
        echo Setup: copy ..\.env.example ..\.env  then edit
    )
)

echo [3/3] Starting Streamlit...
echo.
echo ========================================================
echo   Browser auto-opens: http://localhost:8501
echo   Stop: Ctrl+C
echo ========================================================
echo.

python -m streamlit run soop_app.py

pause
