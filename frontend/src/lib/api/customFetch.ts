interface FetcherOptions extends RequestInit {
  baseURL?: string;
  timeout?: number;
}

interface ApiResponse<T = any> {
  status: "success" | "error";
  data: T;
  error?: {
    code: string;
    message: string;
  };
}

class FetchError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string,
    public response?: Response
  ) {
    super(message);
    this.name = "FetchError";
  }
}

/**
 * Universal customFetch that works for client components, server components, and API routes
 * Handles JSON responses with consistent error handling and type safety
 */
export async function customFetch<T = any>(
  url: string,
  options: FetcherOptions = {}
): Promise<T> {
  const {
    baseURL = typeof window === 'undefined' 
      ? process.env.API_BASE_URL || "http://backend:8000"  // Server-side: use Docker network
      : process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",  // Client-side: use localhost
    timeout = 10000,
    headers = {},
    ...fetchOptions
  } = options;

  // Build a valid URL for the current runtime
  // - On the server, always use an absolute URL (Node fetch requires absolute URLs)
  // - On the client, allow relative paths so the browser resolves against the current origin
  const isServerSide = typeof window === 'undefined'
  const fullURL = url.startsWith('http')
    ? url
    : isServerSide
    ? `${baseURL}${url}`
    : url

  // Default headers
  const defaultHeaders: HeadersInit = {
    "Content-Type": "application/json",
    ...headers,
  };

  // Create AbortController for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(fullURL, {
      ...fetchOptions,
      headers: defaultHeaders,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Handle non-JSON responses
    const contentType = response.headers.get("content-type");
    if (!contentType?.includes("application/json")) {
      if (!response.ok) {
        throw new FetchError(
          `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          response.statusText,
          response
        );
      }
      return response as T;
    }

    // Parse JSON response
    const data: ApiResponse<T> = await response.json();

    // Handle API error responses
    if (data.status === "error") {
      throw new FetchError(
        data.error?.message || "An unknown error occurred",
        response.status,
        response.statusText,
        response
      );
    }

    // Handle HTTP errors
    if (!response.ok) {
      throw new FetchError(
        data.error?.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        response.statusText,
        response
      );
    }

    return data.data;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof FetchError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === "AbortError") {
      throw new FetchError("Request timeout", 408, "Request Timeout");
    }

    if (error instanceof TypeError) {
      throw new FetchError("Network error", 0, "Network Error");
    }

    throw new FetchError(
      error instanceof Error ? error.message : "Unknown error",
      0,
      "Unknown Error"
    );
  }
}

/**
 * GET request wrapper
 */
export function get<T = any>(url: string, options?: FetcherOptions): Promise<T> {
  return customFetch<T>(url, { ...options, method: "GET" });
}

/**
 * POST request wrapper
 */
export function post<T = any>(
  url: string,
  data?: any,
  options?: FetcherOptions
): Promise<T> {
  return customFetch<T>(url, {
    ...options,
    method: "POST",
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * PUT request wrapper
 */
export function put<T = any>(
  url: string,
  data?: any,
  options?: FetcherOptions
): Promise<T> {
  return customFetch<T>(url, {
    ...options,
    method: "PUT",
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * PATCH request wrapper
 */
export function patch<T = any>(
  url: string,
  data?: any,
  options?: FetcherOptions
): Promise<T> {
  return customFetch<T>(url, {
    ...options,
    method: "PATCH",
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * DELETE request wrapper
 */
export function del<T = any>(
  url: string,
  options?: FetcherOptions
): Promise<T> {
  return customFetch<T>(url, { ...options, method: "DELETE" });
}

/**
 * Type-safe customFetch with automatic type inference for API responses
 */
export const api = {
  get,
  post,
  put,
  patch,
  delete: del,
  customFetch,
} as const;

export { FetchError };
export type { FetcherOptions, ApiResponse };
