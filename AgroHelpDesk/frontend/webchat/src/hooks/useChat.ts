import { useCallback, useRef, useState } from 'react';
import { APP_CONFIG, ERROR_MESSAGES } from '../constants';
import { chatService } from '../services';
import type { ChatMessage, ChatStatus } from '../types';

interface UseChatReturn {
    sessionId: string | null;
    messages: ChatMessage[];
    chatStatus: ChatStatus;
    isLoading: boolean;
    isSending: boolean;
    error: string | null;
    startSession: () => Promise<void>;
    sendMessage: (message: string) => Promise<void>;
    resetChat: () => void;
}

/**
 * Hook for managing chat state and operations
 */
export const useChat = (): UseChatReturn => {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [chatStatus, setChatStatus] = useState<ChatStatus>('active');
    const [isLoading, setIsLoading] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [userId] = useState(() => chatService.generateUserId());
    const isStartingSession = useRef(false);

    const startSession = useCallback(async () => {
        // Prevent multiple simultaneous session starts
        if (isStartingSession.current) {
            console.log('Session already starting:', { isStarting: isStartingSession.current });
            return;
        }

        isStartingSession.current = true;

        try {
            setIsLoading(true);
            setError(null);

            const data = await chatService.startSession();
            setSessionId(data.session_id);

            // Add welcome message
            const welcomeMessage: ChatMessage = {
                id: `msg-${Date.now()}`,
                content: `Hello! I am ${APP_CONFIG.BOT_NAME}, your agricultural assistant. How can I help you today?`,
                sender: APP_CONFIG.BOT_NAME,
                timestamp: new Date(),
                isBot: true,
            };
            setMessages([welcomeMessage]);
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? `${ERROR_MESSAGES.SESSION_FAILED}: ${err.message}`
                    : ERROR_MESSAGES.SESSION_FAILED;
            setError(errorMessage);
        } finally {
            setIsLoading(false);
            isStartingSession.current = false;
        }
    }, []);

    const sendMessage = useCallback(
        async (message: string) => {
            if (!sessionId || !message.trim()) return;

            try {
                setIsSending(true);
                setError(null);

                // Add user message
                const userMessage: ChatMessage = {
                    id: `msg-${Date.now()}`,
                    content: message,
                    sender: APP_CONFIG.DEFAULT_USER_NAME,
                    timestamp: new Date(),
                    isBot: false,
                };
                setMessages((prev) => [...prev, userMessage]);

                // Send to backend
                const response = await chatService.sendMessage(sessionId, message, userId);

                console.log('Response flow_state:', response.flow_state); // Debug log

                // Add bot response
                const botMessage: ChatMessage = {
                    id: `msg-${Date.now() + 1}`,
                    content: response.reply,
                    sender: APP_CONFIG.BOT_NAME,
                    timestamp: new Date(),
                    isBot: true,
                };
                setMessages((prev) => [...prev, botMessage]);

                // Check if chat should be closed based on flow_state
                if (response.flow_state === 'completed') {
                    console.log('Closing chat - flow completed');
                    setChatStatus('closed');

                    // Close session on backend
                    try {
                        await chatService.closeSession(sessionId);
                        console.log('Session closed on backend');
                    } catch (error) {
                        console.error('Failed to close session on backend:', error);
                    }
                }
            } catch (err) {
                const errorMessage =
                    err instanceof Error
                        ? `${ERROR_MESSAGES.SEND_FAILED}: ${err.message}`
                        : ERROR_MESSAGES.SEND_FAILED;
                setError(errorMessage);

                // Add error message to chat
                const errorMsg: ChatMessage = {
                    id: `msg-${Date.now()}`,
                    content: errorMessage,
                    sender: 'Sistema',
                    timestamp: new Date(),
                    isBot: true,
                    isError: true,
                };
                setMessages((prev) => [...prev, errorMsg]);
            } finally {
                setIsSending(false);
            }
        },
        [sessionId, userId]
    );

    const resetChat = useCallback(() => {
        setSessionId(null);
        setMessages([]);
        setChatStatus('active');
        setError(null);
        setIsLoading(false);
        setIsSending(false);
        isStartingSession.current = false; // Reset the flag
    }, []);

    return {
        sessionId,
        messages,
        chatStatus,
        isLoading,
        isSending,
        error,
        startSession,
        sendMessage,
        resetChat,
    };
};
