/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'
import path from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
      '@tests': path.resolve(__dirname, './tests'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    environmentOptions: {
      jsdom: {
        // Needed so jsdom enables localStorage/sessionStorage for persist
        url: 'http://localhost',
      },
    },
    setupFiles: ['./tests/frontend/setup.ts'],
    include: ['tests/frontend/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    clearMocks: true,
    restoreMocks: true,
    unstubGlobals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      reportsDirectory: './coverage',
      include: ['frontend/src/**/*.{ts,tsx}'],
      exclude: ['**/*.stories.tsx', '**/__tests__/**', 'frontend/src/mocks/**'],
    },
  },
})
