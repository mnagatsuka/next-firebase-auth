# 8. Navigation & Linking

This section defines the rules and best practices for navigation in Next.js projects using the **App Router** and **React Server Components (RSC)**.

Our goals are:
- Use `next/link` for internal navigation
- Leverage prefetching for performance
- Ensure links are accessible and SEO-friendly
- Use typed routes where applicable to avoid broken links


## 1. `next/link` Best Practices

- Always use [`next/link`](https://nextjs.org/docs/app/api-reference/components/link) for **internal navigation**.
- For external links, use a standard `<a>` tag with `target="_blank"` and `rel="noopener noreferrer"` when opening in a new tab.
- Avoid using plain `<a>` tags for internal links, as they cause full page reloads.

**Example (Internal Link):**

```tsx
import Link from 'next/link'

export default function HomeLink() {
  return <Link href="/dashboard">Go to Dashboard</Link>
}
````

**Example (External Link):**

```tsx
export default function ExternalLink() {
  return (
    <a href="https://example.com" target="_blank" rel="noopener noreferrer">
      Visit Example
    </a>
  )
}
```


## 2. Prefetching Behavior

* By default, `next/link` prefetches pages **in the viewport** during idle time.
* Use `prefetch={false}` if prefetching is unnecessary (e.g., rarely used admin routes).

**Example:**

```tsx
<Link href="/admin" prefetch={false}>Admin Panel</Link>
```

**Rules:**

* Keep prefetch enabled for high-traffic pages.
* Disable prefetch for large pages or rarely accessed routes to reduce bandwidth.


## 3. Navigation in Client Components

Use `useRouter()` from `next/navigation` for **programmatic navigation** inside Client Components.

**Example:**

```tsx
'use client'

import { useRouter } from 'next/navigation'

export default function GoBackButton() {
  const router = useRouter()
  return <button onClick={() => router.back()}>Go Back</button>
}
```

**Rules:**

* Only use `useRouter()` in Client Components.
* Prefer `router.push()` or `router.replace()` for controlled navigation.


## 4. Typed Routes (Optional / Experimental)

* Typed routes prevent typos and broken links at compile time.
* This requires a type definition for available routes and a helper for navigation.

**Example:**

```ts
// routes.ts
export const routes = {
  home: '/',
  dashboard: '/dashboard',
  settings: '/dashboard/settings'
} as const

export type AppRoute = (typeof routes)[keyof typeof routes]
```

```tsx
import Link from 'next/link'
import { routes } from '@/routes'

export default function Nav() {
  return <Link href={routes.dashboard}>Dashboard</Link>
}
```


## 5. Accessibility Considerations

* All links must have **descriptive text** that makes sense out of context.
* Avoid using "Click here" or similar vague text.
* Ensure that interactive elements used for navigation are focusable and keyboard accessible.

**Example:**

```tsx
<Link href="/profile">View Your Profile</Link>
```


By following these rules, we ensure **fast, accessible, and maintainable** navigation in our Next.js applications.
