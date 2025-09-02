import "server-only";
import { cookies } from "next/headers";
import { getAdminAuth } from "../firebase/admin";
import { serverEnv } from "../config/env";

// Use any type to avoid static imports
type DecodedIdToken = any;

const SESSION_COOKIE_NAME = "__session";
const DEFAULT_SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 14; // 14 days

function getSessionCookieMaxAgeSeconds(): number {
    // Prefer validated server env; fallback to raw env; else default
    const fromServerEnv = serverEnv?.SESSION_COOKIE_MAX_AGE;
    const fromProcess = process.env.SESSION_COOKIE_MAX_AGE;

    const candidate =
        typeof fromServerEnv === "number"
            ? fromServerEnv
            : fromProcess !== undefined
                ? Number(fromProcess)
                : undefined;

    if (typeof candidate === "number" && Number.isFinite(candidate) && candidate > 0) {
        return Math.floor(candidate);
    }

    if (process.env.NODE_ENV !== "production" && (fromServerEnv !== undefined || fromProcess !== undefined)) {
        console.warn(
            "SESSION_COOKIE_MAX_AGE is set but invalid; falling back to default (14 days).",
        );
    }

    return DEFAULT_SESSION_COOKIE_MAX_AGE;
}

const SESSION_COOKIE_MAX_AGE = getSessionCookieMaxAgeSeconds();

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
		const isEmulator = !!(serverEnv?.FIREBASE_AUTH_EMULATOR_HOST || process.env.FIREBASE_AUTH_EMULATOR_HOST);

		// In emulator, fall back to using the ID token as the cookie value
		const cookieValue = isEmulator
			? idToken
			: await adminAuth.createSessionCookie(idToken, { expiresIn: SESSION_COOKIE_MAX_AGE * 1000 });

		const cookieStore = await cookies();

		// Set cookie with security options
		cookieStore.set(SESSION_COOKIE_NAME, cookieValue, {
			httpOnly: true,
			secure: process.env.APP_ENV === "production",
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
		const isEmulator = !!(serverEnv?.FIREBASE_AUTH_EMULATOR_HOST || process.env.FIREBASE_AUTH_EMULATOR_HOST);

		// In emulator, verify the ID token directly; otherwise verify the session cookie
		const decodedClaims = isEmulator
			? await adminAuth.verifyIdToken(sessionCookie.value, true)
			: await adminAuth.verifySessionCookie(sessionCookie.value, true);

        return decodedClaims;
    } catch (error) {
        // If verification fails (invalid/revoked/missing user), clear the cookie to avoid noisy loops
        try {
            const code = (error as any)?.errorInfo?.code || (error as any)?.code || "";
            const shouldClear =
                typeof code === "string" && (
                    code.includes("invalid-session-cookie") ||
                    code.includes("session-cookie-revoked") ||
                    code.includes("user-not-found")
                );
            if (shouldClear) {
                const cookieStore = await cookies();
                cookieStore.delete(SESSION_COOKIE_NAME);
            }
        } catch {}
        if (process.env.NODE_ENV !== "production") {
            console.warn("Error verifying session cookie (handled):", error);
        }
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
