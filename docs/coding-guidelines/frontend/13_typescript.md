# 13. TypeScript Rules

This section defines the rules and best practices for using **TypeScript** in our Next.js projects with the **App Router** and **React Server Components (RSC)**.

Our goals are:
- Maintain strict type safety across the entire codebase
- Avoid untyped or loosely typed code
- Improve developer experience with better auto-completion and error checking
- Keep type definitions organized and reusable


## 1. Compiler Strictness

We enforce strict compiler settings to catch potential issues early.

**Required `tsconfig.json` settings:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  }
}
````

**Rules:**

* Never disable `strict` mode.
* Avoid adding `// @ts-ignore` unless absolutely necessary, and document the reason.
* Address type errors immediately instead of bypassing them.


## 2. Explicit Types for Props and Exports

* Always type component props, function parameters, and return values.
* Avoid relying solely on type inference for exported functions and components.

**Example:**

```tsx
type UserCardProps = {
  name: string
  age: number
}

export default function UserCard({ name, age }: UserCardProps): JSX.Element {
  return (
    <div>
      <h2>{name}</h2>
      <p>{age} years old</p>
    </div>
  )
}
```


## 3. Avoiding `any`

* Do not use `any` unless absolutely necessary.
* Prefer `unknown` when the type is not yet known and require explicit narrowing before use.
* Use `zod` or similar libraries for runtime validation when dealing with external data.

**Anti-pattern:**

```ts
function processData(data: any) { /* ... */ }
```

**Better:**

```ts
function processData(data: unknown) {
  if (typeof data === 'string') {
    // handle string
  }
}
```


## 4. Advanced Compiler Options

Enable the following options for improved safety:

* **`noUncheckedIndexedAccess`** — Ensures indexing arrays/objects includes `undefined` in the type.
* **`forceConsistentCasingInFileNames`** — Avoids issues with case sensitivity across environments.
* **`isolatedModules`** — Ensures compatibility with tools like Babel and SWC.
* **`esModuleInterop`** — Improves import compatibility.


## 5. Organizing Types

**Rules:**

* Co-locate types with the files that use them if they are specific to that file.
* Place shared types in `src/types/` or a dedicated feature folder.
* Use `*.d.ts` declaration files only for ambient type definitions (e.g., global types).

**Example structure:**

```
src/
  types/
    user.ts
    api.ts
  features/
    dashboard/
      Dashboard.tsx
      types.ts
```


## 6. Utility Types

Leverage built-in TypeScript utility types for cleaner and safer code:

* `Partial<T>` — All properties optional
* `Pick<T, K>` — Select specific properties
* `Omit<T, K>` — Remove specific properties
* `Readonly<T>` — Immutable object
* `Record<K, T>` — Object type with keys of `K` and values of `T`

**Example:**

```ts
type User = { id: string; name: string; age: number }
type UserPreview = Pick<User, 'id' | 'name'>
```


## 7. Working with Next.js Types

* Use official Next.js types where applicable (`NextPage`, `Metadata`, `NextRequest`, `NextResponse`).
* When creating API routes, type both the request and response.

**Example:**

```ts
import type { NextRequest } from 'next/server'

export async function GET(req: NextRequest) {
  return new Response('Hello')
}
```


By following these rules, we maintain a **safe, consistent, and maintainable** TypeScript codebase that improves both developer experience and application reliability.
