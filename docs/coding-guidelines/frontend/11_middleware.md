# 11. Middleware & Edge Functions

This section defines the rules and best practices for using **middleware** and **Edge Functions** in Next.js projects with the **App Router**.

Our goals are:
- Use middleware for lightweight request handling at the edge
- Apply middleware selectively to improve performance
- Keep middleware logic simple, fast, and secure
- Leverage Edge Functions for low-latency, region-distributed processing


## 1. Use Cases for `middleware.ts`

Middleware runs **before** a request is completed and can modify the request/response.

**Common use cases:**
- Authentication and access control
- Redirects and rewrites
- Logging and analytics
- Locale detection for internationalization (i18n)
- Feature flag checks

**Example:**

```ts
// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*']
}
````


## 2. Performance Considerations

* Middleware runs **on every matching request** — keep logic minimal to reduce latency.
* Avoid heavy computations or large data fetches in middleware.
* For complex server-side logic, prefer **Server Actions** or API routes instead.


## 3. Applying Middleware Selectively

* Use the `matcher` config to apply middleware only to relevant routes.
* Avoid running middleware globally unless absolutely necessary.

**Example:**

```ts
export const config = {
  matcher: ['/admin/:path*', '/account/:path*']
}
```


## 4. Edge Functions

* Use Edge Functions for **low-latency** server-side logic distributed across regions.
* Ideal for personalization, A/B testing, and real-time content modifications.
* Avoid database queries that require a persistent TCP connection — prefer edge-compatible services (e.g., Vercel KV, Upstash Redis).

**Example (Edge Runtime API Route):**

```ts
// src/app/api/hello/route.ts
export const runtime = 'edge'

export async function GET() {
  return new Response(JSON.stringify({ message: 'Hello from the Edge!' }), {
    headers: { 'content-type': 'application/json' }
  })
}
```


## 5. Security Guidelines

* Do not expose sensitive logic in middleware — it runs before route handlers but still executes in a public environment.
* Sanitize all inputs and avoid trusting request headers without validation.
* Use HTTPS for all requests and avoid insecure redirects.


By following these rules, we ensure that middleware and Edge Functions are **fast, secure, and applied only where necessary**, improving performance and maintainability in our Next.js applications.
