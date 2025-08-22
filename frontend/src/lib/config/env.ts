import { z } from "zod";

// Client-side environment schema
const clientEnvSchema = z.object({
	NEXT_PUBLIC_API_BASE_URL: z.string().url().optional(),
	NEXT_PUBLIC_FIREBASE_API_KEY: z.string().min(1).optional(),
	NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: z.string().min(1).optional(),
	NEXT_PUBLIC_FIREBASE_PROJECT_ID: z.string().min(1).optional(),
	NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: z.string().optional(),
	NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: z.string().optional(),
	NEXT_PUBLIC_FIREBASE_APP_ID: z.string().min(1).optional(),
	NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID: z.string().optional(),
});

// Server-side environment schema
const serverEnvSchema = z.object({
	NODE_ENV: z.enum(["development", "test", "staging", "production"]).default("development"),
	API_BASE_URL: z.string().url().optional(),
	FIREBASE_PROJECT_ID: z.string().min(1).optional(),
	FIREBASE_CLIENT_EMAIL: z.string().email().optional(),
	FIREBASE_PRIVATE_KEY: z.string().min(1).optional(),
	// Server-side Identity Toolkit API key (used for custom token exchange)
	FIREBASE_API_KEY: z.string().min(1).optional(),
	// Optional auth emulator host (e.g., 127.0.0.1:9099). Not used on Vercel.
	FIREBASE_AUTH_EMULATOR_HOST: z.string().optional(),
});

function getClientEnv() {
	const env = {
		NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
		NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
		NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
		NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
		NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
		NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
		NEXT_PUBLIC_FIREBASE_APP_ID: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
		NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
	};

	const result = clientEnvSchema.safeParse(env);

	if (!result.success) {
		console.warn("Invalid client environment variables:", result.error.flatten().fieldErrors);
	}

	return result.success ? result.data : env;
}

function getServerEnv() {
	if (typeof window !== "undefined") {
		throw new Error("Server environment variables should not be accessed on the client");
	}

	const env = {
		NODE_ENV: process.env.NODE_ENV,
		API_BASE_URL: process.env.API_BASE_URL,
		FIREBASE_PROJECT_ID: process.env.FIREBASE_PROJECT_ID,
		FIREBASE_CLIENT_EMAIL: process.env.FIREBASE_CLIENT_EMAIL,
		FIREBASE_PRIVATE_KEY: process.env.FIREBASE_PRIVATE_KEY,
		FIREBASE_API_KEY: process.env.FIREBASE_API_KEY,
		FIREBASE_AUTH_EMULATOR_HOST: process.env.FIREBASE_AUTH_EMULATOR_HOST,
	};

	const result = serverEnvSchema.safeParse(env);

	if (!result.success) {
		console.error("Invalid server environment variables:", result.error.flatten().fieldErrors);
		throw new Error("Invalid server environment configuration");
	}

	return result.data;
}

// Export environment configurations
export const clientEnv = getClientEnv();
export const serverEnv = typeof window === "undefined" ? getServerEnv() : null;

// Helper functions
export const isDevelopment = () => process.env.NODE_ENV === "development";
export const isProduction = () => process.env.NODE_ENV === "production";
export const isStaging = () => process.env.NODE_ENV === "staging";
export const isTest = () => process.env.NODE_ENV === "test";

// API base URL with fallbacks
export const getApiBaseUrl = () => {
	if (typeof window === "undefined") {
		// Server-side
		return serverEnv?.API_BASE_URL || "http://backend:8000";
	} else {
		// Client-side
		return clientEnv.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
	}
};
