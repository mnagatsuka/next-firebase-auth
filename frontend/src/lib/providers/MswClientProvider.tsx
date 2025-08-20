"use client";
import { use } from "react";

// Check if mocking should be enabled
const isMockingEnabled =
	process.env.NEXT_PUBLIC_API_MOCKING === "enabled" ||
	(process.env.NODE_ENV === "development" && process.env.NEXT_PUBLIC_API_MOCKING === undefined);

const mockingEnabledPromise =
	typeof window !== "undefined" && isMockingEnabled
		? import("@/mocks/browser").then(async ({ worker }) => {
				await worker.start({ onUnhandledRequest: "bypass" });
				console.log("🔧 MSW client enabled for API mocking");
			})
		: Promise.resolve().then(() => {
				if (typeof window !== "undefined") {
					console.log("✅ MSW client disabled - using real API endpoints");
				}
			});

export const MswClientProvider = ({ children }: { children: React.ReactNode }) => {
	use(mockingEnabledPromise);
	return children;
};
