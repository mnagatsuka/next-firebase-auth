import { beforeEach, describe, expect, it } from "vitest";
import { useAppStore } from "@/stores/app-store";

// Helper to read current store state
const getState = () => useAppStore.getState();

describe("stores/app-store", () => {
	beforeEach(() => {
		// Reset state; mirror initial values in store
		useAppStore.setState({
			user: null,
			isAuthenticated: false,
			isLoading: false,
			theme: "system",
			sidebarOpen: false,
		});
		// Also clear any persisted storage to avoid cross-test pollution
		try {
			localStorage.clear();
		} catch {}
	});

	it("sets user and updates authentication", () => {
		const { setUser } = getState();
		setUser({
			uid: "1",
			email: "a@example.com",
			displayName: "Alice",
			isAnonymous: false,
			emailVerified: true,
		});

		const s = getState();
		expect(s.user?.uid).toBe("1");
		expect(s.isAuthenticated).toBe(true);
	});

	it("toggles and sets sidebar state", () => {
		const { toggleSidebar, setSidebarOpen } = getState();

		toggleSidebar();
		expect(getState().sidebarOpen).toBe(true);

		setSidebarOpen(false);
		expect(getState().sidebarOpen).toBe(false);
	});

	it("updates theme", () => {
		const { setTheme } = getState();
		setTheme("dark");
		expect(getState().theme).toBe("dark");
	});

	it("handles loading and logout", () => {
		const { setUser, setLoading, logout } = getState();
		setUser({
			uid: "2",
			email: "b@example.com",
			displayName: "Bob",
			isAnonymous: false,
			emailVerified: true,
		});
		setLoading(true);

		expect(getState().isLoading).toBe(true);
		expect(getState().isAuthenticated).toBe(true);

		logout();
		expect(getState().user).toBeNull();
		expect(getState().isAuthenticated).toBe(false);
	});
});
