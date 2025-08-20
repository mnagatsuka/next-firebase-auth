import { type NextRequest, NextResponse } from "next/server";
import { AUTH_CONSTANTS, ROUTES } from "./lib/constants";

// Routes that require authentication
const protectedRoutes = [ROUTES.CREATE_POST, ROUTES.PROFILE];

export async function middleware(request: NextRequest) {
	const { pathname } = request.nextUrl;

	// Check if the route requires protection
	const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route));

	// Get session cookie
	const sessionCookie = request.cookies.get(AUTH_CONSTANTS.COOKIE_NAME);

	// If no session cookie exists and route is protected
	if (!sessionCookie && isProtectedRoute) {
		// Redirect to dedicated anonymous login page (not API route)
		const anonymousLoginUrl = new URL(ROUTES.AUTH_ANONYMOUS, request.url);
		anonymousLoginUrl.searchParams.set("redirect", pathname);
		return NextResponse.redirect(anonymousLoginUrl);
	}

	// Session verification is handled in API routes and page components
	// since Edge Runtime middleware can't use Node.js APIs (Firebase Admin SDK)

	// Continue with the request
	return NextResponse.next();
}

// Configure which routes the middleware should run on
export const config = {
	matcher: [
		/*
		 * Match all request paths except for the ones starting with:
		 * - api/auth (authentication API routes)
		 * - _next/static (static files)
		 * - _next/image (image optimization files)
		 * - favicon.ico (favicon file)
		 * - public folder files
		 */
		"/((?!login|signup|auth|api|_next/static|_next/image|favicon.ico|assets).*)",
	],
};
