"use client";

import { useCallback } from "react";
import { useAuthStore } from "@/stores/auth-store";

export const useAuth = () => {
	const {
		user,
		isAuthenticated,
		isLoading,
		authInitialized,
		error,
		signInWithEmail,
		signUpWithEmail,
		signInAnonymously,
		linkAnonymousWithEmail,
		logout,
		refreshToken,
		initializeAuth,
		setError,
	} = useAuthStore();

	// Auth listener is initialized centrally in AuthProvider

	// Wrapped auth actions with error handling
	const handleSignInWithEmail = useCallback(
		async (email: string, password: string) => {
			try {
				setError(null);
				await signInWithEmail(email, password);
			} catch (error) {
				// Error is already set in the store by the auth action
				throw error;
			}
		},
		[signInWithEmail, setError],
	);

	const handleSignUpWithEmail = useCallback(
		async (email: string, password: string) => {
			try {
				setError(null);
				await signUpWithEmail(email, password);
			} catch (error) {
				// Error is already set in the store by the auth action
				throw error;
			}
		},
		[signUpWithEmail, setError],
	);

	const handleSignInAnonymously = useCallback(async () => {
		try {
			setError(null);
			await signInAnonymously();
		} catch (error) {
			// Error is already set in the store by the auth action
			throw error;
		}
	}, [signInAnonymously, setError]);

	const handleLinkAnonymousWithEmail = useCallback(
		async (email: string, password: string) => {
			try {
				setError(null);
				await linkAnonymousWithEmail(email, password);
			} catch (error) {
				// Error is already set in the store by the auth action
				throw error;
			}
		},
		[linkAnonymousWithEmail, setError],
	);

	const handleLogout = useCallback(async () => {
		try {
			setError(null);
			await logout();
		} catch (error) {
			// Error is already set in the store by the auth action
			throw error;
		}
	}, [logout, setError]);

	return {
		// State
		user,
		isAuthenticated,
		isLoading,
		authInitialized,
		error,
		isAnonymous: user?.isAnonymous ?? false,

		// Actions (with error handling)
		signInWithEmail: handleSignInWithEmail,
		signUpWithEmail: handleSignUpWithEmail,
		signInAnonymously: handleSignInAnonymously,
		linkAnonymousWithEmail: handleLinkAnonymousWithEmail,
		logout: handleLogout,
		refreshToken,
		clearError: () => setError(null),
		initializeAuth,
	};
};
