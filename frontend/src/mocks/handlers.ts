import { HttpResponse, http } from "msw";
import { getBlogPostAPIMock } from "@/lib/api/generated/client.msw";

// Use all generated handlers - they already include the correct mock data
const apiHandlers = getBlogPostAPIMock();

// Firebase Auth API mocks
const authHandlers = [
	// Login endpoint
	http.post("/api/auth/login", async ({ request }) => {
		const body = (await request.json()) as { idToken: string };
		if (!body.idToken) {
			return HttpResponse.json(
				{
					success: false,
					message: "ID token is required",
				},
				{ status: 400 },
			);
		}

		return HttpResponse.json({
			success: true,
			message: "Login successful",
		});
	}),

	// Logout endpoint
	http.post("/api/auth/logout", () => {
		return HttpResponse.json({
			success: true,
			message: "Logout successful",
		});
	}),

	// Session verification endpoint
	http.get("/api/auth/session", () => {
		return HttpResponse.json({
			success: true,
			user: {
				uid: "mock-user-id",
				email: "test@example.com",
				emailVerified: true,
				isAnonymous: false,
				customClaims: {},
			},
			message: "Session valid",
		});
	}),

	// Anonymous login redirect
	http.get("/api/auth/anonymous", ({ request }) => {
		const url = new URL(request.url);
		const redirect = url.searchParams.get("redirect") || "/";
		const authUrl = new URL("/", request.url);
		authUrl.searchParams.set("auth", "1");
		authUrl.searchParams.set("anonymous", "true");
		authUrl.searchParams.set("redirect", redirect);

		return HttpResponse.redirect(authUrl.toString());
	}),
];

// Additional custom error handlers for testing
const errorHandlers = [
	http.get("/posts/error-500", () => {
		return HttpResponse.json(
			{
				status: "error",
				error: {
					code: "INTERNAL_SERVER_ERROR",
					message: "Something went wrong",
				},
			},
			{ status: 500 },
		);
	}),

	http.post("/posts/unauthorized", () => {
		return HttpResponse.json(
			{
				status: "error",
				error: {
					code: "UNAUTHORIZED",
					message: "Authentication required",
				},
			},
			{ status: 401 },
		);
	}),
];

export const handlers = [...apiHandlers, ...authHandlers, ...errorHandlers];
