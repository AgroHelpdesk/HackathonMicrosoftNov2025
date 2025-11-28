export const AGENTS = [
  { id: 'field-sense', name: 'FieldSense', role: 'Intent Agent' },
  { id: 'farm-ops', name: 'FarmOps', role: 'Info Collector' },
  { id: 'agro-brain', name: 'AgroBrain', role: 'Knowledge Agent' },
  { id: 'runbook-master', name: 'RunbookMaster', role: 'Decision Agent' },
  { id: 'explain-it', name: 'ExplainIt', role: 'Transparency Agent' }
]

export const TICKETS = [
  {
    id: 'T-001',
    type: 'Field Diagnosis',
    summary: 'Leaf photos with spots, possible fungus',
    channel: 'Microsoft Teams',
    location: 'Plot 22',
    crop: 'Soybean',
    stage: 'V5',
    images: ['/images/leaf-1.jpg'],
    steps: [
      { agent: 'field-sense', text: 'Identified phytosanitary intention', ts: '2025-11-14T08:05:00' },
      { agent: 'farm-ops', text: 'Requested crop, age and additional photo', ts: '2025-11-14T08:06:12' }
    ],
    status: 'open',
    decision: null
  },
  {
    id: 'T-002',
    type: 'Equipment Failure',
    summary: 'Harvester vibrating',
    channel: 'WhatsApp',
    location: 'Plot 12',
    crop: 'Corn',
    images: ['/images/machine-1.jpg'],
    steps: [
      { agent: 'field-sense', text: 'Mechanical failure detected', ts: '2025-11-14T06:02:11' },
      { agent: 'farm-ops', text: 'Collected telemetry and last service', ts: '2025-11-14T06:03:33' }
    ],
    status: 'open',
    decision: 'escalate'
  },
  {
    id: 'T-003',
    type: 'Input Stock',
    summary: 'Low urea in warehouse',
    channel: 'ERP',
    location: 'North Warehouse',
    crop: 'Various',
    images: [],
    steps: [
      { agent: 'field-sense', text: 'Stock request', ts: '2025-11-13T12:01:01' },
      { agent: 'agro-brain', text: 'Checking consumption and forecast', ts: '2025-11-13T12:02:10' }
    ],
    status: 'resolved',
    decision: 'auto-order'
  }
]

export const RUNBOOKS = [
  {
    id: 'RB-01',
    name: 'Generate Pest Report',
    description: 'Analyzes image and produces preliminary report with georeferenced points',
    safe: true
  },
  {
    id: 'RB-02',
    name: 'Open Urgent Work Order',
    description: 'Creates a work order and notifies on-duty mechanic',
    safe: false
  },
  {
    id: 'RB-03',
    name: 'Stock Inquiry',
    description: 'Checks balance and suggests automatic replenishment',
    safe: true
  },
  {
    id: 'RB-04',
    name: 'Pre-fill ART',
    description: 'Generates preliminary PDF for signature',
    safe: false
  },
    {
    id: 'RB-05',
    name: 'Compliance Check',
    description: 'Validates licenses and environmental permits',
    safe: false
  }
]

export const METRICS = {
  reduction: 65,
  avgResolutionTime: 12,
  accuracy: 92,
  escalated: 8,
  topSymptoms: [
    { machine: 'Harvester', symptom: 'Vibration', percentage: 45 },
    { machine: 'Planter', symptom: 'Sensor Failure', percentage: 30 },
    { machine: 'Sprayer', symptom: 'Leakage', percentage: 15 }
  ]
}

export const TALHOES = [
  { id: 'T-22', crop: 'Soybean', status: 'Pest Alert', lat: -22.5, lng: -47.5 },
  { id: 'T-12', crop: 'Corn', status: 'Maintenance', lat: -22.6, lng: -47.6 },
  { id: 'T-07', crop: 'Cotton', status: 'Normal', lat: -22.7, lng: -47.7 }
]
