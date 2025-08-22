# 15. API Mocking

This section outlines the rules and best practices for API mocking in Next.js projects using **MSW (Mock Service Worker)** with **Orval** code generation. Our approach standardizes mocking across development, testing, and Storybook environments while maintaining type safety through OpenAPI specifications.

## Goals

- **Single source of truth**: Generate mocks from OpenAPI specifications
- **Environment consistency**: Same handlers work in CSR, tests, and Storybook
- **Type safety**: Leverage generated TypeScript types for all mocking
- **Developer experience**: Simple toggle between real and mocked APIs
- **Realistic data**: Use OpenAPI examples for consistent mock responses

## 1. Dependencies and Setup

### Required Dependencies

Install MSW in the frontend workspace and Orval at the repository root:

```bash
# MSW for runtime mocking (frontend)
cd frontend && pnpm add -D msw

# Orval for code generation (repo root)
pnpm add -D orval
```

### Initialize MSW Service Worker

Generate the service worker file for browser mocking:

```bash
cd frontend && pnpm msw init public
```

This creates `frontend/public/mockServiceWorker.js` required for CSR mocking.

## 2. Environment Configuration

### Environment Variables

Configure mocking behavior in `frontend/.env.development`:

```env
NEXT_PUBLIC_API_MOCKING=enabled
NEXT_PUBLIC_API_BASE_URL=http://localhost:3000
```

**Rules:**
- Default to enabled in development for faster iteration
- Set `NEXT_PUBLIC_API_MOCKING=disabled` in production
- Use relative URLs in handlers for environment portability

## 3. Code Generation with Orval

### Orval Configuration

Configure Orval in `orval.config.ts` at the repository root:

```typescript
import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: {
      target: "openapi/dist/openapi.yml", // Bundled OpenAPI spec
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
        useExamples: true,              // Use OpenAPI examples
        generateEachHttpStatus: false,  // Avoid faker dependency
      },
      override: {
        query: {
          useQuery: true,
          useMutation: true,
        },
        mutator: {
          path: "frontend/src/lib/api/customFetch.ts",
          name: "customFetch",
        },
        fetch: {
          includeHttpResponseReturnType: false,
        },
        mock: {
          required: true,
        },
      },
    },
  },
});
```

### Package Scripts

Add generation scripts to root `package.json`:

```json
{
  "scripts": {
    "orval:gen": "orval --config orval.config.ts",
    "orval:watch": "orval --config orval.config.ts --watch"
  }
}
```

### Generated Output Structure

Running `pnpm orval:gen` creates:

```
frontend/src/lib/api/generated/
├── client.ts              # React Query hooks
├── client.msw.ts          # MSW handlers
└── schemas/               # TypeScript interfaces
    ├── index.ts
    ├── blogPost.ts
    └── ...
```

## 4. Handler Composition

### Primary Handler Entry Point

Maintain a single entry point that combines generated and custom handlers:

**File:** `frontend/src/mocks/handlers/index.ts`

```typescript
import { http, HttpResponse } from 'msw'
import { getBlogPostAPIMock } from '@/lib/api/generated/client.msw'

// Generated handlers from OpenAPI spec
const apiHandlers = getBlogPostAPIMock()

// Custom handlers for specific scenarios
const customHandlers = [
  // Health check endpoint
  http.get('/health', () => {
    return HttpResponse.json({ status: 'ok' })
  }),
  
  // Error scenarios for testing
  http.get('/posts/error-500', () => {
    return HttpResponse.json({
      status: 'error',
      error: { code: 'INTERNAL_SERVER_ERROR', message: 'Something went wrong' }
    }, { status: 500 })
  }),
]

export const handlers = [
  ...apiHandlers,
  ...customHandlers,
]
```

**Rules:**
- Generated handlers come first for default behavior
- Custom handlers can override generated ones when placed later
- Use relative paths (`/posts`) for environment portability
- Prefer OpenAPI examples over manual mock data

