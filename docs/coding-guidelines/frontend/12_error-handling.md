# 12. Error & State Handling

This section defines the rules and best practices for handling errors and loading states in Next.js projects using the **App Router** and **React Server Components (RSC)**.

Our goals are:
- Provide clear and consistent error pages
- Handle loading states gracefully
- Use built-in Next.js conventions for `error.tsx`, `not-found.tsx`, and `loading.tsx`
- Ensure users can recover from errors whenever possible


## 1. `error.tsx` — Route-Level Error UI

- Placed inside a route folder to handle errors **within that route**.
- Automatically rendered when a Server Component throws an error during rendering, data fetching, or streaming.
- Can be a **Client Component** to handle user interaction (e.g., retry button).

**Example:**

```tsx
'use client'

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="p-6 text-center">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="text-gray-600 mt-2">{error.message}</p>
      <button
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
        onClick={() => reset()}
      >
        Try Again
      </button>
    </div>
  )
}
````

**Rules:**

* Always provide a way to **retry** or navigate away.
* Keep messages user-friendly; avoid exposing sensitive error details in production.


## 2. `not-found.tsx` — Handling 404 States

* Rendered when a page or resource is not found.
* Can be triggered manually with the `notFound()` helper from `next/navigation`.

**Example:**

```tsx
import { notFound } from 'next/navigation'

export default function Page({ params }) {
  if (!isValidResource(params.id)) {
    notFound()
  }
  return <div>Valid Resource</div>
}
```

**Example `not-found.tsx`:**

```tsx
export default function NotFound() {
  return (
    <div className="p-6 text-center">
      <h1 className="text-2xl font-bold">Page Not Found</h1>
      <p className="text-gray-600 mt-2">The page you are looking for does not exist.</p>
    </div>
  )
}
```


## 3. `loading.tsx` — Loading States

* Rendered while a route or component is loading (during streaming or data fetching).
* Should be lightweight and visually consistent across the app.

**Example:**

```tsx
export default function Loading() {
  return (
    <div className="flex justify-center items-center h-full">
      <p className="text-gray-500">Loading...</p>
    </div>
  )
}
```


## 4. Using `<Suspense>` for Component-Level Loading

* For partial loading states, wrap slow components in `<Suspense>` with a fallback.

**Example:**

```tsx
import { Suspense } from 'react'
import Comments from './Comments'
import CommentsLoading from './CommentsLoading'

export default function Page() {
  return (
    <div>
      <h1>Post</h1>
      <Suspense fallback={<CommentsLoading />}>
        <Comments />
      </Suspense>
    </div>
  )
}
```


## 5. Redirects & `notFound()` Helper

* Use `redirect('/path')` from `next/navigation` for immediate redirects.
* Use `notFound()` to trigger the nearest `not-found.tsx`.

**Example:**

```ts
import { redirect } from 'next/navigation'

export default function Page() {
  const user = getCurrentUser()
  if (!user) redirect('/login')
  return <div>Dashboard</div>
}
```


## 6. General Guidelines

* Keep error and loading components **minimal and reusable** where possible.
* Test error boundaries and loading states during development.
* For API routes, return meaningful HTTP status codes and error messages.


By following these rules, we ensure our applications provide **clear feedback**, **smooth loading experiences**, and **recoverable error handling** for end users.
