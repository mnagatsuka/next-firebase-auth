/**
 * Safe date formatting utilities that work consistently on server and client
 */

/**
 * Format date for server-side rendering (consistent format)
 */
export function formatDateSSR(dateString: string): string {
	const date = new Date(dateString);
	return date.toISOString().split("T")[0] || ""; // YYYY-MM-DD format
}

/**
 * Format date for blog post display (server-safe)
 */
export function formatBlogPostDate(dateString: string): string {
	const date = new Date(dateString);

	// Use a consistent format that works on both server and client
	const months = [
		"January",
		"February",
		"March",
		"April",
		"May",
		"June",
		"July",
		"August",
		"September",
		"October",
		"November",
		"December",
	];

	return `${months[date.getUTCMonth()]} ${date.getUTCDate()}, ${date.getUTCFullYear()}`;
}

/**
 * Format date with custom options
 */
export function formatDate(
	date: string | Date,
	options: Intl.DateTimeFormatOptions = {
		year: "numeric",
		month: "long",
		day: "numeric",
	},
): string {
	const dateObj = typeof date === "string" ? new Date(date) : date;

	if (isNaN(dateObj.getTime())) {
		throw new Error("Invalid date");
	}

	return new Intl.DateTimeFormat("en-US", options).format(dateObj);
}

/**
 * Format date relative to now (e.g., "2 hours ago")
 */
export function formatDateRelative(date: string | Date): string {
	const dateObj = typeof date === "string" ? new Date(date) : date;
	const now = new Date();
	const diffInMs = now.getTime() - dateObj.getTime();
	const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
	const diffInHours = Math.floor(diffInMinutes / 60);
	const diffInDays = Math.floor(diffInHours / 24);
	const diffInWeeks = Math.floor(diffInDays / 7);

	if (diffInMinutes < 60) {
		return diffInMinutes === 1 ? "1 minute ago" : `${diffInMinutes} minutes ago`;
	} else if (diffInHours < 24) {
		return diffInHours === 1 ? "1 hour ago" : `${diffInHours} hours ago`;
	} else if (diffInDays < 7) {
		return diffInDays === 1 ? "1 day ago" : `${diffInDays} days ago`;
	} else {
		return diffInWeeks === 1 ? "1 week ago" : `${diffInWeeks} weeks ago`;
	}
}
