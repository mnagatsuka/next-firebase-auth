# 7. Mutations & Server Actions

This section defines the rules and best practices for using **Server Actions** in Next.js projects with the **App Router** and **React Server Components (RSC)**.

Our goals are:
- Use Server Actions for secure, server-side mutations
- Keep mutation logic close to where it’s used
- Ensure predictable cache invalidation after changes
- Validate all inputs and outputs


## 1. `"use server"` Directive Usage

- A Server Action is a function that runs **only on the server** and can be called from Client Components.
- Must include the `"use server"` directive at the **top of the function body** (not the file).
- Can be defined inline in a component file or exported from a separate server-only module.

**Example:**

```ts
'use server'

export async function updateUserName(id: string, name: string) {
  // Update in DB
  await db.user.update({ where: { id }, data: { name } })
}
````


## 2. Triggering Server Actions

### a. From a Form

Server Actions can be bound to a form’s `action` attribute.

```tsx
'use client'

import { updateUserName } from './actions'

export default function UpdateForm() {
  return (
    <form action={updateUserName}>
      <input type="hidden" name="id" value="123" />
      <input type="text" name="name" />
      <button type="submit">Update</button>
    </form>
  )
}
```

### b. From a Button Click

Wrap the Server Action in a client-side handler.

```tsx
'use client'

import { updateUserName } from './actions'

export default function UpdateButton() {
  return (
    <button onClick={() => updateUserName('123', 'New Name')}>
      Update Name
    </button>
  )
}
```


## 3. Serialization Rules for Inputs/Outputs

* Inputs and outputs must be **serializable** (no functions, DOM nodes, or circular references).
* Use `zod` or similar schema validators to ensure type safety and runtime validation.

**Example with Validation:**

```ts
'use server'

import { z } from 'zod'

const UpdateUserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1)
})

export async function updateUser(data: unknown) {
  const parsed = UpdateUserSchema.safeParse(data)
  if (!parsed.success) throw new Error('Invalid input')

  const { id, name } = parsed.data
  await db.user.update({ where: { id }, data: { name } })
}
```


## 4. Cache Invalidation After Mutations

* Always invalidate or revalidate caches after a mutation to ensure the UI reflects the latest data.
* Use:

  * `revalidateTag('tagName')` for tag-based caches
  * `revalidatePath('/path')` for path-based caches

**Example:**

```ts
'use server'

import { revalidateTag } from 'next/cache'

export async function updateUserName(id: string, name: string) {
  await db.user.update({ where: { id }, data: { name } })
  revalidateTag('user')
}
```


## 5. Co-location of Server Actions

* Place Server Actions in the **same folder** as the component or route when they are used only in one place.
* Move to `/src/server/actions/` or a feature-specific folder if shared across multiple routes.

Example:

```
src/app/dashboard/
  page.tsx
  actions.ts         # Server Actions for dashboard page
```


By following these rules, we ensure **secure, maintainable, and predictable** server-side mutations in our Next.js applications.
