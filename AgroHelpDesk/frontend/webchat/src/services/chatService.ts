import { API_ENDPOINTS } from '../constants';
import type {
    MessageHistoryResponse,
    SendMessageResponse,
    StartSessionResponse,
} from '../types';
import api from './api';

/**
 * Service for chat operations with AgroHelpDesk backend
 */
export const chatService = {
    /**
     * Start a new chat session
     */
    async startSession(): Promise<StartSessionResponse> {
        const response = await api.post<StartSessionResponse>(API_ENDPOINTS.START_SESSION);
        return response.data;
    },

    /**
     * Send a message to the chat
     */
    async sendMessage(
        sessionId: string,
        message: string,
        userId?: string
    ): Promise<SendMessageResponse> {
        const response = await api.post<SendMessageResponse>(API_ENDPOINTS.SEND_MESSAGE, {
            session_id: sessionId,
            message,
            user_id: userId,
        });
        return response.data;
    },

    /**
     * Get message history for a session
     */
    async getHistory(sessionId: string): Promise<MessageHistoryResponse> {
        const response = await api.get<MessageHistoryResponse>(
            `${API_ENDPOINTS.GET_HISTORY}/${sessionId}`
        );
        return response.data;
    },

    /**
     * Close a chat session
     */
    async closeSession(sessionId: string): Promise<{ ok: boolean; message: string }> {
        const response = await api.post<{ ok: boolean; message: string }>(
            `${API_ENDPOINTS.CLOSE_SESSION}/${sessionId}`
        );
        return response.data;
    },

    /**
     * Generate a unique user ID
     */
    generateUserId(): string {
        return `user-${Date.now()}-${Math.random().toString(36).substring(7)}`;
    },
};
