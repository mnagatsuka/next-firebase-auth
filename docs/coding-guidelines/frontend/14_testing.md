# 14. Testing

# Strategy

This section defines the rules and best practices for testing in Next.js projects, inspired by the **Testing Trophy** concept from Kent C. Dodds. Our focus is on optimizing **return on investment (ROI)** by prioritizing the most valuable and durable test types: static analysis, integration testing, and minimal end-to-end (E2E) testing.

Our goals are:
- Establish a balanced and efficient testing strategy
- Build confidence through realistic, resilient, well-covered tests
- Leverage both automated and manual testing where appropriate
- Co-locate tests with components for maintainability


## 1. Testing Layers Overview

Following the Testing Trophy model:

1. **Static Analysis** (base)
2. **Unit Tests**
3. **Integration Tests** (primary focus)
4. **End-to-End (E2E) Tests** (minimal, critical paths only)

This structure is designed around the **return on investment (ROI)** of each test type—balancing cost, speed, and confidence. Integration tests offer the best balance for frontend projects.:contentReference[oaicite:0]{index=0}


## 2. Test Layer Trade-Offs

As you move up the trophy:
- **Cost** increases – more complex setup; slower to author and maintain
- **Speed** decreases – E2E tests run slower than unit or integration tests
- **Confidence** increases – higher-level tests offer greater assurance the app works as intended:contentReference[oaicite:1]{index=1}

Integration tests hit a “sweet spot”: they’re fast enough to run regularly while offering meaningful coverage.:contentReference[oaicite:2]{index=2}


## 3. Confidence Pedestal Principles

Tests should:
1. Be **Realistic** – resemble user interactions
2. Be **Resilient** – reduce false positives/negatives
3. Provide **Adequate Coverage** – thorough but not redundant:contentReference[oaicite:3]{index=3}

Static analysis underlies this pedestal, ensuring code quality before tests run.


## 4. Testing Tools & Practices

| Layer                | Purpose & Tools |
|---------------------|-----------------|
| Static Analysis      | Catch syntax/style issues early (e.g., ESLint, type checking) |
| Unit Testing         | Validate isolated logic with Jest or Vitest |
| Integration Testing  | Test component interactions and APIs; use React Testing Library, Vitest, MSW |
| E2E Testing (Minimal)| Cover critical user flows via Playwright or Cypress |

**Rules:**
- Always include static analysis via linting and type checks.
- Write unit tests for core logic.
- Invest most effort in thorough integration tests.
- Limit E2E tests to essential paths to ensure confidence efficiently.


## 5. Organizing Tests

- **Co-locate** tests with components and routes (`component.test.tsx`, `fetch-data.test.ts`).
- Use **descriptive test names**: `Component › behavior › should …`.
- Leverage **data-driven testing** (e.g., Vitest’s `.each()` tests) for exhaustive scenarios with minimal boilerplate.:contentReference[oaicite:4]{index=4}


## 6. Strategic Summary

Follow this ordering for testing effort:
1. **Static Analysis** – ALWAYS
2. **Unit Tests** – for small, pure logic
3. **Integration Tests** – for robust coverage
4. **E2E Tests** – only key user journeys

This approach ensures high ROI: strong confidence while limiting test maintenance and execution costs.


By adopting the Testing Trophy methodology, we maintain testing that is **sustainable, reliable, and confidence-inspiring**, while avoiding over-testing and test suite bloat.


# Examples

Updated samples that use **TanStack Query** in Client Components, tested with **Vitest**, **React Testing Library**, **MSW**, and **Playwright**—aligned to the **Testing Trophy**.

## Why this approach?
- **Max ROI**: Focus on **integration tests** that reflect user behavior with fast feedback.
- **Confidence**: Static analysis + strict TypeScript, then integration tests, plus a slim E2E layer.
- **Consistency**: Client Components that fetch server state use **TanStack Query** per our stack.

## Prerequisites

Install dev deps:
```bash
pnpm add -D vitest @testing-library/react @testing-library/user-event jsdom \
  msw @testing-library/jest-dom \
  @types/testing-library__jest-dom playwright \
  @tanstack/react-query
````

`vitest.config.ts` (JSDOM + setup):

```ts
/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
    css: true,
    globals: true
  }
})
```

`test/setup.ts` (RTL + MSW, quiet TanStack Query logger in tests):

```ts
import '@testing-library/jest-dom'
import { afterAll, afterEach, beforeAll, vi } from 'vitest'
import { setupServer } from 'msw/node'
import { handlers } from './test-handlers'
import { setLogger } from '@tanstack/react-query'

// Silence react-query network error logging in test output
setLogger({
  log: console.log,
  warn: console.warn,
  error: vi.fn() // swallow errors (assert via UI, not console)
})

