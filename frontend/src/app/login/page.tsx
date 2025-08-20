"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { LoginForm } from "../../components/auth/LoginForm";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "../../components/ui/card";
import { useAuth } from "../../hooks/useAuth";

export default function LoginPage() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const { isAuthenticated, user, isLoading } = useAuth();

	const redirectTo = searchParams.get("redirect") || "/";
	const isAnonymousFlow = searchParams.get("anonymous") === "true";

	// Redirect authenticated non-anonymous users
	useEffect(() => {
		if (!isLoading && isAuthenticated && !user?.isAnonymous) {
			router.push(redirectTo);
		}
	}, [isAuthenticated, user?.isAnonymous, isLoading, router, redirectTo]);

	const handleSuccess = () => {
		router.push(redirectTo);
	};

	if (isLoading) {
		return (
			<div className="min-h-screen flex items-center justify-center">
				<div className="text-center">
					<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
					<p>Loading...</p>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen flex items-center justify-center bg-background px-4">
			<Card className="w-full max-w-md">
				<CardHeader className="text-center">
					<CardTitle>{isAnonymousFlow ? "Sign In Required" : "Welcome Back"}</CardTitle>
					<CardDescription>
						{isAnonymousFlow
							? "Sign in to access this page, or continue as guest"
							: "Sign in to your account"}
					</CardDescription>
				</CardHeader>
				<CardContent>
					<LoginForm
						onSuccess={handleSuccess}
						allowAnonymous={isAnonymousFlow}
						redirectTo={redirectTo}
					/>

					<div className="mt-6 text-center text-sm">
						<span className="text-muted-foreground">Don't have an account? </span>
						<Link
							href={`/signup${redirectTo !== "/" ? `?redirect=${encodeURIComponent(redirectTo)}` : ""}`}
							className="font-medium text-primary hover:underline"
						>
							Sign up
						</Link>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
