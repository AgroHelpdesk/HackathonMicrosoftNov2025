import { Loader2 } from 'lucide-react';
import React from 'react';

interface LoadingStateProps {
    message?: string;
}

/**
 * Loading state component with spinner
 */
export const LoadingState: React.FC<LoadingStateProps> = ({ message = 'Carregando...' }) => {
    return (
        <div className="flex flex-col items-center justify-center h-96 space-y-4">
            <Loader2 className="w-12 h-12 text-green-600 animate-spin" />
            <p className="text-gray-600">{message}</p>
        </div>
    );
};