export const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

`test/test-handlers.ts` (MSW handlers):

```ts
import { rest } from 'msw'

export const handlers = [
  rest.get('/api/users', (_req, res, ctx) =>
    res(ctx.status(200), ctx.json({ id: 'u1', name: 'Jane Doe' }))
  )
]
```

`test/test-utils.tsx` (render helper with QueryClientProvider):

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import React from 'react'

export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false }
    }
  })
}

export function renderWithQuery(ui: React.ReactElement, client = createTestQueryClient()) {
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}
```

`package.json` scripts (excerpt):

```json
{
  "scripts": {
    "lint": "biome check .",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "e2e": "playwright test",
    "e2e:headed": "playwright test --headed",
    "e2e:report": "playwright show-report"
  }
}
```

### Why these prereqs?

* **TanStack Query**: Consistent client-side server-state fetching, caching, retries, invalidation.
* **RTL + MSW**: User-focused assertions with realistic network behavior, no real HTTP.
* **Vitest + JSDOM**: Fast component tests without a browser; **Playwright** for a thin E2E layer.
* **Biome + TS**: Static guarantees before runtime tests.

## A) Static Analysis (Biome + TypeScript)

`biome.json`:

```json
{
  "$schema": "https://biomejs.dev/schemas/1.0.0/schema.json",
  "formatter": { "enabled": true, "lineWidth": 100 },
  "linter": { "enabled": true, "rules": { "recommended": true } }
}
```

Run:

```bash
pnpm run lint
pnpm run typecheck
```

Explanation: Catch issues early, gate PRs, and keep parity with our strict TS rules.

## B) Unit Tests (Vitest)

Pure function:

```ts
// src/lib/calc.ts
export function sum(a: number, b: number): number {
  return a + b
}
```

Unit test:

```ts
// src/lib/calc.test.ts
import { describe, it, expect } from 'vitest'
import { sum } from './calc'

describe('sum', () => {
  it('adds two numbers', () => {
    expect(sum(2, 3)).toBe(5)
  })
})
```

Zod schema:

```ts
// src/lib/schemas.ts
import { z } from 'zod'
export const UserSchema = z.object({ id: z.string(), name: z.string().min(1) })
export type User = z.infer<typeof UserSchema>
```

Test:

```ts
// src/lib/schemas.test.ts
import { describe, it, expect } from 'vitest'
import { UserSchema } from './schemas'

describe('UserSchema', () => {
  it('validates a user', () => {
    const parsed = UserSchema.safeParse({ id: 'u1', name: 'Jane' })
    expect(parsed.success).toBe(true)
  })
  it('rejects invalid user', () => {
    const parsed = UserSchema.safeParse({ id: 'u1', name: '' })
    expect(parsed.success).toBe(false)
  })
})
```

Explanation: Unit tests cover pure, framework-agnostic logic quickly and reliably.

## C) Integration Tests (RTL + MSW + TanStack Query)

Client component using TanStack Query:

```tsx
// src/app/_components/UserCard.tsx
'use client'

import { useQuery } from '@tanstack/react-query'

type User = { id: string; name: string }

export default function UserCard() {
  const { data: user, isLoading, isError } = useQuery<User>({
    queryKey: ['user'],
    queryFn: async () => {
      const res = await fetch('/api/users')
      if (!res.ok) throw new Error('Request failed')
      return res.json()
    }
  })

  if (isLoading) return <p>Loading…</p>
  if (isError) return <p role="alert">Failed to load user</p>
  return <p aria-label="user-name">{user?.name}</p>
}
```

Integration tests:

```tsx
// src/app/_components/UserCard.test.tsx
import { screen, waitFor } from '@testing-library/react'
import { rest } from 'msw'
import { server } from '../../../test/setup'
import { renderWithQuery } from '../../../test/test-utils'
import UserCard from './UserCard'

describe('UserCard', () => {
  it('renders user name from API', async () => {
    renderWithQuery(<UserCard />)
    expect(screen.getByText(/Loading/i)).toBeInTheDocument()
    await waitFor(() =>
      expect(screen.getByLabelText('user-name')).toHaveTextContent('Jane Doe')
    )
  })

  it('handles API error', async () => {
    server.use(rest.get('/api/users', (_req, res, ctx) => res(ctx.status(500))))
    renderWithQuery(<UserCard />)
    await waitFor(() =>
      expect(screen.getByRole('alert')).toHaveTextContent('Failed to load user')
    )
  })
})
```

API route (for completeness) + a minimal test:

```ts
// src/app/api/users/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ id: 'u1', name: 'Jane Doe' })
}
```

```ts
// src/app/api/users/route.test.ts
import { describe, it, expect } from 'vitest'
import { GET } from './route'

