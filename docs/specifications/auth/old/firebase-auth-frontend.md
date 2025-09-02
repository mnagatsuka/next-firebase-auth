# Next.js (App Router) Auth Guideline: Cookies for SSR, ID Tokens for Cross-Site API

This guideline aligns with your plan:

* Use a **Firebase session cookie** between the browser ⇄ Next.js app (for SSR).
* Use **Bearer ID tokens** from the client to your **cross-site backend** (e.g., `http://localhost:8000`)—no cookies to that backend.

## 1) Architecture Overview

* Browser ⇄ Next.js (same origin on Vercel):
  Use an HttpOnly `session` cookie issued by your Next.js API route (`/api/auth/login`) from the client’s Firebase ID token.
* Browser ⇄ Backend API (cross origin, e.g., `:8000`):
  Use `Authorization: Bearer <idToken>` sent from the client. Backend verifies with Firebase Admin SDK.
* SSR in Next.js:
  Read/verify the `session` cookie on the server to know the user.
  Do not try to “recover” an ID token from a session cookie (you can’t). If SSR needs data that currently requires an ID token at the backend, either:

  * A) Move that fetch to the client (keep Bearer), or
  * B) Add a same-origin Next.js server proxy endpoint that verifies the session cookie and calls the backend using a server-to-server trust (e.g., service account, shared secret, or a backend-accepted header like `X-UID`).

## 2) Environment Setup

### Dev (Auth Emulator)

* Client: connect emulator before any auth calls.
* Server (Next.js): set `FIREBASE_AUTH_EMULATOR_HOST=127.0.0.1:9099`. Initialize Admin with `{ projectId }` only (no private key).
* Backend API: set the same env var and verify tokens with Admin SDK (emulator tokens show `"alg":"none"`—expected in dev).

### Prod

* Remove `FIREBASE_AUTH_EMULATOR_HOST`.
* Initialize Admin SDK with real credentials:

  * `cert({ projectId, clientEmail, privateKey.replace(/\\n/g, '\n') })`
  * Run on **Node runtime** only (`export const runtime = 'nodejs'`).
* Require **HTTPS** end-to-end; ID tokens will be **RS256** and verified automatically.

## 3) Cookie: issuance and attributes (browser ⇄ Next.js only)

Your `/api/auth/login` route should:

1. Accept client ID token (from `signIn...()`).
2. Create a Firebase **session cookie** via Admin SDK.
3. Set it with the right attributes.

Config

- `SESSION_COOKIE_MAX_AGE` (seconds): optional server-only env to control the session cookie lifetime. Default is `1209600` (14 days). Example: `SESSION_COOKIE_MAX_AGE=86400` for 1 day.

Dev (HTTP `http://localhost:3000`)

* `HttpOnly; Path=/; SameSite=Lax; Secure=false; Max-Age=1209600` (14 days)
* Reason: `Secure=true` cookies are not sent over plain HTTP.

Prod (HTTPS)

* `HttpOnly; Path=/; SameSite=Lax; Secure=true; Max-Age=<SESSION_COOKIE_MAX_AGE|1209600>`
* Only use `SameSite=None; Secure=true` if you truly need the cookie across different sites. You don’t—your cookie is only for SSR on the Next.js origin.

Note

* Cookie flags appear only on the **response** `Set-Cookie`; they don’t show in the **request** `Cookie:` header. That’s normal.

## 4) Client: getting and sending the ID token (Bearer)

Client components (or utilities called from them):

```ts
import { getAuth } from 'firebase/auth'

export async function getBearer() {
  const auth = getAuth()
  const token = await auth.currentUser?.getIdToken()
  return token
}

// Example fetch to cross-site API (8000)
const token = await getBearer()
const res = await fetch('http://localhost:8000/posts/123/comments', {
  headers: { Authorization: `Bearer ${token}` }
})
```

On 401/403 from the API, you can attempt a forced refresh:

```ts
const token = await auth.currentUser?.getIdToken(true) // force refresh
```

## 5) Backend API: verifying the Bearer

FastAPI/Express/etc. should:

* Read `Authorization: Bearer <token>`.
* Verify with Admin SDK:

```ts
const decoded = await adminAuth.verifyIdToken(token /* , {checkRevoked: true} in sensitive flows */)
```

