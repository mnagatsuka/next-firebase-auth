// Firebase Admin SDK - Server-side only
// This file should only be imported in API routes or server-side code
import "server-only";
import { serverEnv } from "../config/env";
import type { AppOptions } from "firebase-admin/app";

let _auth: import("firebase-admin/auth").Auth | null = null;

export async function getAdminAuth() {
	if (_auth) return _auth;

	const { getApps, initializeApp, applicationDefault, cert } = await import("firebase-admin/app");
	const { getAuth } = await import("firebase-admin/auth");

	if (!getApps().length) {
		const isEmulator = !!(serverEnv?.FIREBASE_AUTH_EMULATOR_HOST || process.env.FIREBASE_AUTH_EMULATOR_HOST);

		if (isEmulator) {
			// Local (Auth Emulator): no private key; projectId only
			console.log("🔥 Initializing Firebase Admin SDK for emulator");
			const opts: AppOptions = { projectId: serverEnv?.FIREBASE_PROJECT_ID || process.env.FIREBASE_PROJECT_ID };
			initializeApp(opts);
		} else {
			// Production (Vercel env → cert)
			console.log("🔥 Initializing Firebase Admin SDK for production");
			const projectId = serverEnv?.FIREBASE_PROJECT_ID || process.env.FIREBASE_PROJECT_ID;
			const clientEmail = serverEnv?.FIREBASE_CLIENT_EMAIL || process.env.FIREBASE_CLIENT_EMAIL;
			let privateKey = serverEnv?.FIREBASE_PRIVATE_KEY || process.env.FIREBASE_PRIVATE_KEY;

			if (!projectId || !clientEmail || !privateKey) {
				// Fallback (ADC)
				initializeApp({ credential: applicationDefault(), projectId });
			} else {
				// Safety: strip accidental surrounding quotes
				if (privateKey.startsWith('"') && privateKey.endsWith('"')) {
					privateKey = privateKey.slice(1, -1);
				}
				// Convert \\n to real newlines if needed
				if (privateKey.includes("\\\\n")) {
					privateKey = privateKey.replace(/\\\\n/g, "\n");
				}
				initializeApp({ credential: cert({ projectId, clientEmail, privateKey }) });
			}
		}
	}

	_auth = getAuth();
	return _auth;
}
