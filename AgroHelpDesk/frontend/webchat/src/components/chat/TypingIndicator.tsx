import { Sprout } from 'lucide-react';
import React from 'react';

interface TypingIndicatorProps {
    message?: string;
}

/**
 * Typing indicator component
 */
export const TypingIndicator: React.FC<TypingIndicatorProps> = ({
    message = 'Assistant is analyzing your request...',
}) => {
    return (
        <div className="flex justify-start">
            <div className="flex items-start space-x-3 max-w-2xl">
                <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
                    <Sprout className="w-5 h-5 text-white" />
                </div>
                <div className="bg-white text-gray-800 px-5 py-3 rounded-2xl border border-green-100 shadow-md">
                    <div className="flex items-center space-x-3">
                        <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" />
                            <div
                                className="w-2 h-2 bg-green-500 rounded-full animate-bounce"
                                style={{ animationDelay: '0.1s' }}
                            />
                            <div
                                className="w-2 h-2 bg-green-500 rounded-full animate-bounce"
                                style={{ animationDelay: '0.2s' }}
                            />
                        </div>
                        <span className="text-sm text-green-700 font-medium">{message}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
