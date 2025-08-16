# MSW + Orval Setup for Next.js 15 (App Router)

Standardizes API mocking across CSR, Storybook, and tests. Integrates MSW with Orval so mocks stay aligned with the OpenAPI spec and the current `frontend/` structure.

## Goals and Principles

- Single handler entry: `frontend/src/mocks/handlers/index.ts` composes generated and custom handlers.
- CSR uses Service Worker (`msw/browser`); tests use Node server (`msw/node`).
- Toggle via `NEXT_PUBLIC_API_MOCKING` with sensible dev defaults.
- Prefer relative URLs (e.g., `/posts`) so handlers match in every environment.
- Generate typed client, React Query hooks, and MSW handlers from OpenAPI using Orval.

## Dependencies

Install in `frontend/` for runtime mocking and at the repo root for codegen:

```bash
# MSW for runtime mocking (frontend)
cd frontend && pnpm add -D msw && cd ..

# Orval for typed client + MSW handlers (repo root)
pnpm add -D orval
```

Initialize the worker file once in `frontend/` (creates `public/mockServiceWorker.js`):

```bash
cd frontend && pnpm msw init public && cd ..
```

## Environment Variables

`frontend/.env.local`

```
NEXT_PUBLIC_API_MOCKING=enabled
NEXT_PUBLIC_API_BASE_URL=http://localhost:3000
```

- Dev default can be on; set `NEXT_PUBLIC_API_MOCKING=disabled` (or omit) in production.

## Orval: Generate Client, Hooks, and MSW Handlers

Orval reads the bundled OpenAPI spec at `openapi/dist/openapi.yml` (bundled by Redocly per `redocly.yml`) and generates:

- React Query client + hooks under `frontend/src/lib/api/generated/`.
- Schemas in `frontend/src/lib/api/generated/schemas/`.
- MSW handlers in `frontend/src/lib/api/generated/client.msw.ts`.

`orval.config.ts` (repo root):

```ts
import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: {
      // Use bundled OpenAPI for multi-file $ref support
      target: "openapi/dist/openapi.yml",
    },
    output: {
      target: "frontend/src/lib/api/generated/client.ts",
      schemas: "frontend/src/lib/api/generated/schemas",
      client: "react-query",
      httpClient: "fetch",
      mode: "split",
      clean: true,
      mock: {
        type: "msw",
        delay: false,
        useExamples: true,
        generateEachHttpStatus: true,
      },
      override: {
        query: {
          useQuery: true,
          useMutation: true,
        },
        mutator: {
          path: "frontend/src/lib/api/customFetch.ts",
          // Ensure this file exports a named function `fetcher`
        },
        fetch: { includeHttpResponseReturnType: false },
        mock: { required: true },
      },
    },
    hooks: {
      afterAllFilesWrite:
        "cd frontend && npx @biomejs/biome format --write src/lib/api/generated/",
    },
  },
});
```

Add scripts at the repo root:

```json
{
  "scripts": {
    "orval": "orval --config orval.config.ts",
    "orval:watch": "orval --config orval.config.ts --watch"
  }
}
```

Run generation:

```bash
pnpm orval
```

Generated files (example):

```
frontend/src/lib/api/generated/
  client.ts        # React Query hooks using fetcher()
  client.msw.ts    # generated MSW handlers from OpenAPI
  schemas/*.ts     # shared types from components.schemas
```

## Handlers: Compose Orval + Custom

Keep a single entry that merges Orval-generated handlers with any app-specific handlers. Use path-only patterns for custom ones.

`frontend/src/mocks/handlers/index.ts`

```ts
import { http, HttpResponse } from 'msw'
import { getBlogPostAPIMock } from '@/lib/api/generated/client.msw'

// Orval-generated handlers from the OpenAPI spec
const apiHandlers = getBlogPostAPIMock()

// Add or override any custom handlers here
const customHandlers = [
  http.get('/posts/health', () => HttpResponse.json({ status: 'ok' })),
  // ...error cases or feature-flagged mocks
]

export const handlers = [
  ...apiHandlers,
  ...customHandlers,
]
```

