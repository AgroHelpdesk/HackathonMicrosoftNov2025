import { AlertCircle, RefreshCw } from 'lucide-react';
import React from 'react';

interface ErrorDisplayProps {
    error: string;
    onRetry?: () => void;
}

/**
 * Error display component with retry option
 */
export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onRetry }) => {
    return (
        <div className="flex flex-col items-center justify-center h-96 space-y-4 p-8">
            <div className="p-4 bg-red-100 rounded-full">
                <AlertCircle className="w-12 h-12 text-red-500" />
            </div>
            <h3 className="text-xl font-semibold text-gray-800">Error connecting</h3>
            <p className="text-gray-600 text-center max-w-md">{error}</p>
            {onRetry && (
                <button
                    onClick={onRetry}
                    className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 flex items-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                    <RefreshCw className="w-5 h-5" />
                    <span className="font-medium">Try Again</span>
                </button>
            )}
        </div>
    );
};
