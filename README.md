# Google A2A Gamified Goodwill Platform

# 🎮 Google A2A Gamified Goodwill Platform

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.117-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50-red?logo=streamlit)](https://streamlit.io)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Platform-blue?logo=googlecloud)](https://cloud.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**🚀 Revolutionary AI-Powered Gamified Donation Platform**

*Combining Google A2A (Agent-to-Agent) technology with Pokemon Go-style gamification to transform charitable giving into an engaging, intelligent experience.*

[🎯 Live Demo](https://goodwill-platform.app) • [📚 Documentation](./docs/) • [🔧 API Reference](./docs/API_REFERENCE.md) • [🚀 Deploy Guide](./docs/DEPLOYMENT_GUIDE.md)

</div>

## 🏗️ Architecture Overview

This platform uses Google's **A2A protocol v0.3** (released April 2025) to enable seamless communication between specialized agents:

- **Donor Engagement Agent (DEA)**: Manages gamified donor engagement with points, tiers, and achievements
- **Charity Optimization Agent (COA)**: Optimizes charity operations through demand prediction and resource allocation

## 🎮 Key Features

- **Pokemon Go-style Gamification**: Location-based rewards, tier progression, achievement system
- **AI-Driven Optimization**: Prophet-based demand forecasting, smart inventory management
- **Real-time Engagement**: WebSocket connections, live leaderboards, instant notifications
- **Advanced Analytics**: Heat maps, donation patterns, performance metrics
- **Scalable Architecture**: Cloud Run microservices, Firestore real-time database

## 📁 Project Structure

```
goodwillC/
├── agents/                    # A2A Agent implementations
│   ├── donor-engagement/      # Donor Engagement Agent (DEA)
│   └── charity-optimization/  # Charity Optimization Agent (COA)
├── services/                  # Backend microservices
│   ├── donation-service/      # Core donation processing
│   └── points-service/        # Gamification engine
├── frontend/                  # Frontend applications
│   ├── streamlit-dashboard/   # Main dashboard
│   └── maps-integration/      # Google Maps features
├── infrastructure/            # Infrastructure as Code
│   └── terraform/             # GCP resources
├── deployment/                # CI/CD and deployment
└── docs/                      # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Google Cloud Project with billing enabled
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Terraform 1.0+

### Local Development Setup

1. **Clone and navigate to project**
   ```bash
   cd "d:\GCP Hackathon\goodwillC"
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your GCP project details
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. **Start local development**
   ```bash
   docker-compose up -d
   ```

5. **Deploy infrastructure**
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform plan
   terraform apply
   ```

### Access Points

- **Streamlit Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Maps Integration**: http://localhost:3000

## 📊 Platform Metrics

The platform is designed to achieve:
- **5-10% increase** in donation engagement through AI matching
- **Sub-second response times** for all API endpoints
- **99.9% availability** with auto-scaling Cloud Run services
- **Real-time synchronization** across all connected clients

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | `donation-platform-2025` |
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