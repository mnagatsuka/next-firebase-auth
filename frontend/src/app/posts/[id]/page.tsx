import { notFound } from "next/navigation";
import { BlogPostContent } from "@/components/blog/BlogPostContent";
import { CommentsSection } from "@/components/blog/CommentsSection";
import { getBlogPostById } from "@/lib/api/generated/client";
import { getServerAuthorizationHeader, getServerUser } from "@/lib/auth/session";

interface BlogPostPageProps {
	params: Promise<{ id: string }>;
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
	const { id: postId } = await params;

	try {
		// Get the wrapped response and extract the data property
		const authHeader = await getServerAuthorizationHeader();
		const response = await getBlogPostById(postId, authHeader ? { headers: { Authorization: authHeader } } : undefined);

		// Extract the actual post data from the response envelope
		const post = response.data;

    // Get current user to check ownership
    const currentUser = await getServerUser();

    // Determine if current user is anonymous
    const isAnon = !!(currentUser && (currentUser as any)?.firebase?.sign_in_provider === "anonymous");

    // Check if current user can edit this post (owns it) and is not anonymous
    // Note: This assumes the post has an authorId or email in author field - adjust based on your actual schema
    const canEdit =
        !!(
            currentUser &&
            !isAnon &&
            (currentUser.uid === post.author || // If author field contains user ID
                currentUser.email === post.author)
        ); // If author field contains email

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
					isFavorited={(post as any).isFavorited ?? false}
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
