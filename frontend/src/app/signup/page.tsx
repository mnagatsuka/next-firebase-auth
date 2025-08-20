"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { AnonymousUpgradeForm } from "../../components/auth/AnonymousUpgradeForm";
import { SignupForm } from "../../components/auth/SignupForm";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "../../components/ui/card";
import { useAuth } from "../../hooks/useAuth";

export default function SignupPage() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const { isAuthenticated, user, isLoading } = useAuth();

	const redirectTo = searchParams.get("redirect") || "/";

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

	// Show anonymous upgrade form if user is anonymous
	if (isAuthenticated && user?.isAnonymous) {
		return (
			<div className="min-h-screen flex items-center justify-center bg-background px-4">
				<div className="w-full max-w-md">
					<AnonymousUpgradeForm onSuccess={handleSuccess} onCancel={() => router.push("/")} />

					<div className="mt-6 text-center text-sm">
						<Link href="/" className="text-muted-foreground hover:underline">
							← Back to home
						</Link>
					</div>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen flex items-center justify-center bg-background px-4">
			<Card className="w-full max-w-md">
				<CardHeader className="text-center">
					<CardTitle>Create Account</CardTitle>
					<CardDescription>Sign up to get started with your account</CardDescription>
				</CardHeader>
				<CardContent>
					<SignupForm onSuccess={handleSuccess} redirectTo={redirectTo} />

					<div className="mt-6 text-center text-sm">
						<span className="text-muted-foreground">Already have an account? </span>
						<Link
							href={`/login${redirectTo !== "/" ? `?redirect=${encodeURIComponent(redirectTo)}` : ""}`}
							className="font-medium text-primary hover:underline"
						>
							Sign in
						</Link>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
