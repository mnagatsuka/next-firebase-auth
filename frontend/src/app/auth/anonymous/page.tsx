"use client";

import { signInAnonymously } from "firebase/auth";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { auth } from "@/lib/firebase/client";

export default function AnonymousLoginPage() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const redirectTo = searchParams?.get("redirect") || "/";
	const [status, setStatus] = useState("Initializing...");

	useEffect(() => {
		const performAnonymousLogin = async () => {
			try {
				setStatus("Signing in anonymously...");

				// Perform anonymous sign-in
				const result = await signInAnonymously(auth);
				const user = result.user;

				setStatus("Getting authentication token...");

				// Get ID token
				const idToken = await user.getIdToken();

				setStatus("Setting session cookie...");

				// POST to /api/auth/login to issue the HttpOnly session cookie
				const response = await fetch("/api/auth/login", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ idToken }),
				});

				if (!response.ok) {
					throw new Error(`Session cookie failed: ${response.status}`);
				}

				setStatus("Redirecting...");

				// Return to the original page
				router.replace(redirectTo);
			} catch (error) {
				console.error("Anonymous login failed:", error);
				setStatus(`Error: ${error instanceof Error ? error.message : "Unknown error"}`);

				// Fallback: redirect to original page anyway after a delay
				setTimeout(() => {
					router.replace(redirectTo);
				}, 3000);
			}
		};

		performAnonymousLogin();
	}, [redirectTo, router]);

	return (
		<div className="min-h-screen flex items-center justify-center bg-background">
			<div className="text-center space-y-4">
				<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
				<p className="text-sm text-muted-foreground">{status}</p>
				<p className="text-xs text-muted-foreground">Redirecting to: {redirectTo}</p>
			</div>
		</div>
	);
}
