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
    }
};
