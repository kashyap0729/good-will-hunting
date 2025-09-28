@echo off
echo ============================================================
echo FAST GOODWILL GYM PLATFORM LAUNCHER (WINDOWS)
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Run the Python launcher
python fast_launch.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ❌ Platform encountered an error
    pause
)