@echo off
echo ========================================
echo AI Lead Finder - Windows Setup Script
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo [1/5] Python found!
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created!
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed!
echo.

REM Setup .env file
echo [5/5] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo .env file created from template
    echo.
    echo ========================================
    echo IMPORTANT: Edit .env file with your API keys!
    echo ========================================
    echo.
    echo Required API keys:
    echo - BRIGHT_DATA_API_KEY
    echo - WEB_UNLOCKER_PROXY
    echo - GEMINI_API_KEY
    echo.
) else (
    echo .env file already exists
    echo.
)

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: venv\Scripts\activate
echo 3. Run: streamlit run app.py
echo.
echo See QUICKSTART.md for detailed instructions
echo.
pause
