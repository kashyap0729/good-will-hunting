"""
Fast Launcher - Optimized Platform Startup
Starts both fast_backend.py and fast_dashboard.py with proper sequencing
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path

def check_python_path():
    """Ensure we're in the right directory and virtual environment"""
    project_dir = Path(r"d:\GCP Hackathon\goodwillC")
    
    if not project_dir.exists():
        print(f"❌ Project directory not found: {project_dir}")
        return False
    
    os.chdir(project_dir)
    print(f"📁 Working directory: {project_dir}")
    
    # Check if virtual environment exists
    venv_path = project_dir / ".venv"
    if venv_path.exists():
        print(f"✅ Virtual environment found: {venv_path}")
        return True
    else:
        print(f"⚠️ Virtual environment not found at {venv_path}")
        return False

def wait_for_api(max_attempts=30, delay=2):
    """Wait for the API to be ready"""
    print("⏳ Waiting for Fast API to start...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=3)
            if response.status_code == 200:
                print(f"✅ Fast API is ready! (attempt {attempt + 1})")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_attempts - 1:
            print(f"⏳ Attempt {attempt + 1}/{max_attempts} - API not ready yet...")
            time.sleep(delay)
    
    print(f"❌ Fast API failed to start after {max_attempts} attempts")
    return False

def start_fast_backend():
    """Start the fast backend API"""
    print("\n🚀 Starting Fast Backend API...")
    
    try:
        # Use the virtual environment Python
        venv_python = r"d:\GCP Hackathon\goodwillC\.venv\Scripts\python.exe"
        
        if not Path(venv_python).exists():
            print(f"❌ Python executable not found: {venv_python}")
            return None
        
        backend_process = subprocess.Popen(
            [venv_python, "fast_backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=r"d:\GCP Hackathon\goodwillC"
        )
        
        print(f"🔄 Fast Backend started with PID: {backend_process.pid}")
        return backend_process
        
    except Exception as e:
        print(f"❌ Failed to start Fast Backend: {e}")
        return None

def start_fast_dashboard():
    """Start the fast dashboard"""
    print("\n🎮 Starting Fast Dashboard...")
    
    try:
        # Use the virtual environment streamlit
        venv_streamlit = r"d:\GCP Hackathon\goodwillC\.venv\Scripts\streamlit.exe"
        
        if not Path(venv_streamlit).exists():
            print(f"❌ Streamlit executable not found: {venv_streamlit}")
            return None
        
        dashboard_process = subprocess.Popen(
            [venv_streamlit, "run", "fast_dashboard.py", "--server.port", "8501", "--server.headless", "true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=r"d:\GCP Hackathon\goodwillC"
        )
        
        print(f"🔄 Fast Dashboard started with PID: {dashboard_process.pid}")
        return dashboard_process
        
    except Exception as e:
        print(f"❌ Failed to start Fast Dashboard: {e}")
        return None

def check_dashboard_ready(max_attempts=20, delay=3):
    """Check if dashboard is ready"""
    print("⏳ Waiting for Fast Dashboard to be ready...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8501", timeout=3)
            if response.status_code == 200:
                print(f"✅ Fast Dashboard is ready! (attempt {attempt + 1})")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_attempts - 1:
            print(f"⏳ Attempt {attempt + 1}/{max_attempts} - Dashboard not ready yet...")
            time.sleep(delay)
    
    print(f"❌ Fast Dashboard failed to start after {max_attempts} attempts")
    return False

def main():
    print("="*60)
    print("⚡ FAST GOODWILL GYM PLATFORM LAUNCHER")
    print("="*60)
    
    # Check Python environment
    if not check_python_path():
        print("❌ Environment check failed!")
        return False
    
    # Start backend first
    backend_process = start_fast_backend()
    if not backend_process:
        print("❌ Failed to start backend!")
        return False
    
    # Wait for API to be ready
    if not wait_for_api():
        print("❌ API failed to start!")
        if backend_process:
            backend_process.terminate()
        return False
    
    # Start dashboard
    dashboard_process = start_fast_dashboard()
    if not dashboard_process:
        print("❌ Failed to start dashboard!")
        if backend_process:
            backend_process.terminate()
        return False
    
    # Wait for dashboard to be ready
    if not check_dashboard_ready():
        print("❌ Dashboard failed to start!")
        if backend_process:
            backend_process.terminate()
        if dashboard_process:
            dashboard_process.terminate()
        return False
    
    # Success!
    print("\n" + "="*60)
    print("🎉 FAST GOODWILL GYM PLATFORM READY!")
    print("="*60)
    print("📊 Fast Backend API: http://localhost:8000")
    print("🎮 Fast Dashboard:   http://localhost:8501")
    print("📚 API Docs:        http://localhost:8000/docs")
    print("="*60)
    
    print("\n✨ PERFORMANCE FEATURES ENABLED:")
    print("⚡ Connection pooling for 10x faster database access")
    print("🧠 Intelligent caching for sub-second responses")
    print("🗺️ Optimized maps with fast rendering")
    print("📊 Session state caching for instant UI updates")
    print("🎯 Reduced API calls with smart data reuse")
    
    print("\n🎮 ALL ORIGINAL FEATURES PRESERVED:")
    print("🗺️ Interactive maps showing gym leaders")
    print("🏆 Real-time leaderboard competitions")
    print("👤 Complete user profiles and progression")
    print("🚨 Missing items alerts with bonus points")
    print("🎪 Pokemon Go-style gym challenge system")
    
    print("\n" + "="*60)
    print("💡 READY TO USE!")
    print("1. Visit http://localhost:8501 in your browser")
    print("2. Register as a trainer or select existing user")
    print("3. Experience lightning-fast charitable giving!")
    print("="*60)
    
    try:
        print("\n⏸️  Press Ctrl+C to stop both services...")
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("⚠️ Backend process stopped unexpectedly!")
                break
            
            if dashboard_process.poll() is not None:
                print("⚠️ Dashboard process stopped unexpectedly!")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Fast Goodwill Gym Platform...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ Fast Backend stopped")
        
        if dashboard_process:
            dashboard_process.terminate() 
            print("✅ Fast Dashboard stopped")
        
        print("👋 Fast Goodwill Gym Platform stopped successfully!")
        return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Platform stopped cleanly")
        else:
            print("\n❌ Platform encountered issues")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)