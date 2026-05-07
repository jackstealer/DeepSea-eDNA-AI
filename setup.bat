@echo off
echo =========================================
echo eDNA Analysis System - Setup
echo =========================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed
    exit /b 1
)

echo [OK] Python and Node.js found

REM Setup Frontend
echo.
echo Setting up frontend...
call npm install
copy .env.example .env
echo [OK] Frontend setup complete

REM Setup Backend
echo.
echo Setting up backend...
cd backend

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Create directories
mkdir data\uploads 2>nul
mkdir data\results 2>nul
mkdir data\training 2>nul
mkdir ml_models 2>nul
mkdir logs 2>nul

REM Copy environment file
copy .env.example .env

echo [OK] Backend setup complete

cd ..

echo.
echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo Next steps:
echo.
echo 1. Download and train a model:
echo    cd backend
echo    venv\Scripts\activate
echo    python scripts\quick_start_training.py
echo.
echo 2. Start the backend:
echo    cd backend
echo    python app\main.py
echo.
echo 3. Start the frontend (in another terminal):
echo    npm run dev
echo.
echo 4. Or use Docker:
echo    docker-compose up -d
echo.
echo =========================================
pause
