import "server-only";
import { cookies } from "next/headers";
import { getAdminAuth } from "../firebase/admin";
import { serverEnv } from "../config/env";

// Use any type to avoid static imports
type DecodedIdToken = any;

const SESSION_COOKIE_NAME = "session";
const SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 14; // 14 days

export interface SessionCookieOptions {
	httpOnly?: boolean;
	secure?: boolean;
	sameSite?: "strict" | "lax" | "none";
	maxAge?: number;
	path?: string;
}

// Set session cookie
export async function setSessionCookie(idToken: string): Promise<void> {
	try {
		const adminAuth = await getAdminAuth();

		// Create session cookie
		const sessionCookie = await adminAuth.createSessionCookie(idToken, {
			expiresIn: SESSION_COOKIE_MAX_AGE * 1000, // Convert to milliseconds
		});

		const cookieStore = await cookies();

		// Set cookie with security options
		cookieStore.set(SESSION_COOKIE_NAME, sessionCookie, {
			httpOnly: true,
			secure: process.env.NODE_ENV === "production",
			sameSite: "lax",
			maxAge: SESSION_COOKIE_MAX_AGE,
			path: "/",
		});
	} catch (error) {
		console.error("Error setting session cookie:", error);
		throw error;
	}
}

// Verify session cookie and return user
export async function verifySessionCookie(): Promise<DecodedIdToken | null> {
	try {
		const cookieStore = await cookies();
		const sessionCookie = cookieStore.get(SESSION_COOKIE_NAME);

		if (!sessionCookie?.value) {
			return null;
		}

		const adminAuth = await getAdminAuth();

		// Verify session cookie
		const decodedClaims = await adminAuth.verifySessionCookie(
			sessionCookie.value,
			true, // Check if cookie is revoked
		);

		return decodedClaims;
	} catch (error) {
		console.error("Error verifying session cookie:", error);
		return null;
	}
}

// Clear session cookie
export async function clearSessionCookie(): Promise<void> {
	const cookieStore = await cookies();
	cookieStore.delete(SESSION_COOKIE_NAME);
}

// Get session cookie value (for client-side checks)
export async function getSessionCookie(): Promise<string | null> {
	const cookieStore = await cookies();
	const sessionCookie = cookieStore.get(SESSION_COOKIE_NAME);
	return sessionCookie?.value || null;
}

// Check if user is authenticated (server-side)
export async function isAuthenticated(): Promise<boolean> {
	const user = await verifySessionCookie();
	return user !== null;
}

// Get user from session (server-side)
export async function getServerUser(): Promise<DecodedIdToken | null> {
	return await verifySessionCookie();
}

// Get Authorization header value for server-side API calls
// Flow (Option B): verify session cookie -> mint custom token -> exchange for ID token -> return `Bearer <idToken>`
export async function getServerAuthorizationHeader(): Promise<string | null> {
	try {
		const decoded = await verifySessionCookie();
		if (!decoded) return null;

		const adminAuth = await getAdminAuth();

		// Prefer uid if present; fallback to user_id
		const uid: string | undefined = decoded.uid || decoded.user_id;
		if (!uid) return null;

		// Mint a custom token for this uid
		const customToken = await adminAuth.createCustomToken(uid);

        // Use a server-side API key for Identity Toolkit
        const apiKey = serverEnv?.FIREBASE_API_KEY || process.env.FIREBASE_API_KEY || process.env.NEXT_PUBLIC_FIREBASE_API_KEY;
        if (!apiKey) {
            const msg = "getServerAuthorizationHeader: Missing FIREBASE_API_KEY (server)";
            if (process.env.NODE_ENV === "production") {
                throw new Error(msg);
            } else {
                console.warn(msg);
                return null;
            }
        }

        // Determine Identity Toolkit base URL (use emulator when configured)
        const emulatorHost = serverEnv?.FIREBASE_AUTH_EMULATOR_HOST || process.env.FIREBASE_AUTH_EMULATOR_HOST;
        const idToolkitBase = emulatorHost
            ? `http://${emulatorHost}/identitytoolkit.googleapis.com/v1`
            : `https://identitytoolkit.googleapis.com/v1`;
        if (process.env.NODE_ENV !== "production") {
            // Debug log to verify SSR uses the expected Identity Toolkit endpoint
            console.info(`[auth] Using Identity Toolkit base: ${idToolkitBase}`);
        }

        // Exchange custom token -> ID token
        const res = await fetch(
            `${idToolkitBase}/accounts:signInWithCustomToken?key=${apiKey}`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token: customToken, returnSecureToken: true }),
                cache: "no-store",
            },
        );

		if (!res.ok) {
			const text = await res.text().catch(() => "");
			console.error("Custom token exchange failed:", res.status, text);
			return null;
		}

		const json: any = await res.json().catch(() => null);
		const idToken = json?.idToken as string | undefined;
		if (!idToken) return null;

		return `Bearer ${idToken}`;
	} catch (error) {
		console.error("getServerAuthorizationHeader error:", error);
		return null;
	}
}
