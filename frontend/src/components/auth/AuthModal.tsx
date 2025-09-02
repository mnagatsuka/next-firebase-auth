"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { LoginForm } from "@/components/auth/LoginForm";
import { SignupForm } from "@/components/auth/SignupForm";
import { Button } from "@/components/ui/button";

export interface AuthModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialView?: "login" | "signup";
}

export function AuthModal({ open, onOpenChange, initialView = "login" }: AuthModalProps) {
  const [view, setView] = useState<"login" | "signup">(initialView);

  useEffect(() => {
    if (open) setView(initialView);
  }, [open, initialView]);

  const handleSuccess = () => {
    onOpenChange(false);
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{view === "login" ? "Sign In" : "Create Account"}</DialogTitle>
        </DialogHeader>
        <div className="p-0 space-y-4">
        {view === "login" ? (
          <>
            <LoginForm onSuccess={handleSuccess} />
            <p className="text-center text-sm text-muted-foreground">
              Don&apos;t have an account? {" "}
              <Button variant="link" className="px-1" onClick={() => setView("signup")}>Sign up</Button>
            </p>
          </>
        ) : (
          <>
            <SignupForm onSuccess={handleSuccess} />
            <p className="text-center text-sm text-muted-foreground">
              Already have an account? {" "}
              <Button variant="link" className="px-1" onClick={() => setView("login")}>Sign in</Button>
            </p>
          </>
        )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
