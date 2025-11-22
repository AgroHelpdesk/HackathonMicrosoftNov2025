const API_URL = 'http://localhost:8000/api';

export const api = {
    getTickets: async () => {
        const response = await fetch(`${API_URL}/tickets`);
        return response.json();
    },
    getAgents: async () => {
        const response = await fetch(`${API_URL}/agents`);
        return response.json();
    },
    getRunbooks: async () => {
        const response = await fetch(`${API_URL}/runbooks`);
        return response.json();
    },
    getMetrics: async () => {
        const response = await fetch(`${API_URL}/metrics`);
        return response.json();
    },
    getPlots: async () => {
        const response = await fetch(`${API_URL}/plots`);
        return response.json();
    },
    sendMessage: async (message, ticketId) => {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message, ticketId }),
        });
        return response.json();
    },
    // Emulated Azure Functions
    sendACSChatMessage: async (threadId, message) => {
        const response = await fetch(`${API_URL}/acs/chat/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ thread_id: threadId, message }),
        });
        return response.json();
    },
    triggerACSWebhook: async (eventType, data) => {
        const response = await fetch(`${API_URL}/acs/chat/webhook`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ eventType, data }),
        });
        return response.json();
    },
    // Workflow Emulation
    getWorkflowState: async (ticketId) => {
        const response = await fetch(`${API_URL}/workflow/${ticketId}`);
        return response.json();
    },
    advanceWorkflow: async (ticketId) => {
        const response = await fetch(`${API_URL}/workflow/${ticketId}/advance`, {
            method: 'POST',
        });
        return response.json();
    },
    resetWorkflow: async (ticketId) => {
        const response = await fetch(`${API_URL}/workflow/${ticketId}/reset`, {
            method: 'POST',
        });
        return response.json();
    }
};
