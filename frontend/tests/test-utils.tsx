import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type React from "react";

export function createTestQueryClient() {
	return new QueryClient({
		defaultOptions: {
			queries: {
				retry: false,
				staleTime: 0,
				gcTime: 0,
			},
			mutations: {
				retry: false,
			},
		},
	});
}

export function renderWithQuery(ui: React.ReactElement, client = createTestQueryClient()) {
	return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

// Extended render function with all providers
export function renderWithProviders(ui: React.ReactElement, client = createTestQueryClient()) {
	function Wrapper({ children }: { children: React.ReactNode }) {
		return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
	}

	return render(ui, { wrapper: Wrapper });
}
