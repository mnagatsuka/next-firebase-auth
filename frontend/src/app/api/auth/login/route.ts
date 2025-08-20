import { type NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { setSessionCookie } from "@/lib/auth/session";

export const runtime = "nodejs";

// Request validation schema
const loginSchema = z.object({
	idToken: z.string().min(1, "ID token is required"),
});

export async function POST(request: NextRequest) {
	try {
		const body = await request.json();

		// Validate request body
		const { idToken } = loginSchema.parse(body);

		// Set session cookie with the provided ID token
		await setSessionCookie(idToken);

		return NextResponse.json({ success: true, message: "Login successful" }, { status: 200 });
	} catch (error) {
		console.error("Login error:", error);

		if (error instanceof z.ZodError) {
			return NextResponse.json(
				{ success: false, message: "Invalid request data", errors: error.errors },
				{ status: 400 },
			);
		}

		return NextResponse.json({ success: false, message: "Login failed" }, { status: 500 });
	}
}
