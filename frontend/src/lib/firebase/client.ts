import { initializeApp } from "firebase/app";
import { connectAuthEmulator, getAuth } from "firebase/auth";

// Standard Firebase configuration (Auth-only required fields)
const firebaseConfig: Record<string, string> = {
	apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY!,
	authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN!,
	projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID!,
	appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID!,
};

// Optional config (only include if provided)
if (process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET) {
	firebaseConfig.storageBucket = process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET;
}
if (process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID) {
	firebaseConfig.messagingSenderId = process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID;
}

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
export const auth = getAuth(app);

// Connect to Firebase Auth emulator in development
if (process.env.NODE_ENV === "development" && typeof window !== "undefined") {
	const authEmulatorHost = process.env.NEXT_PUBLIC_FIREBASE_AUTH_EMULATOR_HOST;
	if (authEmulatorHost) {
		try {
			connectAuthEmulator(auth, `http://${authEmulatorHost}`);
			console.log("🔥 Connected to Firebase Auth emulator at", authEmulatorHost);
		} catch (error) {
			// Emulator may already be connected, ignore error
			console.log("Firebase Auth emulator already connected or connection failed:", error);
		}
	}
}

export { app };
