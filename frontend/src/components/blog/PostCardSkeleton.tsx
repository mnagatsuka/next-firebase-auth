import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function PostCardSkeleton() {
	return (
		<Card>
			<CardHeader>
				<Skeleton className="h-6 w-3/4" />
				<Skeleton className="h-4 w-1/2" />
			</CardHeader>
			<CardContent className="space-y-3">
				<Skeleton className="h-4 w-full" />
				<Skeleton className="h-4 w-4/5" />
				<Skeleton className="h-4 w-2/3" />
				<div className="flex items-center justify-between pt-4">
					<Skeleton className="h-4 w-20" />
					<Skeleton className="h-4 w-24" />
				</div>
			</CardContent>
		</Card>
	);
}

export function PostListSkeleton({ count = 6 }: { count?: number }) {
	return (
		<div className="grid gap-6 md:grid-cols-2">
			{Array.from({ length: count }).map((_, i) => (
				<PostCardSkeleton key={i} />
			))}
		</div>
	);
}
