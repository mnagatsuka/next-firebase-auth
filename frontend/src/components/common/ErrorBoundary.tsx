"use client";

import { AlertCircle, RefreshCcw } from "lucide-react";
import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ErrorBoundaryState {
	hasError: boolean;
	error?: Error;
	errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
	children: React.ReactNode;
	fallback?: React.ComponentType<ErrorBoundaryState>;
	onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
	constructor(props: ErrorBoundaryProps) {
		super(props);
		this.state = { hasError: false };
	}

	static getDerivedStateFromError(error: Error): ErrorBoundaryState {
		return {
			hasError: true,
			error,
		};
	}

	componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
		this.setState({
			error,
			errorInfo,
		});

		// Call optional error handler
		this.props.onError?.(error, errorInfo);

		// Log error in development
		if (process.env.NODE_ENV === "development") {
			console.error("ErrorBoundary caught an error:", error, errorInfo);
		}
	}

	handleReset = () => {
		this.setState({ hasError: false });
	};

	render() {
		if (this.state.hasError) {
			const { fallback: Fallback } = this.props;

			if (Fallback) {
				return <Fallback {...this.state} />;
			}

			return <DefaultErrorFallback onReset={this.handleReset} error={this.state.error} />;
		}

		return this.props.children;
	}
}

interface DefaultErrorFallbackProps {
	error: Error | undefined;
	onReset: () => void;
}

function DefaultErrorFallback({ error, onReset }: DefaultErrorFallbackProps) {
	return (
		<Card className="w-full max-w-lg mx-auto mt-8">
			<CardHeader className="text-center">
				<div className="flex justify-center mb-4">
					<AlertCircle className="h-12 w-12 text-destructive" />
				</div>
				<CardTitle className="text-destructive">Something went wrong</CardTitle>
			</CardHeader>
			<CardContent className="space-y-4">
				<p className="text-sm text-muted-foreground text-center">
					We encountered an unexpected error. Please try refreshing the page or contact support if
					the problem persists.
				</p>

				{process.env.NODE_ENV === "development" && error && (
					<details className="bg-muted p-4 rounded text-xs overflow-auto">
						<summary className="cursor-pointer font-medium mb-2">
							Error Details (Development)
						</summary>
						<pre className="whitespace-pre-wrap">{error.message}</pre>
						{error.stack && (
							<pre className="mt-2 whitespace-pre-wrap text-xs opacity-70">{error.stack}</pre>
						)}
					</details>
				)}

				<div className="flex justify-center">
					<Button onClick={onReset} variant="outline" className="flex items-center gap-2">
						<RefreshCcw className="h-4 w-4" />
						Try Again
					</Button>
				</div>
			</CardContent>
		</Card>
	);
}

// Hook for easy usage in functional components
export function useErrorBoundary() {
	const [error, setError] = React.useState<Error | null>(null);

	const resetError = React.useCallback(() => {
		setError(null);
	}, []);

	const captureError = React.useCallback((error: Error) => {
		setError(error);
	}, []);

	React.useEffect(() => {
		if (error) {
			throw error;
		}
	}, [error]);

	return { captureError, resetError };
}
