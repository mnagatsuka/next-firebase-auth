import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import { API_ENDPOINTS } from "../lib/constants";
import { type AppError, handleError } from "../lib/errors";
import { type User as FirebaseUser, firebaseAuth } from "../lib/firebase/auth";

interface User {
	uid: string;
	email: string | null;
	displayName: string | null;
	isAnonymous: boolean;
	emailVerified: boolean;
}

interface AppState {
	// User authentication state
	user: User | null;
	isAuthenticated: boolean;
	isLoading: boolean; // auth action or initialization state
	authInitialized: boolean; // first onAuthStateChanged fired
	idToken: string | null;

	// App preferences
	theme: "light" | "dark" | "system";

	// UI state
	sidebarOpen: boolean;

	// Actions
	setUser: (user: User | null) => void;
	setIdToken: (token: string | null) => void;
	setLoading: (loading: boolean) => void;
	setTheme: (theme: "light" | "dark" | "system") => void;
	toggleSidebar: () => void;
	setSidebarOpen: (open: boolean) => void;
	setError: (error: AppError | null) => void;

	// State
	error: AppError | null;

	// Firebase Auth actions
	signInWithEmail: (email: string, password: string) => Promise<void>;
	signUpWithEmail: (email: string, password: string) => Promise<void>;
	signInAnonymously: () => Promise<void>;
	linkAnonymousWithEmail: (email: string, password: string) => Promise<void>;
	logout: () => Promise<void>;
	refreshToken: () => Promise<void>;
	initializeAuth: () => void;
}

// Helper function to convert Firebase User to app User
const mapFirebaseUser = (firebaseUser: FirebaseUser): User => ({
	uid: firebaseUser.uid,
	email: firebaseUser.email,
	displayName: firebaseUser.displayName,
	isAnonymous: firebaseUser.isAnonymous,
	emailVerified: firebaseUser.emailVerified,
});

// Helper function to make authenticated API calls
const makeAuthenticatedRequest = async (url: string, options: RequestInit = {}) => {
	const response = await fetch(url, {
		...options,
		headers: {
			"Content-Type": "application/json",
			...options.headers,
		},
	});

	if (!response.ok) {
		const error = await response.json().catch(() => ({ message: "Request failed" }));
		throw new Error(error.message || "Request failed");
	}

	return response.json();
};