Notes:

- Orval generates handlers based on the spec (prefer examples in the spec for realistic data).
- Custom handlers later in the list can override generated ones for specific scenarios.

## CSR: Start The Service Worker

`frontend/src/lib/providers/MSWProvider.tsx`

```tsx
"use client"
import { useEffect, useState } from "react"

export function MSWProvider({ children }: { children: React.ReactNode }) {
  const mocking =
    process.env.NEXT_PUBLIC_API_MOCKING === "enabled" ||
    (process.env.NODE_ENV === "development" &&
      process.env.NEXT_PUBLIC_API_MOCKING !== "disabled")

  const [ready, setReady] = useState(!mocking)

  useEffect(() => {
    if (!mocking) return
    let active = true
    import("@/mocks/browser")
      .then(({ worker }) =>
        worker.start({
          onUnhandledRequest: "bypass",
          serviceWorker: { url: "/mockServiceWorker.js" },
        })
      )
      .finally(() => { if (active) setReady(true) })
    return () => { active = false }
  }, [mocking])

  if (!ready) return null
  return <>{children}</>
}
```

Wrap the app in `frontend/src/app/layout.tsx`:

```tsx
import { MSWProvider } from "@/lib/providers/MSWProvider"
import { QueryProvider } from "@/lib/providers/QueryProvider"

export const runtime = "nodejs" // enable SSR runtime when needed

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <MSWProvider>
          <QueryProvider>{children}</QueryProvider>
        </MSWProvider>
      </body>
    </html>
  )
}
```

CSR entry:

`frontend/src/mocks/browser.ts`

```ts
import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'
export const worker = setupWorker(...handlers)
```

## Node: Server For Tests

Use a Node server in tests.

`frontend/src/mocks/server.ts`

```ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'
export const server = setupServer(...handlers)
```

## Storybook

Start the worker in preview.

`frontend/.storybook/preview.ts`

```ts
import { worker } from '@/mocks/browser'

const preview = {
  loaders: [
    async () => {
      if (!worker.listHandlers().length) {
        await worker.start({ onUnhandledRequest: 'warn', quiet: false })
      }
      return {}
    },
  ],
  beforeEach: async (context) => {
    worker.resetHandlers()
    const { parameters } = context
    if (parameters.msw?.handlers) {
      worker.use(...parameters.msw.handlers)
    }
  },
}

export default preview
```

## Vitest/Jest Setup

`tests/frontend/setup.ts`

```ts
import '@testing-library/jest-dom'
import { beforeAll, afterAll, afterEach } from 'vitest'
import { server } from '@/mocks/server'

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

Example `tests/vitest.config.ts`:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts', './frontend/setup.ts'],
  },
})
```

## Fetching Guidelines

- Prefer relative paths so handlers match in CSR/tests; `fetcher` builds absolute URLs on the server.
- Centralize fetch in `frontend/src/lib/api/customFetch.ts` and let Orval use it via `mutator`.
- Only set an absolute `baseURL` when intentionally targeting another origin.

## Developer Workflow

- Edit the spec at `docs/specifications/api/openapi.yml`; Redocly bundles to `openapi/dist/openapi.yml` per `redocly.yml`.
- Run `pnpm orval` (or `pnpm orval:watch`) to regenerate the client and MSW handlers.
- Start the app with mocks: `NEXT_PUBLIC_API_MOCKING=enabled pnpm -C frontend dev`.
- Disable mocks: set `NEXT_PUBLIC_API_MOCKING=disabled`.

## Troubleshooting

- Service worker not found: ensure `frontend/public/mockServiceWorker.js` exists (run `pnpm -C frontend msw init public`).
- Handler mismatch: call relative URLs and keep handlers path-only; Orval uses `*/path` patterns for cross-origin safety.
- Storybook worker state: guard with `worker.listHandlers().length` before `worker.start()`.
- Route Handlers without outgoing HTTP are not intercepted (MSW mocks HTTP boundaries). Use module-level stubs in tests for internal functions.

