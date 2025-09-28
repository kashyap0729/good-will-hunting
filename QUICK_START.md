# 🚀 Quick Start Guide - Google A2A Gamified Goodwill Platform

Welcome! This guide will get you up and running with the platform in under 10 minutes.

## 🏃‍♂️ 1. Quick Setup (5 minutes)

### Install Dependencies
```bash
# Activate virtual environment (if not already active)
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install all packages (already done in your environment!)
pip install -r requirements.txt
```

### Set Up Environment
```bash
# Copy the environment template
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env with your settings (optional for local testing)
notepad .env  # Windows
# nano .env  # Linux/Mac
```

## 🎯 2. Run Locally (2 minutes)

### Option A: Full Streamlit Dashboard
```bash
# Start the complete dashboard
streamlit run frontend/streamlit-dashboard/app.py
# Opens in browser at: http://localhost:8501
```

### Option B: API Services  
```bash
# Terminal 1: Donation Service
cd services/donation-service
uvicorn main:app --reload --port 8000
# API docs at: http://localhost:8000/docs

# Terminal 2: Points Service  
cd services/points-service
uvicorn main:app --reload --port 8001
# API docs at: http://localhost:8001/docs
```

## 🔍 3. Test Everything (1 minute)

```bash
# Run validation script
python validate_platform.py
# Should show: "🎉 ALL TESTS PASSED!"
```

## 🎮 4. Explore Features

### Dashboard Features
- 📊 **Real-time Metrics**: Live donation tracking
- 🏆 **Leaderboards**: User rankings and achievements  
- 🗺️ **Interactive Maps**: Location-based hotspots
- 🎯 **Gamification**: Points, tiers, and badges

### API Features
- 💰 **Donations API**: Create and track donations
- 🏆 **Points Engine**: Gamification system
- 🤖 **AI Agents**: A2A intelligent coordination
- 🔔 **Real-time Updates**: WebSocket notifications

## 🚀 5. Deploy to Google Cloud (Optional)

### Prerequisites
```bash
# Install Google Cloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Deploy Infrastructure
```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### Deploy Services
```bash
python deployment/deploy.py --project-id=YOUR_PROJECT --action=full
```

## 📚 Next Steps

### Learn More
- 📖 **[Full Documentation](./docs/DEPLOYMENT_GUIDE.md)**: Complete setup guide
- 🔧 **[API Reference](./docs/API_REFERENCE.md)**: Detailed API documentation
- 🤖 **[A2A Agents](./agents/)**: Explore AI agent implementation
- 🎮 **[Gamification](./services/points-service/)**: Points and achievements system

### Customize
- 🎨 **Branding**: Update colors and logos in Streamlit app
- 🏆 **Achievements**: Add new badges in `points-service/achievements.py`
- 🗺️ **Maps**: Customize hotspots in `frontend/maps-integration/`
- 🤖 **AI Logic**: Enhance agents in `agents/` directory

## 🆘 Need Help?

### Quick Fixes
```bash
# Restart Streamlit if it's not loading
Ctrl+C  # Stop current process
streamlit run frontend/streamlit-dashboard/app.py

# Clear Streamlit cache
streamlit cache clear

# Reinstall packages if imports fail
pip install --upgrade -r requirements.txt
```

### Common Issues
1. **Import Errors**: Make sure you're in the virtual environment
2. **Port Conflicts**: Change port numbers in uvicorn commands
3. **Permission Errors**: Run as administrator on Windows
4. **Google Cloud Auth**: Run `gcloud auth application-default login`

### Get Support
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/your-org/goodwill-platform/issues)
- 💬 **Ask Questions**: [GitHub Discussions](https://github.com/your-org/goodwill-platform/discussions)
- 📧 **Contact**: support@goodwill-platform.com

---

## 🎉 You're Ready!

The platform is now running locally. Start exploring the dashboard and API features!

**Happy coding! 🚀**