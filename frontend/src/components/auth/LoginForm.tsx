"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useAuth } from "../../hooks/useAuth";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";

interface LoginFormProps {
	onSuccess?: () => void;
	allowAnonymous?: boolean;
	redirectTo?: string;
}

export function LoginForm({ onSuccess, allowAnonymous = false }: LoginFormProps) {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const { signInWithEmail, signInAnonymously, isLoading } = useAuth();

	const handleEmailLogin = async (e: React.FormEvent) => {
		e.preventDefault();

		if (!email || !password) {
			toast.error("Please fill in all fields");
			return;
		}

		try {
			await signInWithEmail(email, password);
			toast.success("Signed in successfully!");
			onSuccess?.();
		} catch (error: any) {
			toast.error(error.message || "Sign in failed");
		}
	};

	const handleAnonymousLogin = async () => {
		try {
			await signInAnonymously();
			toast.success("Signed in anonymously!");
			onSuccess?.();
		} catch (error: any) {
			toast.error(error.message || "Anonymous sign in failed");
		}
	};

	return (
		<div className="space-y-6">
			<form onSubmit={handleEmailLogin} className="space-y-4">
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
						placeholder="Enter your password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						disabled={isLoading}
						required
					/>
				</div>

				<Button type="submit" className="w-full" disabled={isLoading}>
					{isLoading ? "Signing in..." : "Sign In"}
				</Button>
			</form>

			{allowAnonymous && (
				<>
					<div className="relative">
						<div className="absolute inset-0 flex items-center">
							<span className="w-full border-t" />
						</div>
						<div className="relative flex justify-center text-xs uppercase">
							<span className="bg-background px-2 text-muted-foreground">Or</span>
						</div>
					</div>

					<Button
						type="button"
						variant="outline"
						className="w-full"
						onClick={handleAnonymousLogin}
						disabled={isLoading}
					>
						Continue as Guest
					</Button>
				</>
			)}
		</div>
	);
}
