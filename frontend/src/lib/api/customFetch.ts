interface FetcherOptions extends RequestInit {
	baseURL?: string;
	timeout?: number;
	skipAuth?: boolean; // Skip auth token injection
	retries?: number;
	retryDelay?: number;
}

type ApiEnvelope<T = unknown> =
	| { status: "success"; data: T }
	| { status: "error"; error: { code: string; message: string } };

// Function to get auth header from client (Zustand)
const getClientAuthHeader = async (): Promise<string | null> => {
	if (typeof window === "undefined") return null;
	try {
		const { useAuthStore } = await import("@/stores/auth-store");
		const token = useAuthStore.getState().idToken;
		return token ? `Bearer ${token}` : null;
	} catch {
		return null;
	}
};

class FetchError extends Error {
	constructor(
		message: string,
		public status: number,
		public statusText: string,
		public response?: Response,
	) {
		super(message);
		this.name = "FetchError";
	}
}

// Simplified, best-practice customFetch: single options object, robust JSON handling, 204/null handling
// Also handles AbortSignal as second parameter (for orval compatibility)
export async function customFetch<T = unknown>(
    url: string, 
    optionsOrSignal: FetcherOptions | AbortSignal = {}
): Promise<T> {
	// Handle orval's signal parameter pattern
	const options: FetcherOptions = optionsOrSignal instanceof AbortSignal 
		? { signal: optionsOrSignal }
		: optionsOrSignal;
	const {
		baseURL,
		timeout = 10000,
		headers: userHeaders = {},
		signal: userSignal,
		body,
		skipAuth = false,
		retries = 0,
		retryDelay = 1000,
		...rest
	} = options;

	// Import getApiBaseUrl dynamically to avoid circular imports
	const apiBaseUrl = baseURL ?? (await import("../config/env").then((m) => m.getApiBaseUrl()));

	const fullURL = url.startsWith("http") ? url : `${apiBaseUrl}${url}`;

	// Headers: default Accept JSON; set Content-Type only if sending a body and not provided by user
	const headers: HeadersInit = {
		Accept: "application/json",
		...userHeaders,
	};

	// Inject Authorization header (client: Zustand token only)
	if (!skipAuth && typeof window !== "undefined") {
		try {
			const authHeader = await getClientAuthHeader();
			if (authHeader) {
				(headers as Record<string, string>)["Authorization"] = authHeader;
			}
		} catch {
			// proceed without auth
		}
	}
	const hasBody = body !== undefined && body !== null;
	if (hasBody) {
		const hasContentType = Object.keys(headers as Record<string, string>).some(
			(k) => k.toLowerCase() === "content-type",
		);
		if (!hasContentType) {
			(headers as Record<string, string>)["Content-Type"] = "application/json";
		}
	}

	// Merge timeout signal and user signal
	const controller = new AbortController();
	const onUserAbort = () => controller.abort(userSignal?.reason);
	if (userSignal) {
		if (userSignal.aborted) controller.abort(userSignal.reason);
		else userSignal.addEventListener("abort", onUserAbort);
	}
	const timeoutId = setTimeout(() => controller.abort("timeout"), timeout);

    // Helper: silent reissue via Firebase currentUser and POST /api/auth/login
    const trySilentReissue = async (): Promise<boolean> => {
        if (typeof window === "undefined") return false;
        try {
            const { auth } = await import("@/lib/firebase/client");
            const current = auth.currentUser;
            if (!current) {
                // No client user → auto-navigate to login modal per spec
                try { window.location.href = "/?auth=1"; } catch {}
                return false;
            }

            const idToken = await current.getIdToken(true);
            const res = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ idToken }),
                cache: "no-store",
            });
            if (!res.ok) return false;

            // Keep client Authorization in sync when present
            try {
                const { useAuthStore } = await import("@/stores/auth-store");
                useAuthStore.getState().setIdToken(idToken);
            } catch {}
            return true;
        } catch (e) {
            console.error("Silent reissue failed:", e);
            return false;
        }
    };

    let didRetry = false;

    try {
        let response = await fetch(fullURL, {
            ...rest,
            headers,
            body,
            signal: controller.signal,
        });

		clearTimeout(timeoutId);
		if (userSignal) userSignal.removeEventListener("abort", onUserAbort);

		// No Content
		if (response.status === 204 || response.status === 205) {
			return null as T;
		}

		// Determine content type
        let contentType = response.headers.get("content-type") || "";

		// Handle error responses first, regardless of content type
		if (!response.ok) {
			let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

			// Try to extract error message from response body
			try {
				if (contentType.includes("application/json")) {
					const json = await response.json();
					const maybeMsg = (json as any)?.error?.message || (json as any)?.message;
					if (maybeMsg) errorMessage = maybeMsg;
				} else if (contentType.includes("text/")) {
					// Handle plain text error messages
					const text = await response.text();
					if (text.trim()) errorMessage = text.trim();
				}
			} catch {
				// If we can't parse the error body, use the status text
			}

            // Handle auth errors: attempt silent reissue, then retry once
            if ((response.status === 401 || response.status === 403) && !didRetry) {
                const ok = await trySilentReissue();
                if (ok) {
                    didRetry = true;
                    response = await fetch(fullURL, {
                        ...rest,
                        headers,
                        body,
                        signal: controller.signal,
                    });
                    // Recompute meta for the retried response
                    if (response.status === 204 || response.status === 205) {
                        return null as T;
                    }
                    contentType = response.headers.get("content-type") || "";
                    if (response.ok && contentType.includes("application/json")) {
                        const json = await response.json().catch(() => null);
                        if (json === null) return null as T;
                        const maybeEnvelope = json as Partial<ApiEnvelope<T>>;
                        if (maybeEnvelope?.status === "error") {
                            const err = maybeEnvelope.error;
                            throw new FetchError(
                                err?.message || `HTTP ${response.status}: ${response.statusText}`,
                                response.status,
                                response.statusText,
                                response,
                            );
                        }
                        return json as T;
                    }
                    if (response.ok) {
                        const contentLength = response.headers.get("content-length");
                        if (!contentType && (!contentLength || contentLength === "0")) {
                            return null as T;
                        }
                    }
                    // If still not ok, fall through to error handling below
                    errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                }
            }

			throw new FetchError(errorMessage, response.status, response.statusText, response);
		}

		// Attempt to parse JSON when indicated for successful responses
		if (contentType.includes("application/json")) {
			let json: unknown;
			try {
				json = await response.json();
			} catch {
				// If server claimed JSON but body is empty
				return null as T;
			}

			// Envelope support
			const maybeEnvelope = json as Partial<ApiEnvelope<T>>;
			if (maybeEnvelope?.status === "error") {
				const err = maybeEnvelope.error;
				throw new FetchError(
					err?.message || "An unknown error occurred",
					response.status,
					response.statusText,
					response,
				);
			}
			// Do not unwrap envelope; return the full JSON to match generated types
			return json as T;
		}

		// Non-JSON success without content-type: treat empty as null, otherwise error
		if (response.ok) {
			const contentLength = response.headers.get("content-length");
			if (!contentType && (!contentLength || contentLength === "0")) {
				return null as T;
			}
		}

		// Unexpected non-JSON response for successful requests
		throw new FetchError(
			`Unexpected content-type: ${contentType || "none"}`,
			response.status,
			response.statusText,
			response,
		);
	} catch (error: any) {
		clearTimeout(timeoutId);
		if (userSignal) userSignal.removeEventListener("abort", onUserAbort);

		if (error instanceof FetchError) throw error;

		if (
			typeof DOMException !== "undefined" &&
			error instanceof DOMException &&
			error.name === "AbortError"
		) {
			const reason = (error as any)?.message || "Request aborted";
			throw new FetchError(reason, 499, "Client Closed Request");
		}

		if (error instanceof TypeError) {
			throw new FetchError("Network error", 0, "Network Error");
		}

		throw new FetchError(error?.message || "Unknown error", 0, "Unknown Error");
	}
}

