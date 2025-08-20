"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export interface BlogPaginationProps {
	/** Current page number */
	currentPage: number;
	/** Total number of pages */
	totalPages: number;
	/** Whether there is a next page */
	hasNext: boolean;
	/** Whether there is a previous page */
	hasPrevious: boolean;
	/** Optional base path for links (default "/") */
	basePath?: string;
	/** Optional extra query params to preserve (excluding page) */
	query?: Record<string, string | undefined>;
	/** Optional custom page change handler */
	onPageChange?: (page: number) => void;
}

export function BlogPagination({
	currentPage,
	totalPages,
	hasNext,
	hasPrevious,
	basePath = "/",
	query,
	onPageChange,
}: BlogPaginationProps) {
	const router = useRouter();

	const handlePageChange = (page: number) => {
		if (onPageChange) {
			onPageChange(page);
			return;
		}

		const params = new URLSearchParams();
		if (query) {
			for (const [k, v] of Object.entries(query)) {
				if (v !== undefined && v !== "") params.set(k, String(v));
			}
		}
		if (page > 1) params.set("page", String(page));
		else params.delete("page");

		const qs = params.toString();
		router.push(qs ? `${basePath}?${qs}` : basePath);
	};

	if (totalPages <= 1) {
		return null;
	}

	return (
		<div className="flex justify-center items-center space-x-4">
			<Button
				variant="outline"
				onClick={() => handlePageChange(currentPage - 1)}
				disabled={!hasPrevious}
				className="flex items-center space-x-1"
			>
				<ChevronLeft className="h-4 w-4" />
				<span>Previous</span>
			</Button>

			<span className="text-sm text-muted-foreground px-4">
				Page {currentPage} of {totalPages}
			</span>

			<Button
				variant="outline"
				onClick={() => handlePageChange(currentPage + 1)}
				disabled={!hasNext}
				className="flex items-center space-x-1"
			>
				<span>Next</span>
				<ChevronRight className="h-4 w-4" />
			</Button>
		</div>
	);
}
