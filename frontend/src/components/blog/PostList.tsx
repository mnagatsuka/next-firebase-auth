import type { BlogPostSummary } from "@/lib/api/generated/schemas";
import { PostCard } from "./PostCard";
import { PostListSkeleton } from "./PostCardSkeleton";

export interface PostListProps {
	/** Array of blog posts to display */
	posts: BlogPostSummary[];
	/** Loading state */
	isLoading?: boolean;
	/** Empty state message */
	emptyMessage?: string;
	/** Whether to show post status badges */
	showStatus?: boolean;
	/** Action buttons style for each item */
	actions?: "default" | "view-and-edit";
}

export function PostList({
	posts,
	isLoading = false,
	emptyMessage = "No posts found.",
	showStatus = false,
	actions = "default",
}: PostListProps) {
	if (isLoading) {
		return <PostListSkeleton count={6} />;
	}

	if (posts.length === 0) {
		return (
			<div className="text-center py-12">
				<p className="text-muted-foreground text-lg">{emptyMessage}</p>
			</div>
		);
	}

	return (
		<div className="grid gap-6 md:grid-cols-2">
			{posts.map((post) => (
				<PostCard
					key={post.id}
					id={post.id}
					title={post.title}
					excerpt={post.excerpt}
					author={post.author}
					publishedAt={post.publishedAt}
					status={showStatus ? (post as any).status ?? "draft" : "published"}
					showStatus={showStatus}
					actions={actions}
				/>
			))}
		</div>
	);
}
