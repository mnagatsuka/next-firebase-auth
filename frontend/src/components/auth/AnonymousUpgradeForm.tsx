"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useAuth } from "../../hooks/useAuth";
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Input } from "../ui/input";
import { Label } from "../ui/label";

interface AnonymousUpgradeFormProps {
	onSuccess?: () => void;
	onCancel?: () => void;
}

export function AnonymousUpgradeForm({ onSuccess, onCancel }: AnonymousUpgradeFormProps) {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const { linkAnonymousWithEmail, isLoading, user } = useAuth();

	const handleUpgrade = async (e: React.FormEvent) => {
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
			await linkAnonymousWithEmail(email, password);
			toast.success("Account upgraded successfully! You can now sign in with your email.");
			onSuccess?.();
		} catch (error: any) {
			console.error("Account upgrade error:", error);
			if (error.message?.includes("already-exists")) {
				toast.error("An account with this email already exists. Please sign in instead.");
			} else {
				toast.error(error.message || "Account upgrade failed");
			}
		}
	};

	if (!user?.isAnonymous) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>Account Status</CardTitle>
					<CardDescription>You already have a registered account.</CardDescription>
				</CardHeader>
			</Card>
		);
	}

	return (
		<Card>
			<CardHeader>
				<CardTitle>Upgrade Your Account</CardTitle>
				<CardDescription>
					Create a permanent account to save your progress and access your data from any device.
				</CardDescription>
			</CardHeader>
			<CardContent>
				<form onSubmit={handleUpgrade} className="space-y-4">
					<div className="space-y-2">
						<Label htmlFor="email">Email Address</Label>
						<Input
							id="email"
							type="email"
							placeholder="Enter your email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							disabled={isLoading}
							required
						/>
						<p className="text-xs text-muted-foreground">
							You'll use this email to sign in to your account.
						</p>
					</div>

					<div className="space-y-2">
						<Label htmlFor="password">Password</Label>
						<Input
							id="password"
							type="password"
							placeholder="Choose a password"
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

					<div className="flex space-x-2">
						<Button type="submit" className="flex-1" disabled={isLoading}>
							{isLoading ? "Upgrading..." : "Upgrade Account"}
						</Button>
						{onCancel && (
							<Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
								Cancel
							</Button>
						)}
					</div>
				</form>

				<div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950/50 rounded-md border border-blue-200 dark:border-blue-800">
					<p className="text-sm text-blue-800 dark:text-blue-200">
						<strong>What happens when you upgrade?</strong>
						<br />• Your current data and progress will be preserved
						<br />• You can sign in from any device
						<br />• Your account will be more secure
					</p>
				</div>
			</CardContent>
		</Card>
	);
}
