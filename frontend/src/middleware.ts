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
  const vercelEnv = process.env.VERCEL_ENV as string | undefined // 'development' | 'preview' | 'production'
  const isProd = vercelEnv === 'production'
  const isPreview = vercelEnv === 'preview'
  const applyCsp = isProd || isPreview
  const publicApiUrl = process.env.NEXT_PUBLIC_API_BASE_URL
  const serverApiUrl = process.env.API_BASE_URL
  const publicWebSocketUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL

  const toWs = (url: string) =>
    url.startsWith('https:') ? url.replace('https:', 'wss:') : url.replace('http:', 'ws:')

  const connectSources: string[] = ["'self'"]

  if (publicApiUrl) connectSources.push(publicApiUrl, toWs(publicApiUrl))
  if (serverApiUrl) connectSources.push(serverApiUrl, toWs(serverApiUrl))
  if (publicWebSocketUrl) connectSources.push(publicWebSocketUrl)

  // Firebase Auth endpoints (anonymous login, token refresh)
  connectSources.push(
    'https://identitytoolkit.googleapis.com',
    'https://securetoken.googleapis.com'
  )
  if (!applyCsp && !publicApiUrl && !serverApiUrl) connectSources.push('http://localhost:8000', 'ws://localhost:8000')

  // Allow frames (e.g., Vercel Live) only outside production
  const frameSources: string[] = ["'self'"]
  if (!isProd) frameSources.push('https://vercel.live')

  // Allow Vercel Live websocket endpoints only outside production
  if (!isProd) connectSources.push('https://vercel.live', 'wss://vercel.live')

  // Build script-src allowing nonce and same-origin. In non-prod, allow Vercel Live.
  const scriptSources: string[] = ["'self'", `'nonce-${nonce}'`]
  if (!isProd) {
    scriptSources.push('https://vercel.live')
  } else {
    // In production, prefer strict-dynamic when all runtime scripts are nonce'd
    scriptSources.push(`'strict-dynamic'`)
  }

  const csp = [
    "default-src 'self'",
    `script-src ${scriptSources.join(' ')}`,
    `connect-src ${connectSources.join(' ')}`,
    `frame-src ${frameSources.join(' ')}`,
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

  // Apply CSP in production and staging (APP_ENV). Skip in local dev to avoid HMR conflicts.
  if (applyCsp) {
    response.headers.set('Content-Security-Policy', csp)
  }

  // Apply a restrictive Permissions-Policy (deny powerful APIs by default)
  // Keep minimal set; enable features explicitly when needed in the future
  const permissionsPolicy = [
    'camera=()',
    'microphone=()',
    'geolocation=()',
    'autoplay=()',
    'payment=()',
    'publickey-credentials-get=()'
  ].join(', ')
  response.headers.set('Permissions-Policy', permissionsPolicy)

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
