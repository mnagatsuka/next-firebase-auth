/**
 * Error handling utilities with proper TypeScript support
 */

// Base error types
export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

export interface AppError {
  type: 'api' | 'auth' | 'validation' | 'network' | 'unknown';
  message: string;
  originalError?: unknown;
  code?: string;
}

/**
 * Type guard to check if an error is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'code' in error &&
    'message' in error &&
    typeof (error as ApiError).code === 'string' &&
    typeof (error as ApiError).message === 'string'
  );
}

/**
 * Type guard to check if an error is a FetchError from our customFetch
 */
export function isFetchError(error: unknown): error is Error & { status: number; statusText: string } {
  return (
    error instanceof Error &&
    'status' in error &&
    'statusText' in error &&
    typeof (error as any).status === 'number'
  );
}

/**
 * Normalize any error into a consistent AppError format
 */
export function normalizeError(error: unknown, fallbackMessage = 'An unexpected error occurred'): AppError {
  // Handle our custom FetchError
  if (isFetchError(error)) {
    return {
      type: error.status >= 400 && error.status < 500 ? 'api' : 'network',
      message: error.message,
      originalError: error,
      code: error.status.toString(),
    };
  }

  // Handle ApiError format
  if (isApiError(error)) {
    return {
      type: 'api',
      message: error.message,
      code: error.code,
      originalError: error,
    };
  }

  // Handle standard Error objects
  if (error instanceof Error) {
    return {
      type: 'unknown',
      message: error.message,
      originalError: error,
    };
  }

  // Handle string errors
  if (typeof error === 'string') {
    return {
      type: 'unknown',
      message: error,
      originalError: error,
    };
  }

  // Fallback for unknown error types
  return {
    type: 'unknown',
    message: fallbackMessage,
    originalError: error,
  };
}

/**
 * Create user-friendly error messages
 */
export function getErrorMessage(error: unknown): string {
  const normalized = normalizeError(error);
  
  switch (normalized.type) {
    case 'auth':
      return normalized.message || 'Authentication failed. Please try again.';
    case 'api':
      return normalized.message || 'Server error. Please try again later.';
    case 'network':
      return 'Network error. Please check your connection.';
    case 'validation':
      return normalized.message || 'Please check your input and try again.';
    default:
      return normalized.message || 'An unexpected error occurred. Please try again.';
  }
}

/**
 * Determine if an error should be reported to error tracking
 */
export function shouldReportError(error: AppError): boolean {
  // Don't report validation errors or auth errors
  if (error.type === 'validation' || error.type === 'auth') {
    return false;
  }
  
  // Don't report 4xx errors except 500
  if (error.code && error.code.startsWith('4') && error.code !== '500') {
    return false;
  }
  
  return true;
}