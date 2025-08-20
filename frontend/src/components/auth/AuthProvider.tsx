"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useRef } from "react";
import { useAuth } from "../../hooks/useAuth";

interface AuthProviderProps {
	children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
	// Initialize auth on the client side
	const { isAuthenticated, isLoading, signInAnonymously } = useAuth();
	const pathname = usePathname();
	const attempted = useRef(false);

	// Background auto-anonymous: enabled globally, skip on /login and /signup
	useEffect(() => {
		if (attempted.current) return;
		const skip = pathname?.startsWith("/login") || pathname?.startsWith("/signup");
		if (!skip && !isAuthenticated && !isLoading) {
			attempted.current = true;
			signInAnonymously().catch((err) => {
				console.warn("Auto anonymous sign-in failed:", err);
				// allow retry on next mount/navigation
				attempted.current = false;
			});
		}
	}, [pathname, isAuthenticated, isLoading, signInAnonymously]);

	return <>{children}</>;
}

// Export as default for easier imports
export default AuthProvider;
