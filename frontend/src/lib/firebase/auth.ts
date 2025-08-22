import {
	createUserWithEmailAndPassword,
	EmailAuthProvider,
	linkWithCredential,
	onAuthStateChanged,
	signInAnonymously,
	signInWithEmailAndPassword,
	signOut,
	type User,
	type UserCredential,
} from "firebase/auth";
import { auth } from "./client";

// Auth utility functions
export const firebaseAuth = {
	// Email/password authentication
	async signInWithEmail(email: string, password: string): Promise<UserCredential> {
		return await signInWithEmailAndPassword(auth, email, password);
	},

	async signUpWithEmail(email: string, password: string): Promise<UserCredential> {
		return await createUserWithEmailAndPassword(auth, email, password);
	},

	// Anonymous authentication
	async signInAnonymously(): Promise<UserCredential> {
		return await signInAnonymously(auth);
	},

	// Link anonymous user with email/password
	async linkAnonymousWithEmail(email: string, password: string): Promise<UserCredential> {
		const user = auth.currentUser;
		if (!user || !user.isAnonymous) {
			throw new Error("No anonymous user to link");
		}

		const credential = EmailAuthProvider.credential(email, password);
		return await linkWithCredential(user, credential);
	},

	// Sign out
	async signOut(): Promise<void> {
		return await signOut(auth);
	},

	// Get current user
	getCurrentUser(): User | null {
		return auth.currentUser;
	},

	// Get ID token
	async getIdToken(forceRefresh = false): Promise<string | null> {
		const user = auth.currentUser;
		if (!user) return null;
		return await user.getIdToken(forceRefresh);
	},

	// Auth state observer
	onAuthStateChanged: (callback: (user: User | null) => void) => {
		return onAuthStateChanged(auth, callback);
	},
};

// Type definitions
export type { User, UserCredential };
export { auth };
