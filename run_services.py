#!/usr/bin/env python3
"""
Service Runner Script
Starts all services needed for the Google A2A Gamified Goodwill Platform
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_service(name, command, cwd=None):
    """Run a service in a separate process"""
    print(f"Starting {name}...")
    try:
        if cwd:
            process = subprocess.Popen(command, cwd=cwd, shell=True)
        else:
            process = subprocess.Popen(command, shell=True)
        print(f"✅ {name} started successfully (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    # Get the project root directory
    project_root = Path(__file__).parent
    python_exe = r"C:/ganti.b/Hackathon/GWH2/.venv/Scripts/python.exe"
    
    print("🚀 Starting Google A2A Gamified Goodwill Platform")
    print("=" * 50)
    
    services = []
    
    # 1. Start Streamlit Dashboard
    streamlit_cmd = f'"{python_exe}" -m streamlit run frontend/streamlit-dashboard/app.py --server.port 8501'
    services.append(run_service("Streamlit Dashboard", streamlit_cmd, project_root))
    
    time.sleep(3)  # Give streamlit time to start
    
    # 2. Start Donation Service (FastAPI)
    donation_cmd = f'"{python_exe}" -m uvicorn services.donation-service.main:app --host 0.0.0.0 --port 8000 --reload'
    services.append(run_service("Donation Service API", donation_cmd, project_root))
    
    time.sleep(2)
    
    # 3. Start Points Service (FastAPI)
    points_cmd = f'"{python_exe}" -m uvicorn services.points-service.main:app --host 0.0.0.0 --port 8001 --reload'
    services.append(run_service("Points Service API", points_cmd, project_root))
    
    print("\n" + "=" * 50)
    print("🎉 All services started!")
    print("\n📊 Access Points:")
    print("   • Streamlit Dashboard: http://localhost:8501")
    print("   • Donation API Docs: http://localhost:8000/docs")
    print("   • Points API Docs: http://localhost:8001/docs")
    print("\n⚠️  Note: Some features may require Google Cloud setup")
    print("   Check the .env file for configuration")
    print("\n🛑 Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for service in services:
            if service:
                service.terminate()
        print("✅ All services stopped.")

if __name__ == "__main__":
    main()
