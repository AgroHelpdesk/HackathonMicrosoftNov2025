import { Tractor, Wheat } from 'lucide-react';
import React from 'react';

/**
 * Application header component
 */
export const Header: React.FC = () => {
    return (
        <header className="bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 shadow-lg">
            <div className="max-w-6xl mx-auto px-4 py-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                            <Tractor className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">AgroHelpDesk</h1>
                            <p className="text-green-100">Technical assistance for Agriculture</p>
                        </div>
                    </div>
                    <div className="flex items-center space-x-3 text-white/80">
                        <Wheat className="w-5 h-5" />
                        <span className="text-sm font-medium">Assistant Active</span>
                    </div>
                </div>
            </div>
        </header>
    );
};
