import { NextRequest, NextResponse } from 'next/server'

// Constants
const AUTH_COOKIE_NAME = '__session' // Firebase Auth session cookie
const ROUTES = {
  CREATE_POST: '/create-post',
  MY_POSTS: '/my/posts',
  HOME: '/',
} as const

// Routes that require authenticated (non-anonymous) users only
const protectedRoutes = [ROUTES.CREATE_POST, ROUTES.MY_POSTS]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Generate nonce for CSP
  const nonce = crypto.randomUUID()

  // Pass nonce to the app via request headers (Next.js CSP guide)
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-nonce', nonce)

  // Prepare response with updated request headers
  const response = NextResponse.next({ request: { headers: requestHeaders } })

  // Build CSP connect-src with WebSocket support from env
  const env = process.env.NODE_ENV
  const isProd = env === 'production'
  const isStaging = (env as string) === 'staging'
  const applyCsp = isProd || isStaging
  const publicApiUrl = process.env.NEXT_PUBLIC_API_BASE_URL
  const serverApiUrl = process.env.API_BASE_URL

  const toWs = (url: string) =>
    url.startsWith('https:') ? url.replace('https:', 'wss:') : url.replace('http:', 'ws:')

  const connectSources: string[] = ["'self'"]

  if (publicApiUrl) connectSources.push(publicApiUrl, toWs(publicApiUrl))
  if (serverApiUrl) connectSources.push(serverApiUrl, toWs(serverApiUrl))
  if (!applyCsp && !publicApiUrl && !serverApiUrl) connectSources.push('http://localhost:8000', 'ws://localhost:8000')

  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'`,
    `connect-src ${connectSources.join(' ')}`,
    "img-src 'self' data:",
    "style-src 'self' 'unsafe-inline'",
    "font-src 'self'",
    "frame-ancestors 'none'",
    "object-src 'none'",
    "base-uri 'self'",
  ].join('; ')

  // Authentication flags for protected routes (modal-based auth)
  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route))
  if (isProtectedRoute) {
    const sessionCookie = request.cookies.get(AUTH_COOKIE_NAME)
    if (!sessionCookie) {
      response.headers.set('x-auth-required', 'true')
      response.headers.set('x-auth-reason', 'no-session')
      response.headers.set('x-redirect-path', pathname)
    } else {
      response.headers.set('x-verify-auth', 'required')
      response.headers.set('x-protected-route', 'true')
    }
  }

  // Apply CSP in production and staging (NODE_ENV=staging). Skip in local dev to avoid HMR conflicts.
  if (applyCsp) {
    response.headers.set('Content-Security-Policy', csp)
  }

  return response
}

// Configure which routes the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files) 
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - assets (public assets)
     */
    '/',
    '/((?!api|_next/static|_next/image|favicon.ico|assets).*)',
  ],
}
