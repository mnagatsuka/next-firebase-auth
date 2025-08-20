import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function Loading() {
	return (
		<div className="space-y-12">
			{/* Blog Post Content Skeleton */}
			<article className="max-w-4xl mx-auto animate-pulse">
				<header className="mb-8 pb-8 border-b">
					<div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div> {/* Tags */}
					<div className="h-10 bg-gray-200 rounded w-3/4 mb-4"></div> {/* Title */}
					<div className="h-6 bg-gray-200 rounded w-1/2"></div> {/* Author/Date */}
				</header>

				<div className="space-y-4">
					<div className="h-4 bg-gray-200 rounded"></div>
					<div className="h-4 bg-gray-200 rounded w-5/6"></div>
					<div className="h-4 bg-gray-200 rounded"></div>
					<div className="h-4 bg-gray-200 rounded w-4/5"></div>
					<div className="h-4 bg-gray-200 rounded"></div>
					<div className="h-4 bg-gray-200 rounded w-2/3"></div>
				</div>
			</article>

			{/* Comments Section Skeleton */}
			<div className="max-w-4xl mx-auto mt-12">
				<Card className="animate-pulse">
					<CardHeader>
						<div className="h-6 bg-gray-200 rounded w-1/3"></div> {/* Comments title */}
					</CardHeader>
					<CardContent className="space-y-6">
						{/* Add Comment Form Skeleton */}
						<div className="space-y-4 p-4 bg-muted/50 rounded-lg">
							<div className="h-4 bg-gray-200 rounded w-1/4"></div>
							<div className="h-8 bg-gray-200 rounded"></div>
							<div className="h-20 bg-gray-200 rounded"></div>
							<div className="h-8 bg-gray-200 rounded w-1/5"></div>
						</div>

						{/* Comments List Skeleton */}
						<div className="space-y-4">
							{Array.from({ length: 2 }).map((_, i) => (
								<div key={i} className="border-l-2 border-muted pl-4 space-y-2">
									<div className="h-4 bg-gray-200 rounded w-1/3"></div>
									<div className="h-12 bg-gray-200 rounded"></div>
								</div>
							))}
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
