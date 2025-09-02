"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "./useAuth";

export const useRequireAuth = (redirectTo = "/?auth=1") => {
	const { isAuthenticated, isLoading, user } = useAuth();
	const router = useRouter();

	useEffect(() => {
		if (!isLoading && !isAuthenticated) {
			router.push(redirectTo);
		}
	}, [isAuthenticated, isLoading, router, redirectTo]);

	return {
		isAuthenticated,
		isLoading,
		user,
		// Redirect is handled automatically
	};
};

// Hook for components that require non-anonymous users
export const useRequireNonAnonymousAuth = (redirectTo = "/?auth=1") => {
	const { isAuthenticated, isLoading, user } = useAuth();
	const router = useRouter();

	useEffect(() => {
		if (!isLoading && (!isAuthenticated || user?.isAnonymous)) {
			router.push(redirectTo);
		}
	}, [isAuthenticated, isLoading, user?.isAnonymous, router, redirectTo]);

	return {
		isAuthenticated: isAuthenticated && !user?.isAnonymous,
		isLoading,
		user,
	};
};
