# 3. Directory Structure & Routing

This section defines the **directory structure** and **routing conventions** for Next.js projects using the **App Router** and **React Server Components (RSC)**.

Our goals are:
- Maintain a clear, predictable structure
- Encourage co-location of related files (UI, data fetching, tests)
- Follow Next.js conventions while enforcing project-specific rules


## 1. Directory Structure Best Practices

We use the `/app` directory for routing with the App Router.

Example:

```

src/
app/
layout.tsx
page.tsx
loading.tsx
error.tsx
not-found.tsx
dashboard/
layout.tsx
page.tsx
loading.tsx
error.tsx
not-found.tsx
settings/
page.tsx
components/
ui/
forms/
lib/
hooks/
styles/
tests/

````

**Rules:**
- Keep route-specific components and logic inside the corresponding folder in `/app`.
- Use **flat routes** unless nested layouts or URL segments require deeper structure.
- Co-locate UI, data fetching, and tests inside the route folder if they are route-specific.


## 2. App Router Usage

We follow the [Next.js App Router](https://nextjs.org/docs/app/building-your-application/routing) pattern:

- All routes live under `/src/app/`.
- Each route must have its own `page.tsx`.
- Nested routes are represented by nested folders.
- Shared layouts use `layout.tsx`.


## 3. File Conventions

The following files have specific purposes:

| File              | Purpose |
|-------------------|---------|
| `layout.tsx`      | Defines persistent UI for a route and its children |
| `page.tsx`        | Defines the main UI for a route |
| `loading.tsx`     | Defines a loading state while streaming or fetching data |
| `error.tsx`       | Defines an error UI for rendering errors within a route |
| `not-found.tsx`   | Defines UI for handling `notFound()` or unmatched routes |
| `route.ts`        | Defines a Route Handler (API endpoint) for a given path |

**Rules:**
- `layout.tsx` should be a **Server Component** unless explicitly requiring client-side interactivity.
- Avoid unnecessary `loading.tsx` if the page renders instantly from the server.
- `error.tsx` must gracefully handle user recovery (e.g., “Retry” button).
- `not-found.tsx` should match the overall site design and link back to main routes.


## 4. Route Handlers (`route.ts`)

- Place `route.ts` inside the relevant route folder (e.g., `src/app/api/users/route.ts`).
- Must be a **Server Component** by default.
- Prefer **typed request/response** objects using `zod` for validation.

Example:

```ts
// src/app/api/users/route.ts
import { NextResponse } from 'next/server'
import { z } from 'zod'

const ParamsSchema = z.object({
  id: z.string().uuid()
})

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  const id = searchParams.get('id')

  const parsed = ParamsSchema.safeParse({ id })
  if (!parsed.success) {
    return NextResponse.json({ error: 'Invalid ID' }, { status: 400 })
  }

  // Fetch user from DB
  const user = { id, name: 'John Doe' }
  return NextResponse.json(user)
}
````


## 5. Co-location of UI, Data Fetching, and Tests

We encourage keeping related files together:

Example:

```
src/app/dashboard/
  page.tsx
  fetch-data.ts      # Server-side data fetching
  dashboard.test.ts  # Unit/integration tests
  styles.module.css  # Route-specific styles
```

**Rules:**

* Avoid scattering route-specific logic into `lib/` unless it’s shared by multiple routes.
* Co-located files should be small and focused.


## 6. Naming Conventions

* Use **kebab-case** for folders (e.g., `user-profile/`).
* Use **PascalCase** for components (e.g., `UserProfileCard.tsx`).
* Keep filenames descriptive — avoid `index.tsx` inside `/app` routes.


## 7. Example: Nested Route Structure

Example for `/dashboard/settings`:

```
src/app/dashboard/
  layout.tsx          # Dashboard-wide layout
  page.tsx            # Dashboard index page
  settings/
    page.tsx          # Settings page
    loading.tsx       # Optional loading state
    error.tsx         # Optional error UI
```


By following these routing rules, our Next.js applications remain **predictable, scalable, and easy to navigate**, both for human developers and AI-assisted tools.
