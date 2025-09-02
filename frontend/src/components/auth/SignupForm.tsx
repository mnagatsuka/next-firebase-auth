"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { normalizeError } from "@/lib/utils/error";
import { auth } from "@/lib/firebase/client";
import { useAuthStore } from "@/stores/auth-store";
import { useRouter } from "next/navigation";


interface SignupFormProps {
	onSuccess?: () => void;
	onCancel?: () => void;
}

export function SignupForm({ onSuccess, onCancel }: SignupFormProps) {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const { signUpWithEmail, linkAnonymousWithEmail, isLoading, isAuthenticated, user } = useAuth();
    const router = useRouter();

	const upgrading = isAuthenticated && !!user?.isAnonymous;

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		if (!email || !password || !confirmPassword) {
			toast.error("Please fill in all fields");
			return;
		}

		if (password !== confirmPassword) {
			toast.error("Passwords do not match");
			return;
		}

		if (password.length < 6) {
			toast.error("Password must be at least 6 characters");
			return;
		}

		try {
			if (upgrading) {
				await linkAnonymousWithEmail(email, password);
				toast.success("Account upgraded successfully!");
			} else {
				await signUpWithEmail(email, password);
				toast.success("Account created successfully!");
			}

			// Issue HttpOnly session cookie and sync client token
			try {
				const current = auth.currentUser;
				if (current) {
					const idToken = await current.getIdToken(true);
					await fetch("/api/auth/login", {
						method: "POST",
						headers: { "Content-Type": "application/json" },
						body: JSON.stringify({ idToken }),
						cache: "no-store",
					});
					useAuthStore.getState().setIdToken(idToken);
				}
			} catch (e) {
				console.warn("Post-signup session sync failed", e);
			}

			onSuccess?.();
			router.refresh();
		} catch (error) {
			const normalizedError = normalizeError(error);
			if (upgrading && normalizedError.message?.includes("already")) {
				toast.error("This email is already in use. Please sign in instead.");
			} else {
				toast.error(normalizedError.message || (upgrading ? "Account upgrade failed" : "Sign up failed"));
			}
		}
	};

	return (
		<form onSubmit={handleSubmit} className="space-y-4">
			<div className="space-y-2">
				<Label htmlFor="email">Email</Label>
				<Input
					id="email"
					type="email"
					placeholder="Enter your email"
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					disabled={isLoading}
					required
				/>
			</div>

			<div className="space-y-2">
				<Label htmlFor="password">Password</Label>
				<Input
					id="password"
					type="password"
					placeholder={upgrading ? "Choose a new password" : "Choose a password"}
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					disabled={isLoading}
					required
					minLength={6}
				/>
			</div>

			<div className="space-y-2">
				<Label htmlFor="confirmPassword">Confirm Password</Label>
				<Input
					id="confirmPassword"
					type="password"
					placeholder="Confirm your password"
					value={confirmPassword}
					onChange={(e) => setConfirmPassword(e.target.value)}
					disabled={isLoading}
					required
					minLength={6}
				/>
			</div>

			<div className="flex gap-2">
				<Button type="submit" className="flex-1" disabled={isLoading}>
					{isLoading
						? upgrading
							? "Upgrading..."
							: "Creating account..."
						: upgrading
						? "Upgrade Account"
						: "Create Account"}
				</Button>
				{onCancel && (
					<Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
						Cancel
					</Button>
				)}
			</div>

			{upgrading && (
				<div className="mt-2 p-3 bg-blue-50 dark:bg-blue-950/50 rounded-md border border-blue-200 dark:border-blue-800">
					<p className="text-sm text-blue-800 dark:text-blue-200">
						<strong>What happens when you upgrade?</strong>
						<br />• Your current data and progress will be preserved
						<br />• You can sign in from any device
						<br />• Your account will be more secure
					</p>
				</div>
			)}
		</form>
	);
}
