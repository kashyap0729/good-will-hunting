# 🎮 Goodwill Hunting

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Cross-Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/kashyap0729/good-will-hunting)

**Pokemon Go-style gamified charitable giving platform** with interactive maps, real-time leaderboards, and high-performance optimizations.

## 🚀 Quick Start

### Platform-Specific Launch Options

**🐍 Python Launcher (All Platforms)**
```bash
python fast_launch.py
```

**🪟 Windows Users**
```cmd
.\launch.bat          # PowerShell
launch.bat            # Command Prompt (double-click in File Explorer)
```

**🐧 macOS/Linux Users**
```bash
./launch.sh
```

The launcher **automatically**:
- 📁 Detects project directory from any location
- 🐍 Finds Python and virtual environment (cross-platform)
- 🚀 Starts backend API and dashboard with proper sequencing
- ✅ Verifies all services are ready

### Manual Setup (If Needed)

1. **Clone Repository**
```bash
git clone https://github.com/kashyap0729/good-will-hunting.git
cd good-will-hunting
```

2. **Create Virtual Environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux  
source .venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Launch Platform**
```bash
python fast_launch.py
```

## 🌐 Access Points

Once launched, access these URLs:
- **🎮 Dashboard**: http://localhost:8501
- **📊 API**: http://localhost:8000  
- **📚 API Docs**: http://localhost:8000/docs

## 🎯 Features

### 🗺️ **Interactive Miami Gym Map**
- **5 Real Miami Locations**: South Beach, Wynwood, Coral Gables, Little Havana, Coconut Grove
- **Pokemon Go-style Markers**: Red (occupied by leader), Green (available for challenge)
- **Click Interactions**: View gym leader info and challenge status

### 🏆 **Gamification System**
- **Trainer Tiers**: Bronze → Silver → Gold → Platinum
- **Point System**: Base points + bonus for high-demand items  
- **Gym Leaders**: Compete to lead each location
- **Achievements**: Unlock badges and streaks
- **Real-time Leaderboards**: Live competition rankings

### 🚨 **Smart Donation Alerts**
- **Missing Items System**: Track urgent needs at each gym
- **Bonus Points**: Extra rewards for high-priority donations
- **Google ADK Notifications**: Achievement celebrations and encouragement

### ⚡ **Performance Optimizations**
- **Sub-20ms API Response Times**: Connection pooling and caching
- **Session State Management**: Reduced API calls for instant UI updates
- **Optimized Database Queries**: SQLite with intelligent indexing
- **Fast Map Rendering**: Streamlined markers and interactions

## 🏛️ Miami Gym Locations

| Gym Name | Neighborhood | Address |
|----------|--------------|---------|
| 🏖️ South Beach Donation Hub | South Beach | 123 Ocean Dr |
| 🎨 Wynwood Warehouse | Wynwood Arts District | 456 NW 2nd Ave |
| 🏛️ Coral Gables Vault | Coral Gables | 789 Miracle Mile |
| ️ Little Havana Helper Hub | Little Havana | 654 SW 8th St |
| 🌴 Coconut Grove Pantry | Coconut Grove | 987 Main Hwy |

## 💻 Cross-Platform Support

The platform works seamlessly on:
- **Windows 10/11** 
- **macOS** 
- **Linux** (Ubuntu, CentOS, Debian)

### 🐍 Python Requirements
- **Python 3.8+** (Recommended: 3.11+)
- **Virtual Environment** (Recommended)

## �️ Troubleshooting

### Common PowerShell Issues

**Error: "launch.bat is not recognized"**
```powershell
# Use .\ prefix in PowerShell
.\launch.bat

# Or run directly with Command Prompt
cmd /c launch.bat
```

**Error: "Execution Policy Restricted"**
```powershell
# Check current policy
Get-ExecutionPolicy

# If restricted, temporarily allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Platform Issues

**"Platform Offline: Connection Error"**
```bash
# Check if services are running
python fast_launch.py

# Or check manually
curl http://localhost:8000/health
```

**"Module not found" errors**
```bash
# Install dependencies
pip install -r requirements.txt

# Or run setup script
python setup.py
```

## �🚀 Ready to Start?

```bash
git clone https://github.com/kashyap0729/good-will-hunting.git
cd good-will-hunting

# Windows PowerShell
.\launch.bat

# Windows Command Prompt / macOS / Linux
python fast_launch.py
```

**Visit http://localhost:8501 and start your Miami charitable gaming adventure!** 🌴🏖️
