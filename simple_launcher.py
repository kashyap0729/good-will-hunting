"""
Simple Goodwill Gym Platform Launcher
Works reliably on Windows with proper virtual environment handling
"""

import subprocess
import sys
import os
import time

def main():
    print("🎮 Goodwill Gym Platform - Simple Launcher")
    print("=" * 50)
    
    # Check if we're in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected")
        print("Please run: .\.venv\Scripts\Activate.ps1")
        print("Then run: python simple_launcher.py")
        input("Press Enter to exit...")
        return
    
    print("✅ Virtual environment active")
    
    # Stop any existing processes
    print("🧹 Cleaning up...")
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, check=False)
        time.sleep(2)
    except:
        pass
    
    # Initialize database
    print("💾 Setting up database...")
    try:
        subprocess.run([sys.executable, "database.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Database setup failed")
        input("Press Enter to exit...")
        return
    
    print("🚀 Starting API...")
    try:
        # Start API
        api_process = subprocess.Popen([sys.executable, "goodwill_gym_backend.py"])
        time.sleep(5)  # Wait for API to start
        
        print("🎨 Starting Dashboard...")
        # Start dashboard
        dashboard_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "goodwill_gym_dashboard.py", 
            "--server.port", "8505"
        ])
        
        print("\n🎉 Platform launched!")
        print("📊 Dashboard: http://localhost:8505")
        print("🔧 API Docs: http://localhost:8000/docs")
        print("\n📝 Instructions:")
        print("1. Open http://localhost:8505 in your browser")
        print("2. Register as a trainer")
        print("3. Explore gym locations on the map")
        print("4. Donate items to earn points and become gym leader!")
        print("\n⏹️  Press Ctrl+C to stop...")
        
        # Keep running
        try:
            api_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping platform...")
            api_process.terminate()
            dashboard_process.terminate()
            print("👋 Stopped!")
            
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()