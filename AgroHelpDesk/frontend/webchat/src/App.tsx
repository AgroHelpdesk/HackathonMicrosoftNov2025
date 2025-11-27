import React, { Suspense, lazy } from 'react';
import { ErrorBoundary, LoadingState } from './components/common';
import { Footer, Header } from './components/layout';

// Lazy load the ChatInterface for better performance
const ChatInterface = lazy(() =>
    import('./components/chat').then((module) => ({ default: module.ChatInterface }))
);

/**
 * Main App component
 * Refactored to use modular components with ErrorBoundary and lazy loading
 */
const App: React.FC = () => {
    return (
        <ErrorBoundary>
            <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
                <Header />

                <main className="max-w-6xl mx-auto px-4 py-8">
                    <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-green-100">
                        <Suspense fallback={<LoadingState message="Loading chat..." />}>
                            <ChatInterface />
                        </Suspense>
                    </div>
                </main>

                <Footer />
            </div>
        </ErrorBoundary>
    );
};

export default App;
