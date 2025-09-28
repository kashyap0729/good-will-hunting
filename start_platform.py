#!/usr/bin/env python3
"""
Google A2A Gamified Goodwill Platform - Service Launcher
Starts all services with proper dependency management and error handling
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path
import json
import requests
from typing import Dict, List, Optional

# Configuration
PROJECT_ROOT = Path(__file__).parent
PYTHON_EXE = r"C:/ganti.b/Hackathon/GWH2/.venv/Scripts/python.exe"
SERVICES = {
    "streamlit": {
        "name": "Streamlit Dashboard",
        "port": 8502,
        "cmd": [PYTHON_EXE, "-m", "streamlit", "run", "frontend/streamlit-dashboard/app.py", "--server.port", "8502"],
        "health_check": "http://localhost:8502",
        "startup_text": "You can now view your Streamlit app"
    },
    "donation": {
        "name": "Donation Service API", 
        "port": 8000,
        "cmd": [PYTHON_EXE, "-m", "uvicorn", "services.donation-service.main:app", "--host", "127.0.0.1", "--port", "8000"],
        "health_check": "http://localhost:8000/health",
        "startup_text": "Application startup complete"
    },
    "points": {
        "name": "Points Service API",
        "port": 8001, 
        "cmd": [PYTHON_EXE, "-m", "uvicorn", "services.points-service.main:app", "--host", "127.0.0.1", "--port", "8001"],
        "health_check": "http://localhost:8001/health",
        "startup_text": "Application startup complete"
    }
}

def print_header():
    """Print startup header"""
    print("🎮" + "=" * 60 + "🎮")
    print("   Google A2A Gamified Goodwill Platform")
    print("   Starting all services...")
    print("🎮" + "=" * 60 + "🎮\n")

def check_port(port: int) -> bool:
    """Check if a port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        result = s.connect_ex(('127.0.0.1', port))
        return result != 0

def start_service(service_key: str, config: Dict) -> Optional[subprocess.Popen]:
    """Start a single service"""
    print(f"🚀 Starting {config['name']}...")
    
    # Check if port is available
    if not check_port(config['port']):
        print(f"   ⚠️  Port {config['port']} is already in use")
        return None
    
    try:
        # Change to project root
        os.chdir(PROJECT_ROOT)
        
        # Start the process
        process = subprocess.Popen(
            config['cmd'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print(f"   📋 Process started (PID: {process.pid})")
        print(f"   🌐 Will be available on port {config['port']}")
        
        # Monitor startup in a separate thread
        def monitor_startup():
            try:
                for line in iter(process.stdout.readline, ''):
                    if config['startup_text'] in line:
                        print(f"   ✅ {config['name']} is ready!")
                        break
                    if "error" in line.lower() or "failed" in line.lower():
                        print(f"   ❌ Error in {config['name']}: {line.strip()}")
            except Exception as e:
                print(f"   ⚠️  Monitoring error for {config['name']}: {e}")
        
        monitor_thread = threading.Thread(target=monitor_startup, daemon=True)
        monitor_thread.start()
        
        return process
        
    except Exception as e:
        print(f"   ❌ Failed to start {config['name']}: {e}")
        return None

def create_mock_endpoints():
    """Create a simple mock service for missing Google Cloud dependencies"""
    mock_code = '''
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

app = FastAPI(title="Mock Google Services")

@app.get("/health")
def health():
    return {"status": "ok", "service": "mock"}

@app.get("/")
def root():
    return {"message": "Mock Google Cloud Services for local development"}

@app.post("/firestore/documents")
def mock_firestore(data: Dict[str, Any]):
    return {"id": "mock_id", "data": data}

@app.get("/firestore/documents/{collection}")
def mock_firestore_get(collection: str):
    return {"documents": [], "collection": collection}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8888)
'''
    
    mock_file = PROJECT_ROOT / "mock_services.py"
    with open(mock_file, 'w') as f:
        f.write(mock_code)
    
    print("🔧 Created mock services for local development")
    return mock_file

def main():
    """Main startup function"""
    print_header()
    
    # Create mock services
    create_mock_endpoints()
    
    # Start mock services first
    print("🔧 Starting mock Google Cloud services...")
    mock_cmd = [PYTHON_EXE, str(PROJECT_ROOT / "mock_services.py")]
    mock_process = subprocess.Popen(mock_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("   📋 Mock services started on port 8888")
    time.sleep(2)
    
    # Start all main services
    processes = {}
    
    for service_key, config in SERVICES.items():
        processes[service_key] = start_service(service_key, config)
        time.sleep(3)  # Give each service time to start
    
    # Wait a bit for all services to initialize
    time.sleep(5)
    
    # Print final status
    print("\n🎉" + "=" * 60 + "🎉")
    print("   PLATFORM READY!")
    print("🎉" + "=" * 60 + "🎉\n")
    
    print("📊 Access Points:")
    print("   • Streamlit Dashboard: http://localhost:8502")
    print("   • Donation API Docs: http://localhost:8000/docs")
    print("   • Points API Docs: http://localhost:8001/docs") 
    print("   • Mock Services: http://localhost:8888")
    
    print("\n💡 Features Available:")
    print("   • Gamified donation interface")
    print("   • Real-time leaderboards")
    print("   • Achievement system")
    print("   • Interactive maps")
    print("   • API documentation")
    
    print("\n⚠️  Note: Using mock services for Google Cloud features")
    print("   Configure .env file with real credentials for production")
    
    print("\n🛑 Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for name, process in processes.items():
            if process:
                process.terminate()
        if 'mock_process' in locals():
            mock_process.terminate()
        print("✅ All services stopped.")

if __name__ == "__main__":
    main()
