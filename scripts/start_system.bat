@echo off
REM AI-Powered Real Estate System - Quick Start Script (Windows)
REM This script helps you start all services quickly on Windows

echo 🚀 Starting AI-Powered Real Estate System...
echo ================================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not available. Please install Python 3.11+.
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your configuration before proceeding.
    echo    Required: BASEROW_TOKEN, BASEROW_APPLICATION_ID
    exit /b 1
)

REM Create Python virtual environment if it doesn't exist
if not exist "venv" (
    echo 🐍 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Start services with Docker Compose
echo 🐳 Starting services with Docker Compose...
docker-compose up -d

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak

REM Test services
echo 🧪 Testing service health...
python scripts\test_integration.py

echo.
echo ✅ System startup complete!
echo.
echo 🌐 Access Points:
echo    - Web Dashboard: http://localhost:3000
echo    - n8n Workflows: http://localhost:5678
echo    - Lead Scoring API: http://localhost:5001
echo    - Property Search API: http://localhost:5002
echo    - Property Valuation API: http://localhost:5003
echo    - Email Marketing API: http://localhost:5004
echo    - Dashboard Analytics API: http://localhost:5005
echo    - Data Collection API: http://localhost:5006
echo.
echo 📚 Documentation:
echo    - Setup Guide: COMPLETE_SETUP_GUIDE.md
echo    - API Documentation: Available at each service /docs endpoint
echo.
echo 🎯 Next Steps:
echo 1. Configure your Baserow tables: python setup_baserow_tables.py
echo 2. Import n8n workflows from n8n/workflows/
echo 3. Configure Open WebUI functions
echo 4. Add real property data
echo.

pause
