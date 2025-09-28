@echo off
echo ===================================
echo   Good Will Hunting Platform
echo   With Fixed Notifications
echo ===================================
echo.
echo Starting backend with:
echo - User name support in notifications  
echo - API quota fallback messages
echo - Better UI feedback for quotas
echo.
cd /d "c:\ganti.b\Hackathon\GWH2\good-will-hunting"
echo Backend starting on http://localhost:8000
echo Dashboard available at http://localhost:8501
echo.
python fast_backend.py