* Dev: ensure `FIREBASE_AUTH_EMULATOR_HOST` is set so “alg\:none” tokens verify.
* Prod: don’t set that env; use real credentials.

CORS for Bearer-only

* Allow your Next.js origin (e.g., `http://localhost:3000`).
* Allow `Authorization` header.
* `credentials` not required (no cookies cross-site).

## 6) SSR in Next.js: verify the session cookie

Use the session cookie to identify the user for server rendering:

```ts
// app/(protected)/page.tsx (Server Component)
import { cookies } from 'next/headers'
import { getAdminAuth } from '@/lib/firebase/admin' // Node runtime

export default async function Page() {
  const session = cookies().get('session')?.value
  if (!session) /* redirect to /login or anonymous flow */

  const adminAuth = await getAdminAuth()
  const decoded = await adminAuth.verifySessionCookie(session, true) // checkRevoked in prod
  // Use decoded.uid / claims to render SSR content
  return <div>Hello {decoded.uid}</div>
}
```

If SSR must call the backend that currently requires a Bearer ID token:

* Prefer moving that fetch to the client after hydration (keeps your Bearer pattern simple), or
* Add a Next.js server proxy that verifies the session cookie and calls the backend with **server-to-server** auth the backend accepts (not an ID token derived from the session cookie, which isn’t possible).

## 7) Login and logout handlers (cookie lifecycle)

Issue cookie:

```ts
// app/api/auth/login/route.ts
export const runtime = 'nodejs'
import { NextRequest, NextResponse } from 'next/server'
import { getAdminAuth } from '@/lib/firebase/admin'

export async function POST(req: NextRequest) {
  const { idToken } = await req.json()
  const adminAuth = await getAdminAuth()
  const expiresIn = 14 * 24 * 60 * 60 * 1000

  const session = await adminAuth.createSessionCookie(idToken, { expiresIn })
  const isProd = !!process.env.VERCEL

  const res = NextResponse.json({ ok: true })
  res.cookies.set({
    name: 'session',
    value: session,
    httpOnly: true,
    path: '/',
    sameSite: 'lax',
    secure: isProd, // dev=false (HTTP), prod=true (HTTPS)
    maxAge: expiresIn / 1000
  })
  return res
}
```

Delete cookie:

```ts
// app/api/auth/logout/route.ts
export const runtime = 'nodejs'
import { NextResponse } from 'next/server'
export async function POST() {
  const res = NextResponse.json({ ok: true })
  res.cookies.set({ name: 'session', value: '', path: '/', maxAge: 0 })
  return res
}
```

## 8) Admin SDK initialization (safe split by env)

Dev (emulator):

```ts
initializeApp({ projectId: process.env.FIREBASE_PROJECT_ID })
```

Prod:

```ts
initializeApp({
  credential: cert({
    projectId: process.env.FIREBASE_PROJECT_ID!,
    clientEmail: process.env.FIREBASE_CLIENT_EMAIL!,
    privateKey: process.env.FIREBASE_PRIVATE_KEY!.replace(/\\n/g, '\n')
  })
})
```

Always run on **Node runtime** in API routes/SSR; do not use Admin SDK in Middleware/Edge.

## 9) Vercel origin model

* Next.js pages and **API routes under the same project** deploy to the **same origin**: `https://<your-domain>/api/...`.
* If you keep a separate backend (e.g., FastAPI on another domain/port), it’s **cross-origin**; keep using Bearer with CORS.

## 10) Security and Ops checklist

* Never log full tokens in prod.
* Enforce HTTPS on prod (HSTS, no mixed content).
* Handle 401 from the backend: refresh ID token once; if still failing, sign-in again.
* Consider `verifyIdToken(token, true)` for sensitive endpoints (revocation checks).
* Rotate service account keys periodically; store secrets in server-only env vars (never `NEXT_PUBLIC_`).

## 11) Quick sanity tests

* Dev: cookie present on requests to `:3000` only; Bearer used to `:8000`; emulator tokens show `"alg":"none"`.
* Prod: cookie has `Secure=true`; ID tokens are `RS256`; backend verifies without emulator env var.
* Clearing cookie logs you out of SSR; client Bearer calls fail until you re-sign-in.

This gives you a clean, predictable split: cookie for same-origin SSR identity, Bearer for cross-origin API calls, with correct dev/prod behavior.
