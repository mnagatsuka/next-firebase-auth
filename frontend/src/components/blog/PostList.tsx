import type { BlogPostSummary } from "@/lib/api/generated/schemas";
import { PostCard } from "./PostCard";
import { PostListSkeleton } from "./PostCardSkeleton";
import { classNames, gridLayouts } from "@/lib/design/tokens";
import { cn } from "@/lib/utils/cn";

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
    actions?: "default" | "view-and-edit" | "view-only";
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
			<div className={cn("text-center py-12")}>
				<p className={cn(classNames.textMuted, "text-lg")}>{emptyMessage}</p>
			</div>
		);
	}

	return (
		<div className={gridLayouts.posts}>
			{posts.map((post) => (
				<PostCard
					key={post.id}
					id={post.id}
					title={post.title}
					excerpt={post.excerpt}
					author={post.author}
					publishedAt={post.publishedAt}
					status={showStatus ? post.status : "published"}
					showStatus={showStatus}
					actions={actions}
				/>
			))}
		</div>
	);
}