## 5. Client-Side Rendering (CSR) Setup

### MSW Provider

Create a provider to conditionally start MSW in the browser:

**File:** `frontend/src/lib/providers/MswProvider.tsx`

```typescript
"use client"

import { useEffect, useState } from "react"

export function MswProvider({ children }: { children: React.ReactNode }) {
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
      .finally(() => {
        if (active) setReady(true)
      })
    
    return () => {
      active = false
    }
  }, [mocking])

  if (!ready) return null
  
  return <>{children}</>
}
```

### Browser Worker Setup

**File:** `frontend/src/mocks/browser.ts`

```typescript
import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

export const worker = setupWorker(...handlers)
```

### Layout Integration

Wrap your app in the MSW provider:

**File:** `frontend/src/app/layout.tsx`

```typescript
import { MswProvider } from "@/lib/providers/MswProvider"
import { QueryProvider } from "@/lib/providers/QueryProvider"

export default function RootLayout({ 
  children 
}: { 
  children: React.ReactNode 
}) {
  return (
    <html lang="en">
      <body>
        <MswProvider>
          <QueryProvider>
            {children}
          </QueryProvider>
        </MswProvider>
      </body>
    </html>
  )
}
```

## 6. Testing Setup

### Node Server Setup

Create a server for Node.js environments (tests):

**File:** `frontend/src/mocks/server.ts`

```typescript
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
```

### Test Configuration

**File:** `tests/frontend/setup.ts`

```typescript
import '@testing-library/jest-dom'
import { beforeAll, afterAll, afterEach } from 'vitest'
import { server } from '@/mocks/server'

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### Vitest Integration

**File:** `tests/frontend/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config'
import path from 'path'

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts', './setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '../../frontend/src'),
    },
  },
})
```

## 7. Storybook Integration

### Storybook Preview Configuration

**File:** `frontend/.storybook/preview.ts`

```typescript
import type { Preview } from '@storybook/react'
import { worker } from '@/mocks/browser'

const preview: Preview = {
  loaders: [
    async () => {
      // Only start worker if not already started
      if (!worker.listHandlers().length) {
        await worker.start({ 
          onUnhandledRequest: 'warn', 
          quiet: false 
        })
      }
      return {}
    },
  ],
  
  beforeEach: async (context) => {
    // Reset handlers between stories
    worker.resetHandlers()
    
    // Allow per-story handler overrides
    const { parameters } = context
    if (parameters.msw?.handlers) {
      worker.use(...parameters.msw.handlers)
    }
  },
}

export default preview
```

### Per-Story Handler Overrides

```typescript
import type { Meta, StoryObj } from '@storybook/react'
import { http, HttpResponse } from 'msw'
import { PostCard } from './PostCard'

const meta: Meta<typeof PostCard> = {
  title: 'Components/PostCard',
  component: PostCard,
}

export default meta
type Story = StoryObj<typeof meta>

export const ErrorState: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get('/posts/123', () => {
          return HttpResponse.json(
            { error: 'Post not found' },
            { status: 404 }
          )
        }),
      ],
    },
  },
}
```

## 8. Best Practices

### Handler Organization

```typescript
// ✅ Good: Use relative paths
http.get('/posts', () => { /* handler */ })

// ❌ Bad: Absolute URLs break environment portability  
http.get('http://localhost:3000/posts', () => { /* handler */ })

// ✅ Good: Compose generated and custom handlers
export const handlers = [
  ...getBlogPostAPIMock(),  // Generated handlers first
  ...customErrorHandlers,   // Custom overrides second
]

// ❌ Bad: Manual handlers that duplicate OpenAPI
http.get('/posts', () => {
  return HttpResponse.json({
    // Manual data that duplicates OpenAPI examples
  })
})
```

### Mock Data Management

```typescript
// ✅ Good: Use OpenAPI examples for consistency
// Examples are defined in OpenAPI spec and used by Orval

