# 4. Server vs Client Components

This section defines the rules and best practices for using **Server Components** and **Client Components** in Next.js projects with the **App Router** and **React Server Components (RSC)**.

Our goals are:
- Default to Server Components for better performance and smaller client bundles
- Use Client Components only when necessary
- Clearly define boundaries between server and client code
- Enable predictable rendering and streaming behavior


## 1. Default to Server Components

**Server Components** are rendered on the server and sent to the client as serialized HTML, reducing JavaScript sent to the browser.

**Rules:**
- All components are **Server Components** by default in the `/app` directory.
- Do not add `'use client'` unless required for interactivity.
- Use Server Components for:
  - Static or server-rendered content
  - Data fetching from a database or API
  - Rendering based on environment variables or secrets
  - Heavy computations that should not run in the browser

**Example:**

```tsx
// Server Component
import { fetchUser } from '@/lib/user'

export default async function UserProfile({ id }: { id: string }) {
  const user = await fetchUser(id)
  return <div>{user.name}</div>
}
````


## 2. When to Use Client Components

**Client Components** are required when the component:

* Uses **React state** (`useState`, `useReducer`)
* Uses **React lifecycle hooks** (`useEffect`, `useLayoutEffect`)
* Handles **browser-only APIs** (e.g., `window`, `document`, `localStorage`)
* Requires **event listeners** (e.g., `onClick`, `onChange`)
* Integrates with client-only libraries (e.g., chart libraries, drag-and-drop)

**Example:**

```tsx
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  )
}
```


## 3. `'use client'` Boundary Rules

* Place `'use client'` at the **top** of the file, before imports.
* Adding `'use client'` makes the **entire file** a Client Component, including all its imports.
* Avoid wrapping large component trees in a single `'use client'` — instead, isolate only the parts that require client interactivity.
* Prefer smaller, targeted Client Components imported into Server Components.

**Anti-pattern:**

```tsx
// ❌ Avoid marking entire page as client when only a small part needs it
'use client'

import HeavyChart from '@/components/HeavyChart'

export default function Page() {
  return <HeavyChart />
}
```

**Better:**

```tsx
// page.tsx (Server Component)
import HeavyChart from '@/components/HeavyChart'

export default function Page() {
  return <HeavyChart />
}

// HeavyChart.tsx (Client Component)
'use client'
import { Chart } from 'charting-lib'

export default function HeavyChart() {
  return <Chart data={...} />
}
```


## 4. Component Streaming with `<Suspense>`

We use `<Suspense>` to stream parts of a page while other content is still loading.

**Rules:**

* Use `<Suspense>` to wrap components that fetch data or perform slow operations.
* Provide meaningful fallbacks for loading states.
* Place `<Suspense>` boundaries **inside** Server Components where possible.

**Example:**

```tsx
import { Suspense } from 'react'
import UserProfile from './UserProfile'
import LoadingProfile from './LoadingProfile'

export default function Page() {
  return (
    <Suspense fallback={<LoadingProfile />}>
      <UserProfile id="123" />
    </Suspense>
  )
}
```


## 5. Mixing Server and Client Components

**Best practice:**

* Keep Server Components at the top of the tree
* Pass data from Server Components down into Client Components via props
* Avoid passing functions from Client Components into Server Components

**Example:**

```tsx
// Server Component
import Counter from './Counter'

export default async function Page() {
  const user = await fetchUser('123')
  return (
    <div>
      <h1>{user.name}</h1>
      <Counter initialValue={user.likes} />
    </div>
  )
}
```


By following these rules, we ensure optimal **performance**, **bundle size**, and **maintainability** while working with Next.js Server and Client Components.

