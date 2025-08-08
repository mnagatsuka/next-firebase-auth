# 5. Data Fetching & Caching

This section defines the rules and best practices for **data fetching** and **caching** in Next.js projects using the **App Router** and **React Server Components (RSC)**.

Our goals are:
- Prefer **server-side data fetching** to reduce client bundle size
- Use caching effectively to improve performance
- Avoid unnecessary `no-store` to retain cache benefits
- Co-locate fetch logic with the components that consume the data


## 1. Server-Side Data Fetching

Server Components allow direct use of `async/await` for data fetching without shipping fetch logic to the client.

**Rules:**
- Fetch data on the **server** whenever possible.
- Use the built-in `fetch()` API or data layer functions inside Server Components.
- Keep fetch logic close to the consuming component unless it’s reused across multiple routes.

**Example:**

```tsx
// Server Component
export default async function UserProfile({ id }: { id: string }) {
  const user = await fetch(`${process.env.API_URL}/users/${id}`).then(res => res.json())
  return <div>{user.name}</div>
}
````


## 2. Caching Strategies

We use Next.js’ built-in caching to balance **freshness** and **performance**.

### a. Time-based Caching

* Use `fetch()` with the `next.revalidate` option to control cache duration.

```ts
await fetch(url, { next: { revalidate: 60 } }) // Cache for 60 seconds
```

### b. Tag-based Caching

* Assign **tags** to cache entries for targeted revalidation.

```ts
await fetch(url, { next: { tags: ['user'] } })
```

* Revalidate by tag:

```ts
import { revalidateTag } from 'next/cache'
revalidateTag('user')
```

### c. Path-based Caching

* Cache is automatically keyed by request URL.
* Useful for static or semi-static data.


## 3. Avoiding Unnecessary `no-store`

`cache: 'no-store'` disables caching entirely — use it **only** when:

* Data changes on **every request**
* Data is highly dynamic and must always be fresh
* Security or privacy requirements demand it

**Anti-pattern:**

```ts
// ❌ Avoid using no-store by default
await fetch(url, { cache: 'no-store' })
```

**Better:**

```ts
// ✅ Use revalidate for balanced freshness and performance
await fetch(url, { next: { revalidate: 30 } })
```


## 4. Co-location of Fetch Logic

* Keep data fetching code **in the same folder** as the component or route when it’s route-specific.
* Move fetch logic to `/src/lib/` or `/src/api/` only if shared by multiple routes.

Example:

```
src/app/dashboard/
  page.tsx          # Server Component
  fetch-data.ts     # Route-specific fetch logic
```


## 5. Combining with TanStack Query (Client Side)

For client-side interactivity or background updates, use **TanStack Query** in Client Components.

**Rules:**

* Fetch initial data on the server and pass it as `initialData` to TanStack Query.
* Use query keys consistently for cache invalidation.

**Example:**

```tsx
'use client'

import { useQuery } from '@tanstack/react-query'

function UserProfileClient({ id, initialData }) {
  const { data } = useQuery({
    queryKey: ['user', id],
    queryFn: () => fetch(`/api/users?id=${id}`).then(res => res.json()),
    initialData
  })
  return <div>{data.name}</div>
}
```


## 6. Revalidation After Mutations

After a data mutation, trigger revalidation:

* Use `revalidateTag` for tag-based caches
* Use `revalidatePath` for path-based caches

**Example (Server Action):**

```ts
'use server'

import { revalidateTag } from 'next/cache'

export async function updateUser(id: string, data: any) {
  await fetch(`${process.env.API_URL}/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
  revalidateTag('user')
}
```


By following these rules, we ensure **fast load times**, **reliable caching**, and **predictable data freshness** across our Next.js applications.
