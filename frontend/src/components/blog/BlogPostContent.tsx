import { Edit } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatBlogPostDate } from "@/lib/utils/date";

export interface BlogPostContentProps {
	/** Post title */
	title: string;
	/** Post content (markdown or plain text) */
	content: string;
	/** Post author */
	author: string;
	/** Publication date */
	publishedAt: string;
	/** Post tags */
	tags?: string[];
	/** Reading time estimate */
	readingTime?: string;
	/** Post ID for edit functionality */
	postId?: string;
	/** Whether current user can edit this post */
	canEdit?: boolean;
}

export function BlogPostContent({
	title,
	content,
	author,
	publishedAt,
	tags = [],
	readingTime,
	postId,
	canEdit = false,
}: BlogPostContentProps) {
	const formattedDate = formatBlogPostDate(publishedAt);

	return (
		<article className="max-w-4xl mx-auto">
			<header className="mb-8 pb-8 border-b">
				<div className="flex flex-wrap gap-2 mb-4">
					{tags.map((tag) => (
						<Badge key={tag} variant="secondary">
							{tag}
						</Badge>
					))}
				</div>

				<h1 className="text-4xl font-bold mb-4 leading-tight">{title}</h1>

				<div className="flex items-center justify-between">
					<div className="flex items-center text-muted-foreground space-x-4">
						<span>By {author}</span>
						<span>•</span>
						<span>{formattedDate}</span>
						{readingTime && (
							<>
								<span>•</span>
								<span>{readingTime}</span>
							</>
						)}
					</div>

					{canEdit && postId && (
						<Button variant="outline" size="sm" asChild>
							<Link href={`/create-post?id=${postId}`}>
								<Edit className="h-4 w-4 mr-2" />
								Edit Post
							</Link>
						</Button>
					)}
				</div>
			</header>

			<div className="prose prose-lg max-w-none">
				{/* For now, rendering content as plain text. In production, you'd use a markdown parser */}
				{content &&
					content.split("\n").map((paragraph, index) => (
						<p key={index} className="mb-4 leading-relaxed">
							{paragraph}
						</p>
					))}
				{!content && <p className="text-muted-foreground">No content available</p>}
			</div>
		</article>
	);
}