export const useAppStore = create<AppState>()(
	devtools(
		persist(
			(set) => ({
				// Initial state
				user: null,
				isAuthenticated: false,
				isLoading: true,
				authInitialized: false,
				idToken: null,
				theme: "system",
				sidebarOpen: false,
				error: null,

				// Basic actions
				setUser: (user) =>
					set(
						() => ({
							user,
							isAuthenticated: !!user,
						}),
						false,
						"setUser",
					),

				setIdToken: (idToken) => set({ idToken }, false, "setIdToken"),

				setLoading: (isLoading) => set({ isLoading }, false, "setLoading"),

				setTheme: (theme) => set({ theme }, false, "setTheme"),

				toggleSidebar: () =>
					set(
						(state) => ({
							sidebarOpen: !state.sidebarOpen,
						}),
						false,
						"toggleSidebar",
					),

				setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }, false, "setSidebarOpen"),

				setError: (error) => set({ error }, false, "setError"),

				// Firebase Auth actions
				signInWithEmail: async (email: string, password: string) => {
					try {
						set({ isLoading: true }, false, "signInWithEmail:start");

						const { user: firebaseUser } = await firebaseAuth.signInWithEmail(email, password);
						const idToken = await firebaseUser.getIdToken();

						// Set session cookie via API
						await makeAuthenticatedRequest(API_ENDPOINTS.AUTH.LOGIN, {
							method: "POST",
							body: JSON.stringify({ idToken }),
						});

						const user = mapFirebaseUser(firebaseUser);
						set(
							{
								user,
								isAuthenticated: true,
								idToken,
								isLoading: false,
							},
							false,
							"signInWithEmail:success",
						);
					} catch (error) {
						const appError = handleError(error, "signInWithEmail");
						set({ isLoading: false, error: appError }, false, "signInWithEmail:error");
						throw appError;
					}
				},

				signUpWithEmail: async (email: string, password: string) => {
					try {
						set({ isLoading: true }, false, "signUpWithEmail:start");

						const { user: firebaseUser } = await firebaseAuth.signUpWithEmail(email, password);
						const idToken = await firebaseUser.getIdToken();

						// Set session cookie via API
						await makeAuthenticatedRequest(API_ENDPOINTS.AUTH.LOGIN, {
							method: "POST",
							body: JSON.stringify({ idToken }),
						});

						const user = mapFirebaseUser(firebaseUser);
						set(
							{
								user,
								isAuthenticated: true,
								idToken,
								isLoading: false,
							},
							false,
							"signUpWithEmail:success",
						);
					} catch (error) {
						console.error("Sign up error:", error);
						set({ isLoading: false }, false, "signUpWithEmail:error");
						throw error;
					}
				},

				signInAnonymously: async () => {
					try {
						set({ isLoading: true }, false, "signInAnonymously:start");

						// If there's already a current user, just refresh cookie/token
						const current = firebaseAuth.getCurrentUser();
						if (current) {
							const idToken = await current.getIdToken(true);
							await makeAuthenticatedRequest(API_ENDPOINTS.AUTH.LOGIN, {
								method: "POST",
								body: JSON.stringify({ idToken }),
							});
							const user = mapFirebaseUser(current);
							set(
								{ user, isAuthenticated: true, idToken, isLoading: false },
								false,
								"signInAnonymously:refresh-session",
							);
							return;
						}

						// No current user: perform anonymous sign-in
						const { user: firebaseUser } = await firebaseAuth.signInAnonymously();
						const idToken = await firebaseUser.getIdToken();

						await makeAuthenticatedRequest(API_ENDPOINTS.AUTH.LOGIN, {
							method: "POST",
							body: JSON.stringify({ idToken }),
						});

						const user = mapFirebaseUser(firebaseUser);
						set(
							{ user, isAuthenticated: true, idToken, isLoading: false },
							false,
							"signInAnonymously:success",
						);
					} catch (error) {
						console.error("Anonymous sign in error:", error);
						set({ isLoading: false }, false, "signInAnonymously:error");
						throw error;
					}
				},

				linkAnonymousWithEmail: async (email: string, password: string) => {
					try {
						set({ isLoading: true }, false, "linkAnonymousWithEmail:start");

						const { user: firebaseUser } = await firebaseAuth.linkAnonymousWithEmail(
							email,
							password,
						);
						const idToken = await firebaseUser.getIdToken();

						// Update session cookie via API
						await makeAuthenticatedRequest(API_ENDPOINTS.AUTH.LOGIN, {
							method: "POST",
							body: JSON.stringify({ idToken }),
						});

						const user = mapFirebaseUser(firebaseUser);
						set(
							{
								user,
								isAuthenticated: true,
								idToken,
								isLoading: false,
							},
							false,
							"linkAnonymousWithEmail:success",
						);
					} catch (error) {
						console.error("Link anonymous user error:", error);
						set({ isLoading: false }, false, "linkAnonymousWithEmail:error");
						throw error;
					}
				},

				refreshToken: async () => {
					try {
						const idToken = await firebaseAuth.getIdToken(true); // Force refresh
						if (idToken) {
							set({ idToken }, false, "refreshToken:success");
						}
					} catch (error) {
						console.error("Token refresh error:", error);
						// Clear auth state on token refresh failure
						set(
							{
								user: null,
								isAuthenticated: false,
								idToken: null,
							},
							false,
							"refreshToken:error",
						);
					}
				},

				logout: async () => {
					try {
						set({ isLoading: true }, false, "logout:start");

						// Sign out from Firebase
						await firebaseAuth.signOut();

						// Clear session cookie via API
						await makeAuthenticatedRequest(API_ENDPOINTS.AUTH.LOGOUT, {
							method: "POST",
						}).catch(() => {
							// Continue even if API call fails
							console.warn("Session cookie clear failed, but continuing logout");
						});

						set(
							{
								user: null,
								isAuthenticated: false,
								idToken: null,
								isLoading: false,
							},
							false,
							"logout:success",
						);
					} catch (error) {
						console.error("Logout error:", error);
						// Clear state even on error
						set(
							{
								user: null,
								isAuthenticated: false,
								idToken: null,
								isLoading: false,
							},
							false,
							"logout:error",
						);
					}
				},

				initializeAuth: () => {
					// Set up Firebase auth state listener
					set({ isLoading: true }, false, "initializeAuth:start");
					firebaseAuth.onAuthStateChanged(async (firebaseUser) => {
						try {
							if (firebaseUser) {
								const user = mapFirebaseUser(firebaseUser);
								const idToken = await firebaseUser.getIdToken();
								set(
									{
										user,
										isAuthenticated: true,
										idToken,
										isLoading: false,
										authInitialized: true,
									},
									false,
									"initializeAuth:userFound",
								);
							} else {
								set(
									{
										user: null,
										isAuthenticated: false,
										idToken: null,
										isLoading: false,
										authInitialized: true,
									},
									false,
									"initializeAuth:noUser",
								);
							}
						} catch (error) {
							console.error("Auth state change error:", error);
							set(
								{
									user: null,
									isAuthenticated: false,
									idToken: null,
									isLoading: false,
									authInitialized: true,
								},
								false,
								"initializeAuth:error",
							);
						}
					});
				},
			}),
			{
				name: "app-store",
				partialize: (state) => ({
					theme: state.theme,
					sidebarOpen: state.sidebarOpen,
					// Don't persist sensitive auth data
				}),
			},
		),
		{ name: "AppStore" },
	),
);
