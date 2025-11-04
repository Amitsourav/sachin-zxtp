@echo off
REM Script to run the trading bot web interface locally on Windows

echo ======================================================
echo 🚀 Starting 9:15 Trading Bot Web Interface...
echo ======================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Set environment variables for development
set FLASK_APP=app.py
set FLASK_ENV=development
set SECRET_KEY=dev-secret-key-change-in-production

echo.
echo ✅ Setup complete!
echo ======================================================
echo 🌐 Starting web server...
echo.
echo 📱 Access the dashboard at:
echo    http://localhost:5000
echo.
echo 🔐 Demo Login Credentials:
echo    Username: demo
echo    Password: demo123
echo.
echo Press Ctrl+C to stop the server
echo ======================================================
echo.

REM Run the Flask application
python app.py

pause