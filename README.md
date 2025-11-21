# Agro Auto-Resolve

[![Infrastructure CI/CD](https://github.com/YOUR_USERNAME/HackathonMicrosoftNov2025/actions/workflows/infrastructure-ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/HackathonMicrosoftNov2025/actions/workflows/infrastructure-ci-cd.yml)
[![Backend CI/CD](https://github.com/YOUR_USERNAME/HackathonMicrosoftNov2025/actions/workflows/backend-ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/HackathonMicrosoftNov2025/actions/workflows/backend-ci-cd.yml)
[![Frontend CI/CD](https://github.com/YOUR_USERNAME/HackathonMicrosoftNov2025/actions/workflows/frontend-ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/HackathonMicrosoftNov2025/actions/workflows/frontend-ci-cd.yml)

A complete solution for **"Auto-resolve Service Desk for Agribusiness and Agriculture"** challenge at Microsoft Hackathon Nov 2025.

## 🏗️ Architecture

- **Frontend**: React + Vite + Material-UI → Azure Static Web Apps
- **Backend**: FastAPI (Python 3.11) → Azure Functions
- **Infrastructure**: Azure Bicep (IaC)
- **CI/CD**: GitHub Actions
- **Database**: Azure Cosmos DB (Serverless)
- **Search**: Azure Cognitive Search
- **AI**: Azure OpenAI (optional)

## 🚀 Features

* **Main Dashboard**: Ticket list with agents, runbooks, and interactive details.
* **Chat Simulation**: Mock conversations based on the challenge examples (WhatsApp/Teams style).
* **Metrics Dashboard**: KPIs such as ticket reduction, response time, accuracy, symptom ranking.
* **Field Plot Map**: Interactive Leaflet map showing plots with markers and popups (active alerts).
* **Full Transparency**: Step-by-step logs for each agent in each ticket.
* **Navigation**: React Router with multiple pages.

## 🧠 Demonstrated Agents

* **FieldSense** (Intent): Classifies user requests.
* **FarmOps** (Info Collector): Gathers missing information.
* **AgroBrain** (Knowledge): Queries knowledge bases.
* **RunbookMaster** (Decision): Chooses automation or escalation.
* **ExplainIt** (Transparency): Explains each step taken.

## ⚙️ Mock Runbooks

* **RB-01**: Generate pest report (Safe).
* **RB-02**: Open urgent work order (Critical).
* **RB-03**: Inventory check (Safe).
* **RB-04**: Pre-fill ART report (Critical).
* **RB-05**: Check licences, deadlines, and compliance with environmental permit conditions (Safe).

## 📊 Mock Metrics

* Ticket reduction: **65%**
* Average resolution time: **12 minutes**
* Classification accuracy: **92%**
* Escalated: **8%**

## 🗺️ Field Plot Map

* Integrated with Leaflet (OpenStreetMap tiles).
* Markers for each plot with popups showing ID, crop, and status.
* Visual alerts: Normal (green), Pest/Maintenance (yellow/red).
* Ready for integration with GPS or weather APIs.

## 💻 Quick Start

### Frontend

```bash
cd web-frontend
npm install
npm run dev  # Opens http://localhost:5173
```

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py  # Runs on http://localhost:8000
```

### Infrastructure

```bash
cd infrastructure/bicep

# Login to Azure
az login

# Create resource group
az group create --name rg-agroautoresolve-dev --location brazilsouth

# Deploy infrastructure
az deployment group create \
  --resource-group rg-agroautoresolve-dev \
  --template-file main.bicep \
  --parameters parameters.dev.json
```

See [infrastructure/bicep/README.md](infrastructure/bicep/README.md) for detailed instructions.

## 🔄 CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

- **Infrastructure CI/CD**: Validates and deploys Bicep templates to Azure
- **Backend CI/CD**: Tests, builds, and deploys FastAPI to Azure Functions
- **Frontend CI/CD**: Builds and deploys React app to Azure Static Web Apps
- **PR Validation**: Validates all components on pull requests

### Setup CI/CD

1. **Create Azure Service Principal**:
   ```bash
   az ad sp create-for-rbac \
     --name "github-actions-agro-autoresolve" \
     --role contributor \
     --scopes /subscriptions/YOUR_SUBSCRIPTION_ID \
     --sdk-auth
   ```

2. **Configure GitHub Secrets**:
   - `AZURE_CREDENTIALS`: JSON output from step 1
   - `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
   - `AZURE_STATIC_WEB_APPS_API_TOKEN`: Token from Static Web App

3. **Push to main branch** to trigger automatic deployment

See [CICD.md](CICD.md) for complete CI/CD documentation.

## 📁 Project Structure

```
HackathonMicrosoftNov2025/
├── .github/
│   └── workflows/          # GitHub Actions workflows
│       ├── infrastructure-ci-cd.yml
│       ├── backend-ci-cd.yml
│       ├── frontend-ci-cd.yml
│       └── pr-validation.yml
├── backend/                # FastAPI backend
│   ├── data_processing/    # CSV and PDF processors
│   ├── functions/          # Azure Functions
│   ├── models/             # Data models
│   ├── tests/              # Unit tests
│   ├── main.py             # FastAPI app
│   └── requirements.txt
├── web-frontend/           # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.jsx
│   │   └── mockData.js
│   └── package.json
├── infrastructure/
│   └── bicep/              # Azure Bicep templates
│       ├── main.bicep
│       ├── parameters.dev.json
│       ├── parameters.prod.json
│       └── README.md
├── dataset/                # Sample data (CSV, PDF)
├── CICD.md                 # CI/CD documentation
└── README.md
```

## 🎨 Design

* Material-UI theme with agricultural-green tones.
* Responsive layout with a side Drawer.
* Cards, Chips, and Progress Bars for rich visualization.

## 🔧 Next Steps

* Integrate real APIs (telemetry, ERP, weather).
* Add authentication (roles: operator, agronomist, admin).
* Upload real images for diagnostics.
* Push notifications for alerts.
* Integrate WhatsApp API for real chat automation.
* Improve map: clusters, pest heatmaps, IoT sensor integration.

## 📚 Documentation

- [CI/CD Setup Guide](CICD.md)
- [Infrastructure Documentation](infrastructure/bicep/README.md)
- [Backend API Documentation](backend/README.md) (to be created)

## 🛠️ Technologies

- **Frontend**: React 18, Vite 5, Material-UI 7, Leaflet
- **Backend**: FastAPI, Python 3.11, Pydantic
- **Infrastructure**: Azure Bicep, Azure CLI
- **CI/CD**: GitHub Actions
- **Cloud**: Azure (Functions, Cosmos DB, Cognitive Search, Static Web Apps)

---

**Powered by React + Vite + Material-UI + FastAPI + Azure**  
A complete demo for the **Microsoft Hackathon Nov 2025 Challenge**.
