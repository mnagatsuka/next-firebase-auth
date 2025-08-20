"use client";

import Link from "next/link";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

export function HeaderAuth() {
	const { user, isAuthenticated, logout, isLoading } = useAuth();

	const handleSignOut = async () => {
		try {
			await logout();
			toast.success("Signed out successfully");
		} catch (error: any) {
			toast.error("Sign out failed");
			console.error("Sign out error:", error);
		}
	};

	const getDisplayName = () => {
		if (!user) return "";
		return user.displayName || user.email || "User";
	};

	const handleUpgradeAccount = () => {
		// For anonymous users, redirect to signup to upgrade their account
		window.location.href = "/signup";
	};

	if (isAuthenticated && user) {
		return (
			<>
				<Link href="/create-post" className="text-sm font-medium hover:underline">
					Create Post
				</Link>
				<div className="flex items-center space-x-3">
					<div className="flex items-center space-x-2">
						<span className="text-sm">Welcome, {getDisplayName()}</span>
						{user.isAnonymous && (
							<Badge variant="secondary" className="text-xs">
								Guest
							</Badge>
						)}
					</div>
					<div className="flex items-center space-x-2">
						{user.isAnonymous && (
							<Button
								variant="outline"
								size="sm"
								onClick={handleUpgradeAccount}
								disabled={isLoading}
							>
								Create Account
							</Button>
						)}
						<Button variant="outline" size="sm" onClick={handleSignOut} disabled={isLoading}>
							{isLoading ? "..." : "Sign Out"}
						</Button>
					</div>
				</div>
			</>
		);
	}

	return (
		<div className="flex items-center space-x-2">
			<Link href="/login">
				<Button variant="ghost" size="sm">
					Sign In
				</Button>
			</Link>
			<Link href="/signup">
				<Button variant="default" size="sm">
					Sign Up
				</Button>
			</Link>
		</div>
	);
}
