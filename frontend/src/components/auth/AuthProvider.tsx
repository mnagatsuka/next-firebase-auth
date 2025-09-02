"use client";

import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useRef } from "react";
import { useAuth } from "../../hooks/useAuth";

interface AuthProviderProps {
	children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
	// Initialize auth on the client side
	const { authInitialized, user, signInAnonymously, initializeAuth } = useAuth();
	const pathname = usePathname();
	const router = useRouter();
	const attemptedAutoAnon = useRef(false);
    const lastAuthRef = useRef<{ uid: string | null; isAnon: boolean } | null>(null);

	// Initialize Firebase auth listener once at app start
	useEffect(() => {
		initializeAuth();
		// no cleanup to keep listener for app lifetime
	}, [initializeAuth]);

	// Global auto-anonymous sign-in on initial access
	useEffect(() => {
		if (attemptedAutoAnon.current) return;
		if (!authInitialized) return;
		if (user) return;
		attemptedAutoAnon.current = true;
		(async () => {
			try {
				await signInAnonymously();
				const { auth } = await import("@/lib/firebase/client");
				const current = auth.currentUser;
				if (current) {
					const idToken = await current.getIdToken();
					await fetch("/api/auth/login", {
						method: "POST",
						headers: { "Content-Type": "application/json" },
						body: JSON.stringify({ idToken }),
						cache: "no-store",
					});
				}
			} catch (err) {
				attemptedAutoAnon.current = false;
			}
		})();
	}, [authInitialized, user, signInAnonymously]);

	// Route-change ping to validate/reissue session cookie silently (only when a user exists)
	useEffect(() => {
		if (!authInitialized || !user) return;
		const ping = async () => {
			try {
				const res = await fetch("/api/auth/session", { cache: "no-store" });
				if (res.status === 401) {
					const { auth } = await import("@/lib/firebase/client");
					const current = auth.currentUser;
					if (current) {
						const idToken = await current.getIdToken(true);
						await fetch("/api/auth/login", {
							method: "POST",
							headers: { "Content-Type": "application/json" },
							body: JSON.stringify({ idToken }),
							cache: "no-store",
						});
					}
				}
			} catch {}
		};
		ping();
	}, [pathname, authInitialized, user]);

	// Refresh RSC when auth state materially changes (login/logout or anon->email)
	useEffect(() => {
		if (!authInitialized) return;
		const current = { uid: user?.uid ?? null, isAnon: !!user?.isAnonymous };
		const prev = lastAuthRef.current;
		const becameLoggedIn = !!current.uid && !current.isAnon && (!prev || !prev.uid || prev.isAnon || prev.uid !== current.uid);
		const loggedOut = !current.uid && !!prev?.uid;
		if (becameLoggedIn || loggedOut) {
			// Ensure server reads latest __session and rerenders header/list
			router.refresh();
		}
		lastAuthRef.current = current;
	}, [authInitialized, user?.uid, user?.isAnonymous, router]);

	return <>{children}</>;
}

// Export as default for easier imports
export default AuthProvider;
