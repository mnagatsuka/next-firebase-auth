import { ReactNode } from "react";
import { redirect } from "next/navigation";
import { getServerUser } from "@/lib/auth/session";

export default async function MyPostsLayout({ children }: { children: ReactNode }) {
  const user = await getServerUser();

  // No valid session cookie → prompt login
  if (!user) {
    redirect("/?auth=1");
  }

  // Anonymous users cannot access My Posts
  const isAnonymous = !!(user as any)?.firebase?.sign_in_provider && (user as any).firebase.sign_in_provider === "anonymous";
  if (isAnonymous) {
    redirect("/");
  }

  return <>{children}</>;
}

