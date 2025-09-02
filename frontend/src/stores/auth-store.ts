import { create } from "zustand";
import { devtools } from "zustand/middleware";
import { type AppError } from "@/lib/utils/error";
import { type User as FirebaseUser } from "firebase/auth";
import { auth } from "@/lib/firebase/client";

export interface User {
	uid: string;
	email: string | null;
	displayName: string | null;
	isAnonymous: boolean;
	emailVerified: boolean;
}

interface AuthState {
	// Authentication state
	user: User | null;
	isAuthenticated: boolean;
	isLoading: boolean; // auth action or initialization state
	authInitialized: boolean; // first onAuthStateChanged fired
	idToken: string | null;
	error: AppError | null;

	// Actions
	setUser: (user: User | null) => void;
	setIdToken: (token: string | null) => void;
	setLoading: (loading: boolean) => void;
	setError: (error: AppError | null) => void;
	initializeAuth: () => void;

	// Firebase Auth actions
	signInWithEmail: (email: string, password: string) => Promise<void>;
	signUpWithEmail: (email: string, password: string) => Promise<void>;
	signInAnonymously: () => Promise<void>;
	linkAnonymousWithEmail: (email: string, password: string) => Promise<void>;
	logout: () => Promise<void>;
	refreshToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
	devtools(
		(set, get) => ({
			// Initial state
			user: null,
			isAuthenticated: false,
			isLoading: false,
			authInitialized: false,
			idToken: null,
			error: null,

			// Actions
			setUser: (user) => set({ 
				user, 
				isAuthenticated: !!user 
			}),

			setIdToken: (token) => set({ idToken: token }),

			setLoading: (loading) => set({ isLoading: loading }),

			setError: (error) => set({ error }),

			initializeAuth: () => {
				const { onAuthStateChanged } = require("firebase/auth");
				const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
					set({ isLoading: true });

					if (firebaseUser) {
						try {
							const idToken = await firebaseUser.getIdToken();
							const user: User = {
								uid: firebaseUser.uid,
								email: firebaseUser.email,
								displayName: firebaseUser.displayName,
								isAnonymous: firebaseUser.isAnonymous,
								emailVerified: firebaseUser.emailVerified,
							};

							set({
								user,
								isAuthenticated: true,
								idToken,
								authInitialized: true,
								isLoading: false,
								error: null,
							});
						} catch (error) {
							console.error("Failed to get ID token:", error);
							set({
								user: null,
								isAuthenticated: false,
								idToken: null,
								authInitialized: true,
								isLoading: false,
								error: { type: 'auth', message: 'Failed to get authentication token' } as AppError,
							});
						}
					} else {
						set({
							user: null,
							isAuthenticated: false,
							idToken: null,
							authInitialized: true,
							isLoading: false,
							error: null,
						});
					}
				});

				// Return unsubscribe for cleanup (though not used in current implementation)
				return unsubscribe;
			},

			signInWithEmail: async (email, password) => {
				const { signInWithEmailAndPassword } = await import("firebase/auth");
				set({ isLoading: true, error: null });
				
				try {
					await signInWithEmailAndPassword(auth, email, password);
					// User state will be updated via onAuthStateChanged
				} catch (error) {
					set({ 
						isLoading: false, 
						error: { type: 'auth', message: 'Sign in failed' } as AppError 
					});
					throw error;
				}
			},

			signUpWithEmail: async (email, password) => {
				const { createUserWithEmailAndPassword } = await import("firebase/auth");
				set({ isLoading: true, error: null });

				try {
					await createUserWithEmailAndPassword(auth, email, password);
					// User state will be updated via onAuthStateChanged
				} catch (error) {
					set({ 
						isLoading: false, 
						error: { type: 'auth', message: 'Sign up failed' } as AppError 
					});
					throw error;
				}
			},

			signInAnonymously: async () => {
				const { signInAnonymously } = await import("firebase/auth");
				set({ isLoading: true, error: null });

				try {
					await signInAnonymously(auth);
					// User state will be updated via onAuthStateChanged
				} catch (error) {
					set({ 
						isLoading: false, 
						error: { type: 'auth', message: 'Anonymous sign in failed' } as AppError 
					});
					throw error;
				}
			},

			linkAnonymousWithEmail: async (email, password) => {
				const { EmailAuthProvider, linkWithCredential } = await import("firebase/auth");
				const { user: currentUser } = get();
				
				if (!currentUser || !auth.currentUser) {
					throw new Error("No anonymous user to link");
				}

				set({ isLoading: true, error: null });

				try {
					const credential = EmailAuthProvider.credential(email, password);
					await linkWithCredential(auth.currentUser, credential);
					// User state will be updated via onAuthStateChanged
				} catch (error) {
					set({ 
						isLoading: false, 
						error: { type: 'auth', message: 'Account linking failed' } as AppError 
					});
					throw error;
				}
			},

			logout: async () => {
				const { signOut } = await import("firebase/auth");
				set({ isLoading: true, error: null });

				try {
					await signOut(auth);
					// User state will be updated via onAuthStateChanged
				} catch (error) {
					set({ 
						isLoading: false, 
						error: { type: 'auth', message: 'Sign out failed' } as AppError 
					});
					throw error;
				}
			},

			refreshToken: async () => {
				const { user } = get();
				if (!user || !auth.currentUser) return;

				try {
					const idToken = await auth.currentUser.getIdToken(true);
					set({ idToken });
				} catch (error) {
					console.error("Failed to refresh token:", error);
					set({ 
						error: { type: 'auth', message: 'Failed to refresh authentication token' } as AppError 
					});
				}
			},
		}),
		{ name: "auth-store" }
	)
);