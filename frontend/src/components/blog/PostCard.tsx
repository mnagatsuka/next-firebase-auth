import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatBlogPostDate } from "@/lib/utils/date";

export interface PostCardProps {
	/** Unique post identifier */
	id: string;
	/** Post title */
	title: string;
	/** Post excerpt/summary */
	excerpt: string;
	/** Post author name */
	author: string;
	/** Publication date */
	publishedAt: string;
	/** Optional post tags */
	tags?: string[];
	/** Post status */
	status?: "draft" | "published";
	/** Whether to show status badge */
	showStatus?: boolean;
	/** Action buttons style */
	actions?: "default" | "view-and-edit";
}

export function PostCard({
	id,
	title,
	excerpt,
	author,
	publishedAt,
	tags = [],
	status = "published",
	showStatus = false,
	actions = "default",
}: PostCardProps) {
	const formattedDate = formatBlogPostDate(publishedAt);
	const isDraft = status === "draft";
	const detailHref = `/posts/${id}`;
	const editHref = `/create-post?id=${id}`;
	const primaryHref = actions === "view-and-edit" ? detailHref : isDraft ? editHref : detailHref;

	return (
		<Card className="h-full">
			<CardHeader>
				<div className="flex flex-wrap gap-1 mb-2">
					{showStatus && (
						<Badge variant={isDraft ? "outline" : "default"} className="text-xs">
							{status.charAt(0).toUpperCase() + status.slice(1)}
						</Badge>
					)}
					{tags.map((tag) => (
						<Badge key={tag} variant="secondary" className="text-xs">
							{tag}
						</Badge>
					))}
				</div>
				<CardTitle className="line-clamp-2">
					<Link href={primaryHref} className="hover:underline">
						{title}
					</Link>
				</CardTitle>
				<CardDescription>
					By {author} • {formattedDate}
				</CardDescription>
			</CardHeader>
			<CardContent>
				<p className="text-sm text-muted-foreground line-clamp-3 mb-4">{excerpt}</p>
				{actions === "view-and-edit" ? (
					<div className="flex gap-2">
						<Button variant="outline" size="sm" asChild>
							<Link href={detailHref}>View</Link>
						</Button>
						<Button variant="default" size="sm" asChild>
							<Link href={editHref}>Edit</Link>
						</Button>
					</div>
				) : (
					<Button variant="outline" size="sm" asChild>
						<Link href={primaryHref}>{isDraft ? "Edit Draft" : "Read more"}</Link>
					</Button>
				)}
			</CardContent>
		</Card>
	);
}
