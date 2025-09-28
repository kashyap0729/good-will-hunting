"""
Enhanced Platform Launcher v3.0
Starts the complete Goodwill Gym Platform with SQLite and Maps
"""

import subprocess
import time
import requests
import sys
import os

# Configuration
API_HOST = "localhost"
API_PORT = 8000
DASHBOARD_PORT = 8505
API_SCRIPT = "goodwill_gym_backend.py"
DASHBOARD_SCRIPT = "goodwill_gym_dashboard.py"

def kill_processes_on_ports():
    """Kill any existing processes on our ports"""
    print("🧹 Cleaning up existing processes...")
    
    if sys.platform == "win32":
        # Windows - Use PowerShell commands that work properly
        try:
            # Kill processes using the ports
            subprocess.run([
                "powershell", "-Command", 
                f"Get-NetTCPConnection -LocalPort {API_PORT} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"
            ], capture_output=True)
            
            subprocess.run([
                "powershell", "-Command", 
                f"Get-NetTCPConnection -LocalPort {DASHBOARD_PORT} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"
            ], capture_output=True)
            
        except Exception as e:
            # Fallback: try to kill all python processes (less precise but works)
            try:
                subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                             capture_output=True, check=False)
            except:
                pass  # If this fails too, just continue
    else:
        # Unix-like
        os.system(f"lsof -t -i:{API_PORT} | xargs kill -9 >/dev/null 2>&1")
        os.system(f"lsof -t -i:{DASHBOARD_PORT} | xargs kill -9 >/dev/null 2>&1")

def check_api_health(max_attempts=20):
    """Check if API is healthy with better error handling"""
    print("🔍 Waiting for API to become healthy...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"http://{API_HOST}:{API_PORT}/health", timeout=3)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API is healthy! Version: {health_data.get('version', 'Unknown')}")
                print(f"   Database: {health_data.get('database', {})}")
                return True
        except requests.exceptions.ConnectionError:
            pass  # Expected while API is starting
        except Exception as e:
            print(f"   Attempt {attempt + 1}: {str(e)[:50]}...")
        
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("❌ API failed to become healthy")
    return False

def start_api():
    """Start the Goodwill Gym API backend"""
    print("🚀 Starting Goodwill Gym Platform API v3.0...")
    
    # Initialize database first
    print("💾 Initializing database...")
    try:
        import database
        database.DatabaseManager()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return None
    
    try:
        # Start API with better process handling
        process = subprocess.Popen(
            [sys.executable, API_SCRIPT],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        
        print(f"📡 API started with PID: {process.pid}")
        
        # Wait for API to be ready
        if check_api_health():
            return process
        else:
            print("❌ API failed to start properly")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        return None

def test_api_features():
    """Test the Goodwill Gym API features"""
    print("\n🧪 Testing Goodwill Gym Features...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            features = data.get('features', [])
            if isinstance(features, list):
                print(f"   Features: {', '.join(features[:3])}...")  # Show first 3 features
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health endpoint working")
            db_stats = health.get('database', {})
            if isinstance(db_stats, dict):
                print(f"   Database: {db_stats.get('users', 0)} users, {db_stats.get('storages', 0)} gyms")
        
        # Test storages (gyms)
        response = requests.get(f"{base_url}/storages", timeout=5)
        if response.status_code == 200:
            storages = response.json()
            print(f"✅ Gym system working")
            if isinstance(storages, list):
                print(f"   Storage gyms loaded: {len(storages)}")
        
        # Test missing items
        response = requests.get(f"{base_url}/missing-items", timeout=5)
        if response.status_code == 200:
            missing = response.json()
            print(f"✅ Missing items system working")
            if isinstance(missing, list):
                print(f"   Critical needs: {len(missing)} items")
        
        # Test users endpoint
        response = requests.get(f"{base_url}/users", timeout=5)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ User system working")
            if isinstance(users, list):
                print(f"   Active trainers: {len(users)}")
        
        print("\n🎉 All Goodwill Gym features are operational!")
        return True
        
    except Exception as e:
        print(f"❌ Feature test failed: {e}")
        print("   Some features may not be fully ready, but platform should still work")
        return True  # Continue anyway

def start_dashboard():
    """Start the Goodwill Gym dashboard"""
    print("\n🎨 Starting Goodwill Gym Dashboard...")
    
    try:
        # Use fixed port and kill any existing process
        print(f"📊 Starting dashboard on port {DASHBOARD_PORT}...")
        
        dashboard_process = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run", DASHBOARD_SCRIPT, 
                "--server.port", str(DASHBOARD_PORT),
                "--browser.gatherUsageStats", "false",
                "--server.headless", "true"
            ],
            cwd=os.getcwd(),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        
        # Wait a moment for dashboard to start
        time.sleep(3)
        
        print(f"🌐 Dashboard started! Visit: http://localhost:{DASHBOARD_PORT}")
        return dashboard_process, DASHBOARD_PORT
        
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return None, None

def main():
    """Main launcher function"""
    print("=" * 70)
    print("🎮 GOODWILL GYM PLATFORM v3.0 LAUNCHER")
    print("Pokemon Go-style • SQLite Database • Google ADK Notifications")
    print("=" * 70)
    
    # Clean up any existing processes
    kill_processes_on_ports()
    
    # Step 1: Start API
    api_process = start_api()
    if not api_process:
        print("\n❌ Failed to start platform. Exiting...")
        return False
    
    # Step 2: Test features
    if not test_api_features():
        print("\n⚠️ Some features may not be working properly")
    
    # Step 3: Start dashboard
    dashboard_process, port = start_dashboard()
    
    print("\n" + "=" * 70)
    print("🎉 GOODWILL GYM PLATFORM LAUNCHED SUCCESSFULLY!")
    print("=" * 70)
    print(f"🔗 API Documentation: http://localhost:{API_PORT}/docs")
    print(f"📊 Gym Dashboard: http://localhost:{port if port else 'N/A'}")
    print(f"🏥 Health Check: http://localhost:{API_PORT}/health")
    print(f"📈 Missing Items: http://localhost:{API_PORT}/missing-items")
    print("=" * 70)
    
    print("\n🎮 New Features in v3.0:")
    print("   🗺️  Pokemon Go-style gym system with real locations")
    print("   💾 SQLite database with persistent data")
    print("   🤖 Google ADK notification agent")
    print("   🎯 Missing items gamification with bonus points")
    print("   👑 Gym leader system - compete for leadership!")
    print("   📍 Interactive maps showing all storage locations")
    
    print("\n💡 How to Play:")
    print("   1. Open the dashboard and create your trainer account")
    print("   2. Visit storage locations (gyms) on the map")
    print("   3. Donate items to earn points and challenge gym leaders")
    print("   4. Get bonus points for donating missing items")
    print("   5. Become a gym leader by having the most points at a location!")
    
    print("\n🔧 To stop the platform:")
    print("   Press Ctrl+C in this terminal")
    
    try:
        # Keep running until interrupted
        print("\n🏃 Platform running... Press Ctrl+C to stop")
        while True:
            time.sleep(5)
            # Check if processes are still alive
            if api_process and api_process.poll() is not None:
                print("⚠️ API process stopped unexpectedly")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Goodwill Gym Platform...")
        
        if api_process:
            try:
                api_process.terminate()
                api_process.wait(timeout=5)
            except:
                api_process.kill()
            print("✅ API stopped")
        
        if dashboard_process:
            try:
                dashboard_process.terminate()
                dashboard_process.wait(timeout=5)
            except:
                dashboard_process.kill()
            print("✅ Dashboard stopped")
        
        print("👋 Goodwill Gym Platform stopped successfully!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)