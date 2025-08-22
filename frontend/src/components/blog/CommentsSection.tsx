"use client";

import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
	useCreateComment,
	useGetPostComments,
} from "@/lib/api/generated/client";
import { useCommentsWebSocket } from "@/hooks/useCommentsWebSocket";
import { useWebSocketStatus } from "@/hooks/useWebSocketManager";
import { formatBlogPostDate } from "@/lib/utils/date";
import { useErrorHandler } from "@/lib/errors";

export interface CommentsSectionProps {
	/** Post ID to fetch comments for */
	postId: string;
}

export function CommentsSection({ postId }: CommentsSectionProps) {
	const [newComment, setNewComment] = useState("");
	const { showError } = useErrorHandler();

    // Fetch comments directly via REST API
    // Memoize params so React Query key stays stable across renders
    const commentsParams = useMemo(() => ({ limit: 50 as const }), []);
    const {
        data: commentsResponse,
        isLoading: isLoadingComments,
        refetch: refetchComments,
        error: commentsError,
    } = useGetPostComments(postId, commentsParams);

	const comments = commentsResponse?.data || [];

    // WebSocket connection for real-time new comment notifications
    useCommentsWebSocket({
        onCommentsReceived: (receivedPostId) => {
            // When a new comment notification comes via WebSocket, refetch from REST API
            if (receivedPostId === postId) {
                refetchComments();
            }
        }
    });

    // Determine if WebSocket is connected to avoid duplicate refetches
    const { isConnected } = useWebSocketStatus();

    const createCommentMutation = useCreateComment({
        mutation: {
            onSuccess: () => {
                // If WebSocket is not connected, refetch here as a fallback.
                // Otherwise the comment.created event will trigger refetch.
                if (!isConnected) {
                    refetchComments();
                }
                setNewComment("");
            },
            onError: (error) => {
                showError(error, "Failed to add comment");
            },
        },
    });

	const handleSubmit = async () => {
		if (!newComment.trim()) return;
		
		try {
			// Create comment - returns acknowledgment only
			await createCommentMutation.mutateAsync({
				id: postId,
				data: {
					content: newComment.trim(),
				},
			});
		} catch {
			// Error is already handled by onError callback
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
						) : commentsError ? (
							<div className="text-center py-8">
								<p className="text-destructive mb-2">Failed to load comments</p>
								<Button
									variant="outline"
									size="sm"
									onClick={() => refetchComments()}
								>
									Try Again
								</Button>
							</div>
						) : comments.length === 0 ? (
							<p className="text-muted-foreground text-center py-8">
								No comments yet. Be the first to comment!
							</p>
						) : (
							comments.map((comment) => (
								<div key={comment.id} className="border-l-2 border-muted pl-4 space-y-2">
									<div className="flex items-center space-x-2 text-sm text-muted-foreground">
										<span className="font-medium text-foreground">{comment.userId}</span>
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
