import { notFound } from "next/navigation";
import { BlogPostContent } from "@/components/blog/BlogPostContent";
import { CommentsSection } from "@/components/blog/CommentsSection";
import { getBlogPostById } from "@/lib/api/generated/client";
import { getServerUser } from "@/lib/auth/session";

interface BlogPostPageProps {
	params: Promise<{ id: string }>;
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
	const { id: postId } = await params;

	try {
		// Get the wrapped response and extract the data property
		const response = await getBlogPostById(postId);

		// Extract the actual post data from the response envelope
		const post = response.data;

		// Get current user to check ownership
		const currentUser = await getServerUser();

		// Check if current user can edit this post (owns it)
		// Note: This assumes the post has an authorId field - adjust based on your actual schema
		const canEdit =
			currentUser &&
			(currentUser.uid === post.author || // If author field contains user ID
				currentUser.email === post.author); // If author field contains email

		return (
			<div className="space-y-12">
				<BlogPostContent
					title={post.title}
					content={post.content}
					author={post.author}
					publishedAt={post.publishedAt}
					tags={[]} // TODO: Add tags to BlogPost schema if needed
					postId={postId}
					canEdit={canEdit}
				/>
				<CommentsSection postId={postId} />
			</div>
		);
	} catch (error: any) {
		if (error.status === 404) {
			notFound();
		}
		throw error;
	}
}
