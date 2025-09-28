#!/usr/bin/env python3
"""
🔍 Platform Validation Script
Comprehensive testing to ensure all components are working correctly.
"""

import subprocess
import sys
import importlib
import os
import json
import time
from pathlib import Path

def colored_print(message, color="green"):
    """Print colored messages"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m", 
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{message}{colors['reset']}")

def test_python_environment():
    """Test Python version and virtual environment"""
    colored_print("🐍 Testing Python Environment...", "blue")
    
    # Check Python version
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        colored_print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    else:
        colored_print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Upgrade to 3.11+ required", "red")
        return False
        
    # Check virtual environment
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        colored_print("✅ Virtual environment - Active")
    else:
        colored_print("⚠️ Virtual environment - Not detected", "yellow")
    
    return True

def test_core_imports():
    """Test critical package imports"""
    colored_print("📦 Testing Core Package Imports...", "blue")
    
    packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI web server"),
        ("streamlit", "Dashboard framework"),
        ("pandas", "Data manipulation"),
        ("numpy", "Numerical computing"),
        ("plotly", "Interactive plotting"),
        ("google.cloud.firestore", "Google Cloud Firestore"),
        ("google.auth", "Google Authentication"),
        ("cryptography", "Security and encryption"),
        ("aiohttp", "Async HTTP client"),
        ("pytest", "Testing framework")
    ]
    
    success_count = 0
    for package, description in packages:
        try:
            importlib.import_module(package)
            colored_print(f"✅ {package} - {description}")
            success_count += 1
        except ImportError as e:
            colored_print(f"❌ {package} - Import failed: {e}", "red")
    
    if success_count == len(packages):
        colored_print(f"✅ All {len(packages)} core packages imported successfully!")
        return True
    else:
        colored_print(f"❌ {len(packages) - success_count} packages failed to import", "red")
        return False

def test_project_structure():
    """Validate project directory structure"""
    colored_print("📁 Validating Project Structure...", "blue")
    
    required_dirs = [
        "agents/donor-engagement",
        "agents/charity-optimization", 
        "services/donation-service",
        "services/points-service",
        "frontend/streamlit-dashboard",
        "frontend/maps-integration",
        "infrastructure/terraform",
        "deployment",
        "docs"
    ]
    
    required_files = [
        "requirements.txt",
        ".env.example", 
        "agents/a2a_protocol.py",
        "services/donation-service/main.py",
        "services/points-service/main.py",
        "frontend/streamlit-dashboard/app.py",
        "infrastructure/terraform/main.tf",
        "deployment/deploy.py",
        "docs/API_REFERENCE.md",
        "docs/DEPLOYMENT_GUIDE.md"
    ]
    
    missing_items = []
    
    # Check directories
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            colored_print(f"✅ Directory: {dir_path}")
        else:
            colored_print(f"❌ Missing directory: {dir_path}", "red")
            missing_items.append(dir_path)
    
    # Check files  
    for file_path in required_files:
        if Path(file_path).exists():
            colored_print(f"✅ File: {file_path}")
        else:
            colored_print(f"❌ Missing file: {file_path}", "red")
            missing_items.append(file_path)
    
    if not missing_items:
        colored_print("✅ Project structure is complete!")
        return True
    else:
        colored_print(f"❌ {len(missing_items)} items missing from project structure", "red")
        return False

def test_service_imports():
    """Test that all services can be imported"""
    colored_print("🔧 Testing Service Imports...", "blue")
    
    services = [
        ("services.donation-service.main", "Donation Service"),
        ("services.points-service.main", "Points Service"),
        ("agents.donor-engagement.agent", "Donor Engagement Agent"),
        ("agents.charity-optimization.agent", "Charity Optimization Agent"),
        ("agents.a2a_protocol", "A2A Protocol")
    ]
    
    # Add project paths to Python path
    project_root = Path.cwd()
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "services" / "donation-service"))
    sys.path.insert(0, str(project_root / "services" / "points-service"))
    sys.path.insert(0, str(project_root / "agents"))
    
    success_count = 0
    for module_path, description in services:
        try:
            # Handle special path formats
            if "donation-service" in module_path:
                sys.path.insert(0, str(project_root / "services" / "donation-service"))
                importlib.import_module("main")
            elif "points-service" in module_path:
                sys.path.insert(0, str(project_root / "services" / "points-service"))
                importlib.import_module("main")
            elif "donor-engagement" in module_path:
                sys.path.insert(0, str(project_root / "agents" / "donor-engagement"))
                importlib.import_module("agent")
            elif "charity-optimization" in module_path:
                sys.path.insert(0, str(project_root / "agents" / "charity-optimization"))
                importlib.import_module("agent")
            else:
                importlib.import_module(module_path)
            
            colored_print(f"✅ {description}")
            success_count += 1
        except Exception as e:
            colored_print(f"❌ {description} - Import failed: {e}", "red")
    
    if success_count == len(services):
        colored_print("✅ All services imported successfully!")
        return True
    else:
        colored_print(f"❌ {len(services) - success_count} services failed to import", "red")
        return False

def test_configuration():
    """Test configuration files"""
    colored_print("⚙️ Testing Configuration...", "blue")
    
    # Check .env.example
    if Path(".env.example").exists():
        with open(".env.example", "r") as f:
            env_content = f.read()
            required_vars = ["GCP_PROJECT_ID", "GOOGLE_MAPS_API_KEY", "ENVIRONMENT"]
            missing_vars = [var for var in required_vars if var not in env_content]
            
            if not missing_vars:
                colored_print("✅ Environment template complete")
            else:
                colored_print(f"❌ Missing environment variables: {missing_vars}", "red")
                return False
    
    # Check requirements.txt
    if Path("requirements.txt").exists():
        with open("requirements.txt", "r") as f:
            reqs = f.read()
            if "fastapi" in reqs and "streamlit" in reqs:
                colored_print("✅ Requirements.txt contains core packages")
            else:
                colored_print("❌ Requirements.txt missing core packages", "red")
                return False
    
    return True

def generate_test_report():
    """Generate comprehensive test report"""
    colored_print("📊 Generating Test Report...", "blue")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "tests": {
            "python_environment": test_python_environment(),
            "core_imports": test_core_imports(), 
            "project_structure": test_project_structure(),
            "configuration": test_configuration()
        }
    }
    
    # Save report
    with open("validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    passed_tests = sum(report["tests"].values())
    total_tests = len(report["tests"])
    
    colored_print(f"\n📋 VALIDATION SUMMARY", "blue")
    colored_print(f"Tests Passed: {passed_tests}/{total_tests}")
    colored_print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        colored_print("🎉 ALL TESTS PASSED! Platform is ready to deploy! 🚀", "green")
        return True
    else:
        colored_print("⚠️ Some tests failed. Please review and fix issues before deployment.", "yellow")
        return False

def main():
    """Run complete platform validation"""
    colored_print("🔍 GOODWILL PLATFORM VALIDATION", "blue")
    colored_print("=" * 50)
    
    success = generate_test_report()
    
    colored_print("=" * 50)
    if success:
        colored_print("✅ Platform validation completed successfully!")
        colored_print("🚀 Ready for deployment to Google Cloud Platform!")
        colored_print("📚 Next steps:")
        colored_print("   1. Configure your .env file")
        colored_print("   2. Set up Google Cloud credentials") 
        colored_print("   3. Run: python deployment/deploy.py")
    else:
        colored_print("❌ Platform validation failed. Please fix issues above.", "red")
        sys.exit(1)

if __name__ == "__main__":
    main()