describe('GET /api/users', () => {
  it('returns a user json', async () => {
    const res = await GET()
    expect(res.headers.get('content-type')).toMatch(/application\/json/)
    const json = await res.json()
    expect(json).toEqual({ id: 'u1', name: 'Jane Doe' })
  })
})
```

Explanation: Integration tests verify component behavior with realistic network interactions, benefiting from TanStack Query’s loading/error states and caching.

## D) End-to-End (Playwright)

Config:

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  retries: 0,
  use: { baseURL: 'http://localhost:3000', trace: 'on-first-retry' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'pnpm next dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI
  }
})
```

Test:

```ts
// e2e/home.spec.ts
import { test, expect } from '@playwright/test'

test('home renders and navigates to dashboard', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/MyApp/i)
  await page.getByRole('link', { name: /dashboard/i }).click()
  await expect(page).toHaveURL(/.*dashboard/)
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible()
})
```

Explanation: Keep E2E slim—protect only critical paths with resilient, role/text-based selectors.

## E) Server Actions with TanStack Query (mutation + invalidation)

Pure business logic:

```ts
// src/server/user-service.ts
export async function renameUser(
  db: { user: { update: (a: unknown) => Promise<void> } },
  id: string,
  name: string
) {
  if (!name.trim()) throw new Error('Name required')
  await db.user.update({ where: { id }, data: { name } })
}
```

Server Action (server-side cache revalidation):

```ts
// src/app/dashboard/actions.ts
'use server'
import { revalidateTag } from 'next/cache'
import { renameUser } from '@/server/user-service'

export async function updateUserName(id: string, name: string) {
  // In real code, inject a real DB service here
  await renameUser({ user: { update: async () => {} } }, id, name)
  revalidateTag('user') // Server-side revalidation for RSC and fetch tag caches
}
```

Client Component using TanStack Query `useMutation` + client-side invalidation:

```tsx
// src/app/_components/UpdateUserButton.tsx
'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateUserName } from '@/app/dashboard/actions'

export default function UpdateUserButton({ id }: { id: string }) {
  const queryClient = useQueryClient()

  const { mutate, isPending, isError } = useMutation({
    mutationFn: async (name: string) => {
      await updateUserName(id, name) // Calls Server Action
    },
    onSuccess: async () => {
      // Client-side invalidation for TanStack Query caches
      await queryClient.invalidateQueries({ queryKey: ['user', id] })
      // Optionally broader: await queryClient.invalidateQueries({ queryKey: ['user'] })
    }
  })

  return (
    <div>
      <button
        onClick={() => mutate('New Name')}
        disabled={isPending}
        aria-busy={isPending}
      >
        {isPending ? 'Updating…' : 'Update Name'}
      </button>
      {isError && <p role="alert">Update failed</p>}
    </div>
  )
}
```

Unit test for pure logic:

```ts
// src/server/user-service.test.ts
import { describe, it, expect, vi } from 'vitest'
import { renameUser } from './user-service'

describe('renameUser', () => {
  it('throws on empty name', async () => {
    await expect(renameUser({ user: { update: vi.fn() } }, 'u1', ''))
      .rejects.toThrow('Name required')
  })

  it('updates user name', async () => {
    const update = vi.fn().mockResolvedValue(undefined)
    await renameUser({ user: { update } }, 'u1', 'Jane')
    expect(update).toHaveBeenCalledWith({ where: { id: 'u1' }, data: { name: 'Jane' } })
  })
})
```

Explanation: Mutations flow through a Server Action for security and server-side revalidation; the Client Component wraps it in **TanStack Query** for status, errors, and client cache invalidation.

## Suggested Folder Layout

```
src/
  app/
    api/users/route.ts
    _components/
      UserCard.tsx
      UpdateUserButton.tsx
  lib/
    calc.ts
    schemas.ts
  server/
    user-service.ts
test/
  setup.ts
  test-handlers.ts
  test-utils.tsx
e2e/
  home.spec.ts
vitest.config.ts
playwright.config.ts
```

Explanation: Co-locate tests with code when practical; share network handlers and render helpers under `/test`. Keep boundaries clear: unit (lib/server), integration (components/routes), E2E (e2e/).

## Practical Tips

* Prefer semantic queries (`getByRole`, `getByLabelText`) for resilient tests.
* Use `initialData` in TanStack Query when hydrating server-fetched data to avoid waterfalls.
* Avoid arbitrary timeouts; rely on React Query states and Playwright auto-waits.
* Keep E2E slim; run lint + typecheck + unit/integration on every push; run E2E on main/pre-release.
