import { RefreshCw } from 'lucide-react';
import React from 'react';

interface ChatClosedViewProps {
    onReset: () => void;
}

/**
 * View displayed when chat is closed
 */
export const ChatClosedView: React.FC<ChatClosedViewProps> = ({ onReset }) => {
    return (
        <div className="flex flex-col items-center justify-center space-y-4 py-6">
            <p className="text-gray-600 text-center">The chat session has ended.</p>
            <button
                onClick={onReset}
                className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 flex items-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
                <RefreshCw className="w-5 h-5" />
                <span className="font-medium">Start New Session</span>
            </button>
        </div>
    );
};
