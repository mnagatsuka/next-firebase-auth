"use client";

import { QueryErrorResetBoundary } from "@tanstack/react-query";
import { AlertCircle, RefreshCcw, Wifi, WifiOff } from "lucide-react";
import type React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorBoundary } from "./ErrorBoundary";

interface QueryErrorBoundaryProps {
	children: React.ReactNode;
	onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export function QueryErrorBoundary({ children, onError }: QueryErrorBoundaryProps) {
	return (
		<QueryErrorResetBoundary>
			{({ reset }) => (
				<ErrorBoundary
					onError={onError}
					fallback={(errorState) => <QueryErrorFallback error={errorState.error} onReset={reset} />}
				>
					{children}
				</ErrorBoundary>
			)}
		</QueryErrorResetBoundary>
	);
}

interface QueryErrorFallbackProps {
	error?: Error;
	onReset: () => void;
}

function QueryErrorFallback({ error, onReset }: QueryErrorFallbackProps) {
	const isNetworkError = error?.message.includes("fetch") || error?.message.includes("network");
	const isTimeoutError = error?.message.includes("timeout");

	const getErrorIcon = () => {
		if (isNetworkError) return <WifiOff className="h-12 w-12 text-destructive" />;
		if (isTimeoutError) return <Wifi className="h-12 w-12 text-warning" />;
		return <AlertCircle className="h-12 w-12 text-destructive" />;
	};

	const getErrorTitle = () => {
		if (isNetworkError) return "Connection Error";
		if (isTimeoutError) return "Request Timeout";
		return "Something went wrong";
	};

	const getErrorMessage = () => {
		if (isNetworkError)
			return "Unable to connect to the server. Please check your internet connection and try again.";
		if (isTimeoutError) return "The request took too long to complete. Please try again.";
		return "We encountered an unexpected error while loading data. Please try again.";
	};

	return (
		<Card className="w-full max-w-lg mx-auto mt-8">
			<CardHeader className="text-center">
				<div className="flex justify-center mb-4">{getErrorIcon()}</div>
				<CardTitle className="text-destructive">{getErrorTitle()}</CardTitle>
			</CardHeader>
			<CardContent className="space-y-4">
				<p className="text-sm text-muted-foreground text-center">{getErrorMessage()}</p>

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
						Retry
					</Button>
				</div>
			</CardContent>
		</Card>
	);
}
