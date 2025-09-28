@echo off
echo 🚀 Starting Goodwill Gym Platform with AI Notifications
echo ============================================================

echo.
echo 1. Starting Backend API Server...
start "Goodwill Backend" python fast_backend.py

echo 2. Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo 3. Starting Dashboard...
start "Goodwill Dashboard" streamlit run fast_dashboard.py --server.port=8501

echo.
echo ✅ Platform started successfully!
echo 🌐 Dashboard: http://localhost:8501
echo 🔧 Backend API: http://localhost:8000
echo.
echo 💡 Make a donation to see AI-powered notifications!
echo.
pause
