/// <reference types="vitest" />

import path from "path";
import { defineConfig } from "vitest/config";

export default defineConfig({
	esbuild: {
		jsx: "automatic",
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
		},
	},
	define: {
		global: "globalThis",
	},
	test: {
		globals: true,
		environment: "jsdom",
		environmentOptions: {
			jsdom: {
				url: "http://localhost",
			},
		},
		setupFiles: ["./tests/setup.ts"],
		include: ["tests/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
		clearMocks: true,
		restoreMocks: true,
		unstubGlobals: true,
		coverage: {
			provider: "v8",
			reporter: ["text", "html"],
			reportsDirectory: "./coverage",
			include: ["src/**/*.{ts,tsx}"],
			exclude: ["**/*.stories.tsx", "**/__tests__/**", "src/mocks/**"],
		},
	},
});
