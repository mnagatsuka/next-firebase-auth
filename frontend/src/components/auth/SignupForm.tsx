"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useAuth } from "../../hooks/useAuth";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";

interface SignupFormProps {
	onSuccess?: () => void;
	redirectTo?: string;
}

export function SignupForm({ onSuccess }: SignupFormProps) {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [confirmPassword, setConfirmPassword] = useState("");
	const { signUpWithEmail, isLoading } = useAuth();

	const handleSignup = async (e: React.FormEvent) => {
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
			await signUpWithEmail(email, password);
			toast.success("Account created successfully!");
			onSuccess?.();
		} catch (error: any) {
			toast.error(error.message || "Sign up failed");
		}
	};

	return (
		<form onSubmit={handleSignup} className="space-y-4">
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

			<Button type="submit" className="w-full" disabled={isLoading}>
				{isLoading ? "Creating account..." : "Create Account"}
			</Button>
		</form>
	);
}
