# 6. State Management

This section defines the rules and best practices for managing **state** in Next.js projects using the **App Router** and **React Server Components (RSC)**.

Our goals are:
- Minimize client-side state where possible
- Clearly separate **server state** (fetched from APIs) and **client state** (UI state)
- Use lightweight and purpose-fit libraries
- Ensure predictable state updates and cache invalidation


## 1. When to Use Global State vs. Server State

### Server State
- Data fetched from an API or database
- Usually handled by **Server Components** or **TanStack Query** in Client Components
- Should be cached and revalidated when needed

### Client State
- UI-only state (e.g., modal visibility, active tab)
- Transient data that doesn’t need persistence across navigations
- Managed using **Zustand** or React’s built-in hooks

**Rules:**
- Prefer **Server Components** for initial data loading
- Only use Client Components when the state must be managed in the browser


## 2. Zustand for Lightweight Client State

We use **Zustand** for simple, lightweight client-side state.

**Example:**

```ts
// store/useThemeStore.ts
import { create } from 'zustand'

type ThemeState = {
  theme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark') => void
}

export const useThemeStore = create<ThemeState>(set => ({
  theme: 'light',
  setTheme: theme => set({ theme })
}))
````

```tsx
'use client'

import { useThemeStore } from '@/store/useThemeStore'

export default function ThemeToggle() {
  const { theme, setTheme } = useThemeStore()
  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      Switch to {theme === 'light' ? 'dark' : 'light'} mode
    </button>
  )
}
```

**Rules:**

* Keep store definitions small and focused
* Avoid coupling unrelated states in a single store
* Use TypeScript types to ensure predictable store shape


## 3. TanStack Query for Server State

We use **TanStack Query** for server-fetched state that requires caching, background updates, or optimistic updates.

**Example:**

```tsx
'use client'

import { useQuery } from '@tanstack/react-query'

function UserProfile({ id }) {
  const { data, isLoading } = useQuery({
    queryKey: ['user', id],
    queryFn: () => fetch(`/api/users?id=${id}`).then(res => res.json())
  })

  if (isLoading) return <div>Loading...</div>
  return <div>{data.name}</div>
}
```

**Rules:**

* Always define **stable query keys**
* Use `initialData` from server-fetched props when possible to hydrate the cache
* Invalidate queries after mutations to keep UI fresh


## 4. Combining RSC with Client State Libraries

**Pattern:**

* Fetch data in a **Server Component**
* Pass the data to a **Client Component** as props
* Initialize client-side store or query cache with that data

**Example:**

```tsx
// Server Component
import UserProfileClient from './UserProfileClient'

export default async function Page() {
  const user = await fetchUser('123')
  return <UserProfileClient initialData={user} />
}
```

```tsx
// Client Component
'use client'

import { useQuery } from '@tanstack/react-query'

export default function UserProfileClient({ initialData }) {
  const { data } = useQuery({
    queryKey: ['user', initialData.id],
    queryFn: () => fetch(`/api/users?id=${initialData.id}`).then(res => res.json()),
    initialData
  })
  return <div>{data.name}</div>
}
```


## 5. Query Key Naming & Cache Invalidation

**Rules:**

* Use array format for query keys: `['resource', id]`
* Keep keys **descriptive** but **consistent**
* Invalidate only the relevant queries after mutations

**Example:**

```ts
import { useQueryClient } from '@tanstack/react-query'

const queryClient = useQueryClient()
queryClient.invalidateQueries({ queryKey: ['user', id] })
```


By following these rules, we ensure **clear separation of concerns**, **predictable state updates**, and **efficient caching** in our Next.js applications.
