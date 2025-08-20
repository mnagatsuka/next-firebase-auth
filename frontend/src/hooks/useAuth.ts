"use client";

import { useCallback, useEffect } from "react";
import { useErrorHandler } from "../lib/errors";
import { useAppStore } from "../stores/app-store";

export const useAuth = () => {
	const {
		user,
		isAuthenticated,
		isLoading,
		error,
		signInWithEmail,
		signUpWithEmail,
		signInAnonymously,
		linkAnonymousWithEmail,
		logout,
		refreshToken,
		initializeAuth,
		setError,
	} = useAppStore();

	const { showError } = useErrorHandler();

	// Initialize Firebase Auth listener on first use
	useEffect(() => {
		initializeAuth();
	}, [initializeAuth]);

	// Wrapped auth actions with error handling
	const handleSignInWithEmail = useCallback(
		async (email: string, password: string) => {
			try {
				setError(null);
				await signInWithEmail(email, password);
			} catch (error) {
				showError(error, "Failed to sign in");
				throw error;
			}
		},
		[signInWithEmail, setError, showError],
	);

	const handleSignUpWithEmail = useCallback(
		async (email: string, password: string) => {
			try {
				setError(null);
				await signUpWithEmail(email, password);
			} catch (error) {
				showError(error, "Failed to create account");
				throw error;
			}
		},
		[signUpWithEmail, setError, showError],
	);

	const handleSignInAnonymously = useCallback(async () => {
		try {
			setError(null);
			await signInAnonymously();
		} catch (error) {
			showError(error, "Failed to sign in anonymously");
			throw error;
		}
	}, [signInAnonymously, setError, showError]);

	const handleLinkAnonymousWithEmail = useCallback(
		async (email: string, password: string) => {
			try {
				setError(null);
				await linkAnonymousWithEmail(email, password);
			} catch (error) {
				showError(error, "Failed to upgrade account");
				throw error;
			}
		},
		[linkAnonymousWithEmail, setError, showError],
	);

	const handleLogout = useCallback(async () => {
		try {
			setError(null);
			await logout();
		} catch (error) {
			showError(error, "Failed to sign out");
			throw error;
		}
	}, [logout, setError, showError]);

	return {
		// State
		user,
		isAuthenticated,
		isLoading,
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
	};
};
