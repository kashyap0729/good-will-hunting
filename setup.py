#!/usr/bin/env python3
"""
Setup Script for Fast Goodwill Gym Platform
Automatically sets up virtual environment and dependencies
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"🔄 {description}...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("="*60)
    print("🚀 FAST GOODWILL GYM PLATFORM SETUP")
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Please upgrade Python.")
        print("📥 Download from: https://python.org/downloads")
        return False
    
    # Get project directory
    project_dir = Path(__file__).parent.absolute()
    os.chdir(project_dir)
    print(f"📁 Project directory: {project_dir}")
    
    # Create virtual environment
    venv_path = project_dir / ".venv"
    if not venv_path.exists():
        if not run_command(f"{sys.executable} -m venv .venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation command and pip path
    if platform.system() == "Windows":
        activate_cmd = str(venv_path / "Scripts" / "activate.bat")
        pip_path = str(venv_path / "Scripts" / "pip.exe")
    else:
        activate_cmd = f"source {venv_path}/bin/activate"
        pip_path = str(venv_path / "bin" / "pip")
    
    # Install dependencies
    requirements_file = project_dir / "requirements.txt"
    if requirements_file.exists():
        if not run_command(f"{pip_path} install -r requirements.txt", "Installing dependencies"):
            return False
    else:
        # Install core dependencies manually
        core_deps = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0", 
            "streamlit>=1.28.0",
            "streamlit-folium>=0.15.0",
            "requests>=2.31.0",
            "plotly>=5.17.0",
            "folium>=0.15.0",
            "pydantic>=2.5.0"
        ]
        
        for dep in core_deps:
            if not run_command(f"{pip_path} install {dep}", f"Installing {dep}"):
                print(f"⚠️ Failed to install {dep}, but continuing...")
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("📋 Next steps:")
    print("1. Run the platform:")
    print("   python fast_launch.py")
    print("")
    print("2. Or activate environment manually:")
    if platform.system() == "Windows":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("")
    print("3. Access dashboard: http://localhost:8501")
    print("4. Access API docs: http://localhost:8000/docs")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Setup encountered issues")
            sys.exit(1)
        else:
            print("\n✅ Ready to launch! Run: python fast_launch.py")
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)