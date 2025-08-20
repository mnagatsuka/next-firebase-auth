import { type ReactNode, Suspense } from "react";
import { MswClientProvider } from "./MswClientProvider";

// Server-side MSW setup for SSR
const isMockingEnabled =
	process.env.NEXT_PUBLIC_API_MOCKING === "enabled" ||
	(process.env.NODE_ENV === "development" && process.env.NEXT_PUBLIC_API_MOCKING === undefined);

if (process.env.NEXT_RUNTIME === "nodejs") {
	if (isMockingEnabled) {
		const { server } = await import("@/mocks/server");
		server.listen({ onUnhandledRequest: "bypass" });
		console.log("🔧 MSW server enabled for API mocking");
	} else {
		console.log("✅ MSW disabled - using real API endpoints");
	}
}

export const MswProvider = ({ children }: { children: ReactNode }) => {
	return (
		<Suspense fallback={null}>
			<MswClientProvider>{children}</MswClientProvider>
		</Suspense>
	);
};
