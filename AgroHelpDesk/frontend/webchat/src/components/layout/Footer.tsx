import { Sprout } from 'lucide-react';
import React from 'react';

/**
 * Application footer component
 */
export const Footer: React.FC = () => {
    return (
        <footer className="bg-gradient-to-r from-green-800 to-emerald-800 mt-12">
            <div className="max-w-6xl mx-auto px-4 py-6">
                <div className="flex items-center justify-center space-x-6 text-green-100">
                    <div className="flex items-center space-x-2">
                        <Sprout className="w-5 h-5" />
                        <span className="font-medium">AgroHelpDesk © 2025</span>
                    </div>
                    <span className="text-green-300">•</span>
                    <span className="text-sm">Technical assistance for Agriculture</span>
                </div>
            </div>
        </footer>
    );
};
