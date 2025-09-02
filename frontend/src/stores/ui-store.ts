import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

interface UIState {
	// Theme
	theme: "light" | "dark" | "system";

	// Navigation
	sidebarOpen: boolean;

	// Actions
	setTheme: (theme: "light" | "dark" | "system") => void;
	toggleSidebar: () => void;
	setSidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>()(
	devtools(
		persist(
			(set) => ({
				// Initial state
				theme: "system",
				sidebarOpen: false,

				// Actions
				setTheme: (theme) => set({ theme }),
				
				toggleSidebar: () => 
					set((state) => ({ 
						sidebarOpen: !state.sidebarOpen 
					})),
				
				setSidebarOpen: (open) => set({ sidebarOpen: open }),
			}),
			{
				name: "ui-store",
				// Only persist theme preference, not sidebar state
				partialize: (state) => ({ theme: state.theme })
			}
		),
		{ name: "ui-store" }
	)
);