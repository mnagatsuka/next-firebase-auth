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
			// Production (Vercel): prefer a single JSON secret for credentials
			console.log("🔥 Initializing Firebase Admin SDK for production (JSON secret)");
			const jsonStr = serverEnv?.FIREBASE_SERVICE_ACCOUNT_JSON || process.env.FIREBASE_SERVICE_ACCOUNT_JSON;

			try {
				if (jsonStr) {
					const data = JSON.parse(jsonStr);
					const projectId = data.project_id || serverEnv?.FIREBASE_PROJECT_ID || process.env.FIREBASE_PROJECT_ID;
					const clientEmail = data.client_email || serverEnv?.FIREBASE_CLIENT_EMAIL || process.env.FIREBASE_CLIENT_EMAIL;
					let privateKey: string = data.private_key || serverEnv?.FIREBASE_PRIVATE_KEY || process.env.FIREBASE_PRIVATE_KEY || "";
					if (privateKey.startsWith('"') && privateKey.endsWith('"')) privateKey = privateKey.slice(1, -1);
					if (privateKey.includes("\\n")) privateKey = privateKey.replace(/\\n/g, "\n");
					privateKey = privateKey.replace(/\r\n/g, "\n").trim();
					if (projectId && clientEmail && privateKey) {
						initializeApp({ credential: cert({ projectId, clientEmail, privateKey }) });
					} else {
						// Fallback to ADC if somehow missing
						initializeApp({ credential: applicationDefault(), projectId });
					}
				} else {
					// Fallback to individual envs or ADC
					const projectId = serverEnv?.FIREBASE_PROJECT_ID || process.env.FIREBASE_PROJECT_ID;
					const clientEmail = serverEnv?.FIREBASE_CLIENT_EMAIL || process.env.FIREBASE_CLIENT_EMAIL;
					let privateKey = serverEnv?.FIREBASE_PRIVATE_KEY || process.env.FIREBASE_PRIVATE_KEY;
					if (projectId && clientEmail && privateKey) {
						if (privateKey.startsWith('"') && privateKey.endsWith('"')) privateKey = privateKey.slice(1, -1);
						if (privateKey.includes("\\n")) privateKey = privateKey.replace(/\\n/g, "\n");
						privateKey = privateKey.replace(/\r\n/g, "\n").trim();
						initializeApp({ credential: cert({ projectId, clientEmail, privateKey }) });
					} else {
						initializeApp({ credential: applicationDefault(), projectId });
					}
				}
			} catch (e) {
				console.error("[firebase-admin] Failed to initialize from JSON/env; falling back to ADC", e);
				const projectId = serverEnv?.FIREBASE_PROJECT_ID || process.env.FIREBASE_PROJECT_ID;
				initializeApp({ credential: applicationDefault(), projectId });
			}
		}
	}

	_auth = getAuth();
	return _auth;
}
