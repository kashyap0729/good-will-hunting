#!/bin/bash
echo "============================================================"
echo "⚡ FAST GOODWILL GYM PLATFORM LAUNCHER (macOS/Linux)"
echo "============================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python not found! Please install Python 3.8+ from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Make sure we're in the script directory
cd "$(dirname "$0")"

# Run the Python launcher
$PYTHON_CMD fast_launch.py

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "❌ Platform encountered an error"
    read -p "Press Enter to continue..."
fi