@echo off
echo ======================================================================
echo 🎮 GOODWILL GYM PLATFORM v3.0 LAUNCHER
echo Pokemon Go-style • SQLite Database • Google ADK Notifications  
echo ======================================================================

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Install dependencies  
echo 📦 Ensuring dependencies are installed...
pip install -r requirements.txt >nul 2>&1

REM Clean up any existing processes
echo 🧹 Cleaning up existing processes...
taskkill /f /im python.exe >nul 2>&1

REM Initialize database
echo 💾 Initializing database...
python database.py
if errorlevel 1 (
    echo ❌ Database initialization failed
    pause
    exit /b 1
)

REM Start the backend API
echo 🚀 Starting Goodwill Gym Platform API v3.0...
start /B python goodwill_gym_backend.py

REM Wait for API to start
echo ⏳ Waiting for API to start...
timeout /t 5 /nobreak >nul

REM Test API health
echo 🔍 Testing API connection...
curl -s http://localhost:8000/health >nul
if errorlevel 1 (
    echo ❌ API failed to start properly
    pause
    exit /b 1
)

echo ✅ API is running!

REM Start the dashboard
echo 🎨 Starting Goodwill Gym Dashboard...
start /B streamlit run goodwill_gym_dashboard.py --server.port 8505 --browser.gatherUsageStats false

REM Wait for dashboard
timeout /t 3 /nobreak >nul

echo ======================================================================
echo 🎉 GOODWILL GYM PLATFORM LAUNCHED SUCCESSFULLY!
echo ======================================================================
echo 🔗 API Documentation: http://localhost:8000/docs
echo 📊 Gym Dashboard: http://localhost:8505  
echo 🏥 Health Check: http://localhost:8000/health
echo 📈 Missing Items: http://localhost:8000/missing-items
echo ======================================================================
echo.
echo 🎮 Ready to play! Features:
echo    🗺️  Pokemon Go-style gym system with real locations
echo    💾 SQLite database with persistent data
echo    🤖 Google ADK notification agent
echo    🎯 Missing items gamification with bonus points
echo    👑 Gym leader system - compete for leadership!
echo.
echo 💡 How to Play:
echo    1. Open http://localhost:8505 in your browser
echo    2. Register as a trainer
echo    3. Donate items at gym locations to earn points
echo    4. Become a gym leader by donating the most!
echo.
echo 🔧 Press any key to stop the platform...
pause >nul

echo 🛑 Shutting down platform...
taskkill /f /im python.exe >nul 2>&1
echo 👋 Platform stopped successfully!
pause