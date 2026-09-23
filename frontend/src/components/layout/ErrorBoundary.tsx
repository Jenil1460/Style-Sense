import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center p-4">
          <div className="max-w-xl w-full bg-red-900/10 border border-red-500/20 p-8 rounded-3xl backdrop-blur-md">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-500" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-red-400">Application Error</h1>
                <p className="text-white/50">Something went wrong while rendering this page.</p>
              </div>
            </div>
            
            <div className="bg-black/50 p-4 rounded-xl border border-white/5 mb-6 overflow-x-auto">
              <p className="text-red-300 font-mono text-sm mb-2 font-bold">{this.state.error?.toString()}</p>
              <pre className="text-white/40 font-mono text-xs whitespace-pre-wrap">
                {this.state.errorInfo?.componentStack}
              </pre>
            </div>
            
            <div className="flex justify-end">
              <button
                onClick={() => {
                  this.setState({ hasError: false, error: null, errorInfo: null });
                  window.location.href = '/dashboard';
                }}
                className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-6 py-2 rounded-full transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Return to Dashboard</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
