# Security Headers Guideline

Target: **Next.js (App Router, Vercel)**
Purpose: Protect end users by attaching appropriate security headers to responses.

**Note**

* The security headers covered here are **interpreted by browsers**.
* **They are not required for API responses (JSON, etc.)**, as browsers do not evaluate them.
* Therefore, these headers only need to be configured on the **Next.js frontend**.


## Target Headers and Recommended Values

| Header                        | Purpose                                 | Applies to                               | Recommended Value                     |
| ----------------------------- | --------------------------------------- | ---------------------------------------- | ------------------------------------- |
| **Strict-Transport-Security** | Enforce HTTPS                           | ✅ Next.js (production only)              | `max-age=31536000; includeSubDomains` |
| **X-Content-Type-Options**    | Prevent MIME sniffing                   | ✅ Next.js                                | `nosniff`                             |
| **X-Frame-Options**           | Prevent clickjacking (iframe embedding) | ✅ Next.js (or use CSP `frame-ancestors`) | `DENY`                                |
| **Referrer-Policy**           | Control referrer information            | ✅ Next.js                                | `strict-origin-when-cross-origin`     |
| **Content-Security-Policy**   | Restrict script/connection sources      | ✅ Next.js (nonce pattern recommended)    | See sample below                      |


## Next.js Implementation Examples

### Common Headers (excluding CSP)

```ts
// next.config.ts
// Prefer explicit app environment over NODE_ENV for security toggles
const isProd = process.env.APP_ENV === 'production'

const securityHeaders = [
  ...(isProd
    ? [{ key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains' }]
    : []),
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
]

export default {
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }]
  },
}
```

### CSP (nonce pattern)

```ts
// middleware.ts
import { NextRequest, NextResponse } from 'next/server'
import crypto from 'crypto'

export function middleware(req: NextRequest) {
  const nonce = crypto.randomUUID()

  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'`,
    "connect-src 'self' https://api.example.com",
    "img-src 'self' data:",
    "style-src 'self' 'unsafe-inline'", // practical with Tailwind
    "font-src 'self'",
    "frame-ancestors 'none'",
    "object-src 'none'",
    "base-uri 'self'",
  ].join('; ')

  const res = NextResponse.next()
  res.headers.set('Content-Security-Policy', csp)
  return res
}
```


## Rationale for Recommended Values

* **HSTS**: Enforce HTTPS in production. Use `preload` only if all subdomains are HTTPS.
* **nosniff**: Always include to prevent MIME type sniffing.
* **X-Frame-Options / frame-ancestors**: Protect against clickjacking. Prefer `DENY`. If embedding is required, use CSP `frame-ancestors`.
* **Referrer-Policy**: Balance privacy and usability. `strict-origin-when-cross-origin` is the standard default.
* **CSP**: Use the Next.js nonce pattern. Whitelist only the external resources you truly need.


## Verification

```bash
# Frontend
curl -sI https://your-frontend.vercel.app | grep -iE 'strict|nosniff|frame|referrer|csp'
```

Automated testing with Playwright or similar tools is also recommended.


## Minimal Required Set

* **Strict-Transport-Security** (production only)
* **X-Content-Type-Options: nosniff**
* **Referrer-Policy: strict-origin-when-cross-origin**
* **X-Frame-Options: DENY** (or CSP `frame-ancestors`)
* **Content-Security-Policy** (nonce pattern)