// ✅ Good: Override specific scenarios
const errorHandlers = [
  http.get('/posts/500', () => {
    return HttpResponse.json({
      status: 'error',
      error: { code: 'INTERNAL_SERVER_ERROR' }
    }, { status: 500 })
  })
]

// ❌ Bad: Hardcoded mock data that diverges from API
const badHandler = http.get('/posts', () => {
  return HttpResponse.json({
    // Data structure that doesn't match OpenAPI
    items: [], // Should be 'posts' per API spec
  })
})
```

### Environment Handling

```typescript
// ✅ Good: Conditional mocking with sensible defaults
const mocking =
  process.env.NEXT_PUBLIC_API_MOCKING === "enabled" ||
  (process.env.NODE_ENV === "development" &&
    process.env.NEXT_PUBLIC_API_MOCKING !== "disabled")

// ✅ Good: Graceful degradation
if (!ready) return null  // Don't render until MSW is ready

// ❌ Bad: Always enabled mocking
const mocking = true  // Should be configurable
```

## 9. Development Workflow

### Daily Development

```bash
# 1. Update OpenAPI specification
vim openapi/spec/openapi.yml

# 2. Regenerate client and mocks
pnpm orval:gen

# 3. Start development with mocking enabled (default)
cd frontend && pnpm dev

# 4. Disable mocking when testing against real API
NEXT_PUBLIC_API_MOCKING=disabled pnpm dev
```

### Continuous Development

```bash
# Watch for OpenAPI changes and regenerate automatically
pnpm orval:watch
```

## 10. Troubleshooting

### Common Issues

**Service Worker Not Found**
```bash
# Solution: Initialize MSW service worker
cd frontend && pnpm msw init public
```

**Handler Mismatch**
- Ensure handlers use relative paths (`/posts`, not `http://localhost:3000/posts`)
- Check that generated handlers are imported correctly
- Verify OpenAPI examples match expected response structure

**Storybook Worker State**
```typescript
// Guard against multiple worker starts
if (!worker.listHandlers().length) {
  await worker.start({ onUnhandledRequest: 'warn' })
}
```

**Route Handlers Not Intercepted**
- MSW only intercepts HTTP requests, not internal function calls
- Use module-level mocks for testing internal functions
- Ensure API calls go through the network layer

### Debugging

```typescript
// Add logging to handlers for debugging
http.get('/posts', ({ request }) => {
  console.log('MSW intercepted:', request.url)
  return HttpResponse.json(mockData)
})

// List active handlers
console.log('Active handlers:', worker.listHandlers())
```

## 11. Integration with Existing Guidelines

This mocking strategy integrates with:

- **[05. Fetching & Caching](./05_fetching-caching.md)**: Use generated React Query hooks
- **[13. TypeScript](./13_typescript.md)**: Leverage generated types for type safety  
- **[14. Testing](./14_testing.md)**: Provide realistic mocks for integration tests
- **[17. Storybook](./17_storybook.md)**: Enable component development with mock data

## 12. Rules Summary

### Must Rules

- **MUST** use Orval to generate MSW handlers from OpenAPI specifications
- **MUST** use relative paths in all handlers for environment portability
- **MUST** compose generated and custom handlers in a single entry point
- **MUST** reset handlers between tests and stories
- **MUST** initialize MSW service worker for browser environments

### Should Rules

- **SHOULD** prefer OpenAPI examples over manual mock data
- **SHOULD** use environment variables to control mocking behavior
- **SHOULD** place custom handlers after generated ones for override capability
- **SHOULD** use TypeScript types from generated schemas

### Could Rules

- **COULD** add logging to handlers for debugging purposes
- **COULD** create per-story handler overrides for specific scenarios
- **COULD** implement request delays for testing loading states

This mocking strategy ensures consistent, type-safe API mocking across all development environments while maintaining excellent developer experience and integration with our OpenAPI-driven development workflow.