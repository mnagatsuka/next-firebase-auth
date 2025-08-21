"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// Name input removed; user identity comes from auth on server
import { Textarea } from "@/components/ui/textarea";
import {
	useCreateComment,
	getPostComments,
} from "@/lib/api/generated/client";
import { useCommentsWebSocket } from "@/hooks/useCommentsWebSocket";
import type { Comment } from "@/lib/api/generated/schemas";
import { formatBlogPostDate } from "@/lib/utils/date";

export interface CommentsSectionProps {
	/** Post ID to fetch comments for */
	postId: string;
}

export function CommentsSection({ postId }: CommentsSectionProps) {
	const [newComment, setNewComment] = useState("");
	const [comments, setComments] = useState<Comment[]>([]);
	const [isLoadingComments, setIsLoadingComments] = useState(true);

	// WebSocket connection for real-time comments
	useCommentsWebSocket({
		onCommentsReceived: (receivedPostId, receivedComments) => {
			if (receivedPostId === postId) {
				setComments(receivedComments);
				setIsLoadingComments(false);
			}
		}
	});

	const createCommentMutation = useCreateComment({
		mutation: {
			onSuccess: () => {
				// After successful comment creation, fetch comments to trigger WebSocket response
				loadComments();
			},
		},
	});

	// Function to load comments (triggers WebSocket response)
	const loadComments = useCallback(async () => {
		try {
			setIsLoadingComments(true);
			// This API call returns acknowledgment and sends data via WebSocket
			await getPostComments(postId);
		} catch (error) {
			console.error("Failed to load comments:", error);
			setIsLoadingComments(false);
		}
	}, [postId]);

	// Load comments on component mount
	useEffect(() => {
		loadComments();
	}, [loadComments]);

	const handleSubmit = async () => {
		if (newComment.trim()) {
			try {
				await createCommentMutation.mutateAsync({
					id: postId,
					data: {
						content: newComment.trim(),
						postId,
					} as any,
				});
				setNewComment("");
			} catch (error) {
				console.error("Failed to add comment:", error);
			}
		}
	};

	return (
		<div className="max-w-4xl mx-auto mt-12">
			<Card>
				<CardHeader>
					<CardTitle>Comments ({comments.length})</CardTitle>
				</CardHeader>
				<CardContent className="space-y-6">
					{/* Add Comment Form */}
					<div className="space-y-4 p-4 bg-muted/50 rounded-lg">
						<h3 className="font-medium">Add a Comment</h3>
						<div className="space-y-3">
								{/* Name input removed */}
							<Textarea
								placeholder="Write your comment..."
								value={newComment}
								onChange={(e) => setNewComment(e.target.value)}
								disabled={createCommentMutation.isPending}
								rows={4}
							/>
							<Button
								onClick={handleSubmit}
								disabled={createCommentMutation.isPending || !newComment.trim()}
							>
								{createCommentMutation.isPending ? "Posting..." : "Post Comment"}
							</Button>
						</div>
					</div>

					{/* Comments List */}
					<div className="space-y-4">
						{isLoadingComments ? (
							<div className="space-y-4">
								{Array.from({ length: 3 }).map((_, i) => (
									<div key={i} className="animate-pulse">
										<div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
										<div className="h-16 bg-gray-200 rounded"></div>
									</div>
								))}
							</div>
						) : comments.length === 0 ? (
							<p className="text-muted-foreground text-center py-8">
								No comments yet. Be the first to comment!
							</p>
						) : (
							comments.map((comment) => (
								<div key={comment.id} className="border-l-2 border-muted pl-4 space-y-2">
									<div className="flex items-center space-x-2 text-sm text-muted-foreground">
											<span className="font-medium text-foreground">{(comment as any).userId ?? (comment as any).author}</span>
										<span>•</span>
										<span>{formatBlogPostDate(comment.createdAt)}</span>
									</div>
									<p className="text-sm leading-relaxed">{comment.content}</p>
								</div>
							))
						)}
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
