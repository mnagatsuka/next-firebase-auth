import { NextResponse } from "next/server";
import { clearSessionCookie } from "@/lib/auth/session";

export const runtime = "nodejs";

export async function POST() {
	try {
		// Clear the session cookie
		await clearSessionCookie();

		return NextResponse.json({ success: true, message: "Logout successful" }, { status: 200 });
	} catch (error) {
		console.error("Logout error:", error);

		return NextResponse.json({ success: false, message: "Logout failed" }, { status: 500 });
	}
}
