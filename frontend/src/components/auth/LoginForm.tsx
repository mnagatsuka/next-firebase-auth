"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getErrorMessage } from "@/lib/utils/error";
import { auth } from "@/lib/firebase/client";
import { useAuthStore } from "@/stores/auth-store";
import { useRouter } from "next/navigation";

interface LoginFormProps {
	onSuccess?: () => void;
	allowAnonymous?: boolean;
	redirectTo?: string;
}

export function LoginForm({ onSuccess, allowAnonymous = false }: LoginFormProps) {
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const { signInWithEmail, signInAnonymously, isLoading } = useAuth();
    const router = useRouter();

	const handleEmailLogin = async (e: React.FormEvent) => {
		e.preventDefault();

		if (!email || !password) {
			toast.error("Please fill in all fields");
			return;
		}

		try {
			await signInWithEmail(email, password);
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
				console.warn("Post-login session sync failed", e);
			}
			toast.success("Signed in successfully!");
			onSuccess?.();
			router.refresh();
		} catch (error) {
			toast.error(getErrorMessage(error));
		}
	};

	const handleAnonymousLogin = async () => {
		try {
			await signInAnonymously();
			// Also issue a session cookie for guest sessions
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
				console.warn("Anonymous session sync failed", e);
			}
			toast.success("Signed in anonymously!");
			onSuccess?.();
			router.refresh();
		} catch (error) {
			toast.error(getErrorMessage(error));
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
