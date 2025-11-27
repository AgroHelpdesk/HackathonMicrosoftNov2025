import { Activity, MessageSquare } from 'lucide-react';
import React from 'react';
import type { ChatStatus } from '../../types';

interface ChatHeaderProps {
    sessionId: string | null;
    chatStatus: ChatStatus;
}

/**
 * Chat header component displaying status and session info
 */
export const ChatHeader: React.FC<ChatHeaderProps> = ({ sessionId, chatStatus }) => {
    return (
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
                <MessageSquare className="w-6 h-6" />
                <div>
                    <h2 className="text-lg font-semibold">Customer Service Chat</h2>
                    {sessionId && (
                        <p className="text-xs text-green-100">Session: {sessionId.substring(0, 8)}...</p>
                    )}
                </div>
            </div>
            <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 animate-pulse" />
                <span className="text-sm font-medium">
                    {chatStatus === 'active' ? 'Active' : 'Closed'}
                </span>
            </div>
        </div>
    );
};
