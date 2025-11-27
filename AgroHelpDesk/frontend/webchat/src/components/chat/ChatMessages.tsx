import React from 'react';
import { useAutoScroll } from '../../hooks';
import type { ChatMessage as ChatMessageType } from '../../types';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';

interface ChatMessagesProps {
    messages: ChatMessageType[];
    isSending: boolean;
}

/**
 * Chat messages container with auto-scroll
 */
export const ChatMessages: React.FC<ChatMessagesProps> = ({ messages, isSending }) => {
    const scrollRef = useAutoScroll<HTMLDivElement>([messages, isSending]);

    return (
        <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-white to-green-50 scrollbar-thin"
            style={{ height: '500px' }}
        >
            {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
            ))}
            {isSending && (
                <div className="flex justify-start">
                    <TypingIndicator />
                </div>
            )}
        </div>
    );
};
