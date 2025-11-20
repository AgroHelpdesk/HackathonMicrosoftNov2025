# Agro Auto-Resolve - Azure Implementation Plan

This document outlines the roadmap to transform the current React mock application into a fully functional, cloud-native solution on Microsoft Azure.

## 1. Architecture Overview

We will use a **Serverless Architecture** to minimize cost and maintenance while maximizing scalability.

### Core Components
*   **Frontend**: Azure Static Web Apps (hosting the Vite/React app).
*   **Backend**: Azure Functions (Python) for API endpoints.
*   **Database**: Azure Cosmos DB (NoSQL) for ticket management, users, and operational data.
*   **Storage**: Azure Blob Storage for images (pest photos, equipment issues) and raw documents (PDFs, CSVs).
*   **AI & Search**:
    *   **Azure OpenAI Service**: For the "Agents" logic (FieldSense, FarmOps, etc.).
    *   **Azure AI Search**: For RAG (Retrieval-Augmented Generation) over the `dataset` folder (PDFs/CSVs).

## 2. Data Strategy (The `dataset` folder)

The current `dataset` folder contains valuable knowledge that needs to be accessible to the AI agents.

### Ingestion Pipeline
1.  **Upload**: Move `dataset/*.pdf` and `dataset/*.csv` to Azure Blob Storage.
2.  **Indexing**:
    *   Use **Azure AI Document Intelligence** to parse PDFs (manuals, technical specs).
    *   Use **Azure AI Search** with vectorization to index the content.
    *   CSVs (like `basedeconhecimentoMAPA.csv`) will be converted to structured JSON or text chunks for indexing.

### Retrieval (RAG)
*   When a user asks a question, **AgroBrain** (Knowledge Agent) will query Azure AI Search.
*   Relevant chunks are retrieved and sent to Azure OpenAI (GPT-4o) to generate the answer.

## 3. Backend Implementation (Azure Functions)

We will replace `src/mockData.js` with real API calls.

### API Endpoints
*   `GET /api/tickets`: List all tickets (replaces `TICKETS` array).
*   `GET /api/tickets/{id}`: Get details.
*   `POST /api/tickets`: Create new ticket.
*   `POST /api/chat`: Send message to agents.
    *   *Logic*: This function orchestrates the agents. It decides if it needs `FieldSense` (intent), `AgroBrain` (search), or `RunbookMaster` (action).
*   `GET /api/metrics`: Calculate real-time metrics from Cosmos DB.
*   `GET /api/plots`: GeoJSON data for the map.

## 4. Frontend Integration

### Changes Required
1.  **API Client**: Create a `services/api.js` to handle Axios/Fetch requests to the Azure Functions.
2.  **State Management**: Refactor components to load data asynchronously (using `useEffect` or React Query) instead of importing from `mockData.js`.
3.  **Authentication**: Implement **MSAL (Microsoft Authentication Library)** to log in users via Azure Active Directory (Entra ID).

## 5. Specific Agent Implementation

*   **FieldSense (Intent)**:
    *   *Azure*: GPT-4o system prompt to classify input text into categories (Phytosanitary, Mechanical, Stock).
*   **AgroBrain (Knowledge)**:
    *   *Azure*: RAG implementation querying the indexed `dataset`.
*   **RunbookMaster (Decision)**:
    *   *Azure*: GPT-4o with "Function Calling" capabilities to trigger specific actions (e.g., "Send Email", "Create Work Order").

## 6. Maps & Geospatial

*   **Current**: Leaflet with static markers.
*   **Future**:
    *   Keep Leaflet for frontend rendering (cost-effective).
    *   Backend serves dynamic GeoJSON based on database records.
    *   Integration with **Azure Maps Weather Service** to overlay real-time weather data on the plots.

## 7. Deployment Pipeline (CI/CD)

*   **GitHub Actions**:
    *   On push to `main`:
        1.  Build React App.
        2.  Deploy to Azure Static Web Apps.
        3.  Deploy Azure Functions.

## 8. Next Steps (Phased Approach)

1.  **Phase 1: Foundation**: Set up Azure resources (Cosmos, Storage, OpenAI) and connect a basic "Hello World" API.
2.  **Phase 2: Data Ingestion**: Index the `dataset` files into Azure AI Search.
3.  **Phase 3: Agent Logic**: Implement the Chat API with RAG.
4.  **Phase 4: Frontend Wiring**: Replace mock data with real API calls.