// Convenience wrappers (keep signatures simple; signal provided via options)
export function get<T = any>(url: string, options?: FetcherOptions): Promise<T> {
	return customFetch<T>(url, { ...options, method: "GET" });
}

export function post<T = any>(url: string, data?: any, options?: FetcherOptions): Promise<T> {
	return customFetch<T>(url, {
		...options,
		method: "POST",
		body: data !== undefined ? JSON.stringify(data) : undefined,
	});
}

export function put<T = any>(url: string, data?: any, options?: FetcherOptions): Promise<T> {
	return customFetch<T>(url, {
		...options,
		method: "PUT",
		body: data !== undefined ? JSON.stringify(data) : undefined,
	});
}

export function patch<T = any>(url: string, data?: any, options?: FetcherOptions): Promise<T> {
	return customFetch<T>(url, {
		...options,
		method: "PATCH",
		body: data !== undefined ? JSON.stringify(data) : undefined,
	});
}

export function del<T = any>(url: string, options?: FetcherOptions): Promise<T> {
	return customFetch<T>(url, { ...options, method: "DELETE" });
}

export const api = {
	get,
	post,
	put,
	patch,
	delete: del,
	customFetch,
} as const;

export { FetchError };
export type ApiResponse<T = unknown> = ApiEnvelope<T>;
export type { FetcherOptions, ApiEnvelope };

// Provide default export for tooling compatibility (Orval mutator expects named, but default helps envs)
export default customFetch;
