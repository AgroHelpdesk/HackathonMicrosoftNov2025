import { MessageCircle, Sprout, User } from 'lucide-react';
import React from 'react';
import type { ChatMessage as ChatMessageType } from '../../types';

interface ChatMessageProps {
    message: ChatMessageType;
}

/**
 * Individual chat message component
 */
export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
    return (
        <div className={`flex ${message.isBot ? 'justify-start' : 'justify-end'} animate-fade-in`}>
            <div className="flex items-start space-x-3 max-w-3xl">
                {message.isBot && (
                    <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
                        <Sprout className="w-5 h-5 text-white" />
                    </div>
                )}
                <div
                    className={`px-5 py-3 rounded-2xl shadow-sm ${message.isBot
                        ? message.isError
                            ? 'bg-red-100 text-red-800 border border-red-200'
                            : 'bg-white text-gray-800 border border-green-100 shadow-md'
                        : 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-md'
                        }`}
                >
                    <div className="text-sm">
                        <div className="font-semibold text-xs mb-2 opacity-75 flex items-center space-x-1">
                            {message.isBot && <MessageCircle className="w-3 h-3" />}
                            <span>{message.sender}</span>
                            {message.agentType && (
                                <span className="bg-green-200 text-green-800 px-2 py-0.5 rounded-full text-xs">
                                    {message.agentType}
                                </span>
                            )}
                        </div>
                        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                        <div className="text-xs opacity-60 mt-2">
                            {message.timestamp.toLocaleTimeString('en-US')}
                        </div>
                    </div>
                </div>
                {!message.isBot && (
                    <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-green-600 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
                        <User className="w-5 h-5 text-white" />
                    </div>
                )}
            </div>
        </div>
    );
};
