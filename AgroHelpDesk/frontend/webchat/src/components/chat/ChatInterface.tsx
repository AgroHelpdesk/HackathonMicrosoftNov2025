import React, { useEffect } from 'react';
import { LOADING_MESSAGES, UI_CONFIG } from '../../constants';
import { useChat } from '../../hooks';
import { ErrorDisplay, LoadingState } from '../common';
import { ChatClosedView } from './ChatClosedView';
import { ChatHeader } from './ChatHeader';
import { ChatInput } from './ChatInput';
import { ChatMessages } from './ChatMessages';

/**
 * Main chat interface component
 */
export const ChatInterface: React.FC = () => {
    const {
        sessionId,
        messages,
        chatStatus,
        isLoading,
        isSending,
        error,
        startSession,
        sendMessage,
        resetChat,
    } = useChat();

    // Initialize session on mount
    useEffect(() => {
        if (!sessionId) {
            startSession();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Handle chat reset
    const handleReset = () => {
        resetChat();
        startSession();
    };

    // Loading state
    if (isLoading && !sessionId) {
        return <LoadingState message={LOADING_MESSAGES.STARTING_SESSION} />;
    }

    // Error state
    if (error && !sessionId) {
        return <ErrorDisplay error={error} onRetry={startSession} />;
    }

    // Main chat interface
    return (
        <div
            className="flex flex-col bg-gradient-to-b from-white to-green-50"
            style={{ height: UI_CONFIG.CHAT_HEIGHT }}
        >
            <ChatHeader sessionId={sessionId} chatStatus={chatStatus} />

            <ChatMessages messages={messages} isSending={isSending} />

            <div className="bg-white border-t border-green-100 p-4">
                {chatStatus === 'closed' ? (
                    <ChatClosedView onReset={handleReset} />
                ) : (
                    <ChatInput onSendMessage={sendMessage} disabled={isSending} />
                )}
            </div>
        </div>
    );
};
