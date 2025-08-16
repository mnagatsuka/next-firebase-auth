"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useGetPostComments, useCreateComment } from "@/lib/api/generated/client"
import { formatBlogPostDate } from "@/lib/utils/date"

export interface CommentsSectionProps {
  /** Post ID to fetch comments for */
  postId: string
}


export function CommentsSection({ postId }: CommentsSectionProps) {
  const [newComment, setNewComment] = useState("")
  const [authorName, setAuthorName] = useState("")

  const { data: commentsResponse, isLoading } = useGetPostComments(postId)
  const createCommentMutation = useCreateComment()

  const comments = commentsResponse?.data || []

  const handleSubmit = async () => {
    if (newComment.trim() && authorName.trim()) {
      try {
        await createCommentMutation.mutateAsync({
          id: postId,
          data: {
            author: authorName.trim(),
            content: newComment.trim()
          }
        })
        setNewComment("")
        setAuthorName("")
      } catch (error) {
        console.error("Failed to add comment:", error)
      }
    }
  }

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
              <Input
                placeholder="Your name"
                value={authorName}
                onChange={(e) => setAuthorName(e.target.value)}
                disabled={createCommentMutation.isPending}
              />
              <Textarea
                placeholder="Write your comment..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                disabled={createCommentMutation.isPending}
                rows={4}
              />
              <Button
                onClick={handleSubmit}
                disabled={createCommentMutation.isPending || !newComment.trim() || !authorName.trim()}
              >
                {createCommentMutation.isPending ? "Posting..." : "Post Comment"}
              </Button>
            </div>
          </div>

          {/* Comments List */}
          <div className="space-y-4">
            {isLoading ? (
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
                    <span className="font-medium text-foreground">{comment.author}</span>
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
  )
}