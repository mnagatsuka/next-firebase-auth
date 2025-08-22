import { describe, expect, it } from "vitest";
import {
	formatBlogPostDate,
	formatDate,
	formatDateRelative,
	formatDateSSR,
} from "@/lib/utils/date";

describe("lib/utils/date", () => {
	it("formatDateSSR returns YYYY-MM-DD", () => {
		expect(formatDateSSR("2024-01-05T12:34:56.000Z")).toBe("2024-01-05");
	});

	it("formatBlogPostDate returns readable date", () => {
		// Jan 5, 2024 UTC
		expect(formatBlogPostDate("2024-01-05T00:00:00.000Z")).toBe("January 5, 2024");
	});

	it("formatDate supports options", () => {
		const date = new Date("2024-01-05T00:00:00.000Z");
		const text = formatDate(date, { year: "numeric", month: "2-digit", day: "2-digit" });
		// Locale-dependent formatting can vary by environment, so check parts
		expect(text).toMatch(/01/);
		expect(text).toMatch(/05/);
		expect(text).toMatch(/2024/);
	});

	it("formatDate throws on invalid date", () => {
		expect(() => formatDate("invalid-date")).toThrow("Invalid date");
	});

	it("formatDateRelative returns human friendly text", () => {
		const now = new Date();
		const tenMinutesAgo = new Date(now.getTime() - 10 * 60 * 1000);
		const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

		expect(formatDateRelative(tenMinutesAgo)).toMatch(/minute/);
		expect(formatDateRelative(oneDayAgo)).toMatch(/day/);
	});
});
