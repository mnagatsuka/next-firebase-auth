import { NextResponse } from "next/server";
import { verifySessionCookie } from "@/lib/auth/session";
const AUTH_COOKIE_NAME = "__session";

export const runtime = "nodejs";

export async function GET() {
	try {
		// Verify session cookie and get user
		const user = await verifySessionCookie();

    	if (!user) {
        	const res = NextResponse.json(
            	{ success: false, message: "No valid session found" },
            	{ status: 401 },
        	);
        	try { res.cookies.delete(AUTH_COOKIE_NAME); } catch {}
        	return res;
    	}

		// Compute fields from decoded claims
		const isAnonymous = user?.firebase?.sign_in_provider === "anonymous";
		const emailVerified = user?.email_verified === true;

		const reserved = new Set([
			"iss",
			"aud",
			"auth_time",
			"user_id",
			"sub",
			"iat",
			"exp",
			"email",
			"email_verified",
			"firebase",
			"uid",
		]);
		const customClaims = Object.fromEntries(
			Object.entries(user || {}).filter(([k]) => !reserved.has(k)),
		);

		const userInfo = {
			uid: user.uid || user.user_id,
			email: user.email || null,
			emailVerified,
			isAnonymous,
			customClaims,
		};

		return NextResponse.json(
			{
				success: true,
				user: userInfo,
				message: "Session valid",
			},
			{ status: 200 },
		);
	} catch (error) {
		console.error("Session verification error:", error);

		return NextResponse.json(
			{ success: false, message: "Session verification failed" },
			{ status: 500 },
		);
	}
}
