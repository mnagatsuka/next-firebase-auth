import "../src/app/globals.css";
import type { Preview } from "@storybook/nextjs-vite";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { worker } from "../src/mocks/browser";

// Create a QueryClient for Storybook that works with MSW
const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			retry: false,
			staleTime: 0,
			gcTime: 0,
		},
	},
});

const preview: Preview = {
	decorators: [
		(Story) =>
			React.createElement(QueryClientProvider, { client: queryClient }, React.createElement(Story)),
	],
	parameters: {
		controls: {
			expanded: true,
			matchers: {
				color: /(background|color)$/i,
				date: /Date$/i,
			},
		},
		a11y: {
			test: "todo",
		},
		docs: {
			autodocs: "tag",
		},
	},
	loaders: [
		async () => {
			// Start MSW worker once
			if (!worker.listHandlers().length) {
				await worker.start({
					onUnhandledRequest: "warn",
					quiet: false,
				});
			}
			return {};
		},
	],
	beforeEach: async (context) => {
		// Reset handlers and apply story-specific handlers
		worker.resetHandlers();
		const { parameters } = context;
		if (parameters.msw?.handlers) {
			worker.use(...parameters.msw.handlers);
		}
	},
};

export default preview;
