/**
 * API Client Service
 * Handles communication with the backend Chat API
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:7071/api'

class ApiClient {
    constructor() {
        this.baseUrl = API_BASE_URL
    }

    /**
     * Send a chat message to the backend
     * @param {string} message - User message
     * @param {object} context - Optional context (plotId, crop, etc.)
     * @param {string} ticketId - Optional ticket ID
     * @returns {Promise<object>} - Chat response with agent data
     */
    async sendMessage(message, context = null, ticketId = null) {
        try {
            const response = await fetch(`${this.baseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    context,
                    ticketId
                })
            })

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
            }

            return await response.json()
        } catch (error) {
            console.error('Error sending message:', error)
            throw error
        }
    }

    /**
     * Health check endpoint
     * @returns {Promise<object>} - Health status
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`)

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            return await response.json()
        } catch (error) {
            console.error('Health check failed:', error)
            throw error
        }
    }

    /**
     * Format agent response for display
     * @param {object} chatResponse - Response from backend
     * @returns {object} - Formatted response
     */
    formatAgentResponse(chatResponse) {
        const { response, agents, suggestedActions } = chatResponse

        // Extract agent details
        const agentDetails = agents.map(agent => ({
            name: agent.name,
            data: agent.data,
            executionTime: agent.executionTime
        }))

        // Find specific agent data
        const fieldSense = agents.find(a => a.name === 'FieldSense')
        const agroBrain = agents.find(a => a.name === 'AgroBrain')
        const runbookMaster = agents.find(a => a.name === 'RunbookMaster')

        return {
            message: response,
            intent: fieldSense?.data?.intent || 'Unknown',
            confidence: fieldSense?.data?.confidence || 0,
            sources: agroBrain?.data?.sources || [],
            action: runbookMaster?.data?.action || 'None',
            riskLevel: runbookMaster?.data?.riskLevel || 'Unknown',
            suggestedActions: suggestedActions || [],
            agents: agentDetails
        }
    }
}

// Export singleton instance
export const apiClient = new ApiClient()
export default apiClient
