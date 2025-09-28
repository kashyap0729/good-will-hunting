# 🎮 Goodwill Gaming Platform v2.0# Google A2A Gamified Goodwill Platform



[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)# 🎮 Google A2A Gamified Goodwill Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)](https://fastapi.tiangolo.com)

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit)](https://streamlit.io)<div align="center">



**Enhanced Gamified Donation Platform with Advanced Features**[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.117-green?logo=fastapi)](https://fastapi.tiangolo.com)

## ✨ Features[![Streamlit](https://img.shields.io/badge/Streamlit-1.50-red?logo=streamlit)](https://streamlit.io)

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Platform-blue?logo=googlecloud)](https://cloud.google.com)

- 🏆 **Multi-tier System**: Bronze → Silver → Gold → Platinum progression[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

- 🎯 **Achievement Engine**: 6+ unlockable achievements with point rewards

- 💰 **Multiple Donation Types**: Money, Crypto, Goods, Time (each with bonuses)**🚀 Revolutionary AI-Powered Gamified Donation Platform**

- 🔥 **Streak System**: Daily donation streaks with multipliers

- 📊 **Real-time Analytics**: Live leaderboards and platform statistics*Combining Google A2A (Agent-to-Agent) technology with Pokemon Go-style gamification to transform charitable giving into an engaging, intelligent experience.*

- 🎨 **Modern Dashboard**: Enhanced UI with interactive features

[🎯 Live Demo](https://goodwill-platform.app) • [📚 Documentation](./docs/) • [🔧 API Reference](./docs/API_REFERENCE.md) • [🚀 Deploy Guide](./docs/DEPLOYMENT_GUIDE.md)

## 🚀 Quick Start

</div>

### 1. Install Dependencies

```bash## 🏗️ Architecture Overview

pip install -r requirements.txt

```This platform uses Google's **A2A protocol v0.3** (released April 2025) to enable seamless communication between specialized agents:



### 2. Launch Platform- **Donor Engagement Agent (DEA)**: Manages gamified donor engagement with points, tiers, and achievements

```bash- **Charity Optimization Agent (COA)**: Optimizes charity operations through demand prediction and resource allocation

python launch_platform.py

```## 🎮 Key Features



### 3. Access Platform- **Pokemon Go-style Gamification**: Location-based rewards, tier progression, achievement system

- **Enhanced Dashboard**: http://localhost:8505- **AI-Driven Optimization**: Prophet-based demand forecasting, smart inventory management

- **API Documentation**: http://localhost:8000/docs- **Real-time Engagement**: WebSocket connections, live leaderboards, instant notifications

- **Health Check**: http://localhost:8000/health- **Advanced Analytics**: Heat maps, donation patterns, performance metrics

- **Scalable Architecture**: Cloud Run microservices, Firestore real-time database

## 📁 Project Structure

## 📁 Project Structure

```

goodwillC/```

├── enhanced_backend.py       # Complete FastAPI backend v2.0goodwillC/

├── enhanced_dashboard.py     # Advanced Streamlit dashboard├── agents/                    # A2A Agent implementations

├── launch_platform.py       # One-command platform launcher│   ├── donor-engagement/      # Donor Engagement Agent (DEA)

├── simple_donation_api.py    # Basic API (alternative)│   └── charity-optimization/  # Charity Optimization Agent (COA)

├── working_dashboard.py      # Basic dashboard (alternative)├── services/                  # Backend microservices

├── demo_runner.py           # API testing utility│   ├── donation-service/      # Core donation processing

└── requirements.txt         # Minimal dependencies│   └── points-service/        # Gamification engine

```├── frontend/                  # Frontend applications

│   ├── streamlit-dashboard/   # Main dashboard

## 🎮 Gamification Features│   └── maps-integration/      # Google Maps features

├── infrastructure/            # Infrastructure as Code

### Tier System│   └── terraform/             # GCP resources

- **Bronze**: Default tier (1.0x multiplier)├── deployment/                # CI/CD and deployment

- **Silver**: $100+ donated (1.25x multiplier)  └── docs/                      # Documentation

- **Gold**: $500+ donated (1.5x multiplier)```

- **Platinum**: $2000+ donated (2.0x multiplier)

## 🚀 Quick Start

### Achievements

1. **First Steps** - Make your first donation (100 points)### Prerequisites

2. **Generous Giver** - Single donation ≥ $100 (500 points)

3. **Champion Donor** - Total donations ≥ $500 (1000 points)- Google Cloud Project with billing enabled

4. **Consistent Supporter** - Complete 10 donations (750 points)- Docker and Docker Compose

5. **Streak Master** - 7-day donation streak (1500 points)- Python 3.11+

6. **Crypto Pioneer** - Make a crypto donation (2000 points)- Node.js 18+

- Terraform 1.0+

### Point System

- **Base**: 10 points per $1 donated### Local Development Setup

- **Tier Bonus**: Multiplier based on user tier

- **Type Bonus**: Money (1.0x), Goods (1.2x), Crypto (1.5x), Time (2.0x)1. **Clone and navigate to project**

- **Streak Bonus**: Up to 500 bonus points for consecutive donations   ```bash

   cd "d:\GCP Hackathon\goodwillC"

## 🔧 API Endpoints   ```



| Endpoint | Method | Description |2. **Set up environment variables**

|----------|--------|-------------|   ```bash

| `/` | GET | Platform information |   cp .env.example .env

| `/health` | GET | System health check |   # Edit .env with your GCP project details

| `/users` | POST/GET | User management |   ```

| `/donations` | POST/GET | Donation processing |

| `/achievements` | GET | Achievement system |3. **Install dependencies**

| `/leaderboard` | GET | User rankings |   ```bash

| `/stats` | GET | Platform analytics |   pip install -r requirements.txt

   npm install

## 📊 Example Usage   ```



### Create User4. **Start local development**

```python   ```bash

import requests   docker-compose up -d

   ```

user_data = {

    "username": "john_doe",5. **Deploy infrastructure**

    "email": "john@example.com",   ```bash

    "full_name": "John Doe"   cd infrastructure/terraform

}   terraform init

   terraform plan

response = requests.post("http://localhost:8000/users", json=user_data)   terraform apply

```   ```



### Make Donation### Access Points

```python

donation_data = {- **Streamlit Dashboard**: http://localhost:8501

    "user_id": "user_id_here",- **API Documentation**: http://localhost:8000/docs

    "amount": 100.0,- **Maps Integration**: http://localhost:3000

    "donation_type": "monetary",

    "message": "Great cause!"## 📊 Platform Metrics

}

The platform is designed to achieve:

response = requests.post("http://localhost:8000/donations", json=donation_data)- **5-10% increase** in donation engagement through AI matching

```- **Sub-second response times** for all API endpoints

- **99.9% availability** with auto-scaling Cloud Run services

## 🏃 Development- **Real-time synchronization** across all connected clients



The platform uses a unified architecture with:## 🔧 Configuration

- **Single Backend**: Enhanced FastAPI service with all features

- **Single Frontend**: Advanced Streamlit dashboard### Environment Variables

- **Zero Dependencies**: No Docker, cloud services, or complex microservices

- **Instant Setup**: One command to launch everything| Variable | Description | Example |

|----------|-------------|---------|

Built with ❤️ for simplicity and functionality.| `GCP_PROJECT_ID` | Google Cloud Project ID | `donation-platform-2025` |
| `FIRESTORE_DATABASE` | Firestore database name | `(default)` |
| `A2A_DONOR_AGENT_URL` | DEA service URL | `https://dea.donationplatform.com` |
| `A2A_CHARITY_AGENT_URL` | COA service URL | `https://coa.donationplatform.com` |
| `GOOGLE_MAPS_API_KEY` | Maps JavaScript API key | `AIza...` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Contact the development team
- Check the [documentation](docs/)

---

Built with ❤️ using Google Cloud Platform and cutting-edge AI technologies.