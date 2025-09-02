"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { AuthModal } from "@/components/auth/AuthModal";
import Link from "next/link";
import { useRouter } from "next/navigation";

export function HeaderAuth() {
  const { user, isAuthenticated, logout, isLoading } = useAuth();
  const [open, setOpen] = useState(false);
  const router = useRouter();

  // Open modal if URL contains ?auth=1
  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    if (params.get("auth") === "1") {
      setOpen(true);
    }
  }, []);

  const handleSignOut = async () => {
    try {
      await logout();
      try {
        await fetch("/api/auth/logout", { method: "POST", cache: "no-store" });
      } catch (e) {
        // Non-blocking
        console.warn("Logout session clear failed", e);
      }
      toast.success("Signed out successfully");
      router.refresh();
    } catch (error: any) {
      toast.error("Sign out failed");
      console.error("Sign out error:", error);
    }
  };

  const isLoggedIn = isAuthenticated && !!user && !user.isAnonymous;

  return (
    <>
      {/* Optional: show Create Post for logged-in users */}
      {isLoggedIn && (
        <Link href="/create-post" className="text-sm font-medium hover:underline">
          Create Post
        </Link>
      )}

      {/* Auth controls */}
      {isLoggedIn ? (
        <Button variant="outline" size="sm" onClick={handleSignOut} disabled={isLoading}>
          {isLoading ? "..." : "Logout"}
        </Button>
      ) : (
        <Button variant="default" size="sm" onClick={() => setOpen(true)} disabled={isLoading}>
          Login or Signup
        </Button>
      )}

      {/* Auth Modal */}
      <AuthModal open={open} onOpenChange={setOpen} />
    </>
  );
}
