# AgroHelpdesk

Modern React frontend (Vite + Material UI) that demonstrates an **auto‑resolve service desk for agribusiness**, built for the **Microsoft Hackathon – Innovation Studio, Nov 2025**.

![Screen Workflow](assets/Screen.png)

## 💡 Problem & Vision

Large farms receive hundreds of repetitive, multi‑channel support requests: pest diagnosis, equipment failures, stock checks, and compliance tasks.  
Most calls are low‑complexity, but still consume agronomists’ time and delay decisions in the field.

**AgroHelpdesk** turns this into an **AI‑first, auto‑resolving service desk** that:

- Classifies and routes tickets automatically.
- Orchestrates multiple specialized agents (diagnosis, knowledge, runbooks, explainability).
- Escalates only the critical or ambiguous cases to humans.
- Keeps full transparency of every decision for supervisors and regulators.

---

## 🚀 Main Capabilities 

- **Agent‑Aware Dashboard**
   - List of tickets with status, channel (Teams, WhatsApp, ERP), crop, and location.
   - Right panel with **Details**: issue type, decision taken, agronomic context.
   - **Agent Timeline** showing which agent acted (FieldSense, FarmOps, AgroBrain, RunbookMaster, ExplainIt) and when.

- **Chat Simulation**
   - End‑to‑end conversation per ticket (farmer ↔ AI ↔ operator).
   - Mimics WhatsApp / Teams styles using mock data from the challenge.
   - Swapping tickets instantly updates the chat and agent history.

- **Metrics Dashboard**
   - KPIs demonstrating business impact:
      - Ticket reduction (auto‑resolved)
      - Average resolution time
      - Classification accuracy
      - Escalation rate
   - Symptom ranking by machine type (harvester, planter, sprayer) to show how data reveals patterns.

- **Field Plot Map**
   - Interactive Leaflet map with OpenStreetMap tiles.
   - Plots with markers, crops, and alert status (normal, pest, maintenance).
   - Ready to plug in GPS, weather APIs, or IoT telemetry.

- **Transparency by Design**
   - For each ticket we show:
      - Which agents ran,
      - What they did,
      - How long each step took,
      - What final decision was made (auto‑resolve, escalate, open work order, etc.).

---

## 🧠 Multi‑Agent Orchestration (Concept)

The frontend showcases how the backend/agent layer behaves, using mock data to simulate **Semantic Kernel + Azure OpenAI** agents:

- **FieldSense – Intent Agent**  
   Classifies the farmer’s request (pest, machine, stock, compliance).

- **FarmOps – Info Collector**  
   Asks clarifying questions and enriches the ticket with context: crop, stage, images, telemetry.

- **AgroBrain – Knowledge Agent**  
   Consults agronomic knowledge bases, labels, and internal docs to propose recommendations.

- **RunbookMaster – Decision & Automation**  
   Chooses and executes the right runbook: create work order, generate report, schedule visit, etc.

- **ExplainIt – Transparency Agent**  
   Translates the AI pipeline into human‑readable explanations for supervisors and auditors.

---

## ⚙️ Mock Runbooks (Examples)

These runbooks are mocked in the frontend to illustrate decision flows:

- **RB‑01 – Generate Pest Report (Safe)**  
   Builds a technical recommendation with product, dose, and interval.

- **RB‑02 – Open Urgent Work Order (Critical)**  
   Creates a high‑priority ticket for machinery or field visit.

- **RB‑03 – Inventory Check (Safe)**  
   Verifies availability of inputs and suggests replenishment.

- **RB‑04 – Pre‑fill ART Report (Critical)**  
   Assists with regulatory paperwork, requiring agronomist sign‑off.

- **RB‑05 – Compliance Check (Critical)**  
   Validates licenses and environmental permits.

---

## 📊 Mock Metrics (Business Impact)

The metrics page simulates the first weeks of operation:

- **Ticket reduction:** **65%** of repetitive calls are auto‑resolved.
- **Average resolution time:** **12 minutes** (vs. hours in manual triage).
- **Classification accuracy:** **92%** of tickets correctly routed.
- **Escalated:** **8%** go to a human expert (critical/ambiguous).

These numbers are illustrative for the hackathon, but reflect realistic targets for an AI‑augmented support desk.

---

## 🗺️ Field Plot Map

- Built with **Leaflet** and OpenStreetMap.
- Each plot displays:
   - Plot ID,
   - Crop,
   - Status (normal / alert),
   - Short description.
- Designed to integrate with:
   - GPS boundaries,
   - Weather and disease risk indices,
   - Machinery and sensor data.

---

## 🧱 Tech Stack

- **Frontend:** React + Vite
- **UI:** Material‑UI (MUI) with custom green/agri theme
- **Routing:** React Router
- **Maps:** Leaflet
- **State & Data:** Local mock data (`src/mockData.js`)

This repository focuses on the **experience layer** of the auto‑resolve desk.  
The backend/agents are represented conceptually (AgroHelpDesk backend folder) and can be wired later to real Azure services.

---

## 💻 How to Run (PowerShell – Windows)

From the project root:

```powershell
cd e:\projects\HackathonMicrosoftNov2025\web-frontend
npm install
npm run dev
```

Open the browser at: `http://localhost:5173`.

Build & preview:

```powershell
npm run build
npm run preview
```

---

## 🎨 Design Highlights

- Material‑UI theme with agricultural green accents.
- Responsive layout with permanent/temporary sidebar depending on screen size.
- Cards, chips, badges, and progress bars that reflect ticket state and agent progress.
- Layouts designed specifically for **demo storytelling**.

---

## 🔭 Next Steps (Post‑Hackathon)

- Validate flows with real farmers and support teams, collecting feedback and sample conversations.
- Add authentication and roles (Operator, Agronomist, Supervisor).
- Replace mock images with real field photos.
- Integrate official WhatsApp/Teams channels through Azure Communication Services.
- Persist ticket and agent runs for full auditability.

---

Powered by **React + Vite + Material‑UI**.  
Created for the **Microsoft Innovation Studio Hackathon – Nov 2025** to demonstrate an **AI‑orchestrated, transparent, auto‑resolving service desk for agribusiness**.
