import { Suspense, type ReactNode } from "react";
import { MswClientProvider } from "./MswClientProvider";

// Server-side MSW setup for SSR
const isMockingEnabled = 
  process.env.NEXT_PUBLIC_API_MOCKING === "enabled" ||
  (process.env.NODE_ENV === "development" &&
    process.env.NEXT_PUBLIC_API_MOCKING !== "disabled");

if (process.env.NEXT_RUNTIME === "nodejs" && isMockingEnabled) {
  const { server } = await import("@/mocks/server");
  server.listen({ onUnhandledRequest: "bypass" });
}

export const MswProvider = ({ children }: { children: ReactNode }) => {
  return (
    <Suspense fallback={null}>
      <MswClientProvider>{children}</MswClientProvider>
    </Suspense>
  );
};