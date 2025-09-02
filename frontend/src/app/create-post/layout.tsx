import { ReactNode } from "react";
import { redirect } from "next/navigation";
import { getServerUser } from "@/lib/auth/session";

export default async function CreatePostLayout({ children }: { children: ReactNode }) {
  const user = await getServerUser();

  // Require a valid session cookie
  if (!user) {
    redirect("/?auth=1");
  }

  // Reject anonymous users for create-post
  const isAnonymous = (user as any)?.firebase?.sign_in_provider === "anonymous";
  if (isAnonymous) {
    redirect("/?auth=1");
  }

  return <>{children}</>;
}

