import { AlertCircle, RefreshCw } from 'lucide-react';
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

/**
 * Error Boundary component to catch and display errors
 */
export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null });
        window.location.reload();
    };

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full">
                        <div className="flex flex-col items-center space-y-4">
                            <div className="p-4 bg-red-100 rounded-full">
                                <AlertCircle className="w-12 h-12 text-red-500" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-800">Algo deu errado</h2>
                            <p className="text-gray-600 text-center">
                                Desculpe, ocorreu um erro inesperado. Por favor, tente recarregar a página.
                            </p>
                            {process.env.NODE_ENV === 'development' && this.state.error && (
                                <div className="w-full p-4 bg-gray-100 rounded-lg">
                                    <p className="text-xs font-mono text-red-600 break-all">
                                        {this.state.error.toString()}
                                    </p>
                                </div>
                            )}
                            <button
                                onClick={this.handleReset}
                                className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 flex items-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl"
                            >
                                <RefreshCw className="w-5 h-5" />
                                <span className="font-medium">Recarregar Página</span>
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
