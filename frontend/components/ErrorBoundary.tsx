'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showDetails?: boolean;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * ErrorBoundary - React Error Boundary Component
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI.
 *
 * Usage:
 * ```tsx
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 *
 * With custom fallback:
 * ```tsx
 * <ErrorBoundary fallback={<CustomErrorUI />}>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error);
      console.error('Error details:', errorInfo);
    }

    // Update state with error details
    this.setState({
      error,
      errorInfo
    });

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // In production, you might want to send error to logging service
    // Example: sendErrorToService(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // If custom fallback provided, use it
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-md w-full space-y-8">
            <div className="text-center">
              {/* Error Icon */}
              <div className="mx-auto h-24 w-24 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <ExclamationTriangleIcon className="h-16 w-16 text-red-600" />
              </div>

              {/* Error Title */}
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Oops! Something went wrong
              </h2>
              <p className="text-sm text-gray-600 mb-6">
                We're sorry for the inconvenience. An error occurred while rendering this page.
              </p>

              {/* Error Details (only in development or if showDetails=true) */}
              {(process.env.NODE_ENV === 'development' || this.props.showDetails) &&
                this.state.error && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-left">
                    <h3 className="text-sm font-semibold text-red-900 mb-2">
                      Error Details:
                    </h3>
                    <div className="text-xs text-red-800 font-mono overflow-auto max-h-48">
                      <p className="font-bold mb-2">{this.state.error.name}:</p>
                      <p className="mb-2">{this.state.error.message}</p>
                      {this.state.error.stack && (
                        <details className="mt-2">
                          <summary className="cursor-pointer font-semibold">
                            Stack Trace
                          </summary>
                          <pre className="mt-2 whitespace-pre-wrap break-words">
                            {this.state.error.stack}
                          </pre>
                        </details>
                      )}
                      {this.state.errorInfo && (
                        <details className="mt-2">
                          <summary className="cursor-pointer font-semibold">
                            Component Stack
                          </summary>
                          <pre className="mt-2 whitespace-pre-wrap break-words">
                            {this.state.errorInfo.componentStack}
                          </pre>
                        </details>
                      )}
                    </div>
                  </div>
                )}

              {/* Action Buttons */}
              <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={this.handleReset}
                  className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition"
                >
                  <ArrowPathIcon className="h-5 w-5 mr-2" />
                  Try Again
                </button>

                <button
                  onClick={() => (window.location.href = '/dashboard')}
                  className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition"
                >
                  Go to Dashboard
                </button>
              </div>

              {/* Help Text */}
              <p className="mt-6 text-xs text-gray-500">
                If this problem persists, please contact support.
              </p>
            </div>
          </div>
        </div>
      );
    }

    // No error, render children
    return this.props.children;
  }
}

/**
 * Functional wrapper for ErrorBoundary with custom error handler
 */
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  errorHandler?: (error: Error, errorInfo: ErrorInfo) => void
): React.FC<P> {
  return function WithErrorBoundary(props: P) {
    return (
      <ErrorBoundary onError={errorHandler}>
        <WrappedComponent {...props} />
      </ErrorBoundary>
    );
  };
}

export default ErrorBoundary;
