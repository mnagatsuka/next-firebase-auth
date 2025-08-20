import { type NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
	// This API route is deprecated - redirect to the dedicated anonymous login page
	const { searchParams } = new URL(request.url);
	const redirectTo = searchParams.get("redirect") || "/";

	const anonymousPageUrl = new URL("/auth/anonymous", request.url);
	anonymousPageUrl.searchParams.set("redirect", redirectTo);

	return NextResponse.redirect(anonymousPageUrl);
}
