import { toast } from "sonner";

export class AppError extends Error {
	public code: string;
	public statusCode: number;
	public cause?: Error;

	constructor(
		message: string,
		code: string = "UNKNOWN_ERROR",
		statusCode: number = 500,
		cause?: Error,
	) {
		super(message);
		this.name = "AppError";
		this.code = code;
		this.statusCode = statusCode;
		this.cause = cause;
	}
}

export class ValidationError extends AppError {
	constructor(
		message: string,
		public field?: string,
	) {
		super(message, "VALIDATION_ERROR", 400);
		this.name = "ValidationError";
	}
}

export class AuthError extends AppError {
	constructor(message: string, code: string = "AUTH_ERROR") {
		super(message, code, 401);
		this.name = "AuthError";
	}
}

export class NetworkError extends AppError {
	constructor(message: string = "Network request failed") {
		super(message, "NETWORK_ERROR", 0);
		this.name = "NetworkError";
	}
}

// Error handling utilities
export function handleError(error: unknown, context?: string): AppError {
	console.error(`Error${context ? ` in ${context}` : ""}:`, error);

	if (error instanceof AppError) {
		return error;
	}

	if (error instanceof Error) {
		// Handle specific error types
		if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
			return new NetworkError();
		}

		if (error.message.includes("auth") || error.message.includes("unauthorized")) {
			return new AuthError(error.message);
		}

		return new AppError(error.message, "UNKNOWN_ERROR", 500, error);
	}

	return new AppError("An unexpected error occurred", "UNKNOWN_ERROR", 500);
}

export function showErrorToast(error: unknown, defaultMessage?: string): void {
	const appError = handleError(error);
	const message = defaultMessage || appError.message || "An unexpected error occurred";

	toast.error(message, {
		description: appError.code !== "UNKNOWN_ERROR" ? `Error: ${appError.code}` : undefined,
	});
}

// Hook for error handling in components
export function useErrorHandler() {
	return {
		handleError: (error: unknown, context?: string) => handleError(error, context),
		showError: (error: unknown, defaultMessage?: string) => showErrorToast(error, defaultMessage),
	};
}
