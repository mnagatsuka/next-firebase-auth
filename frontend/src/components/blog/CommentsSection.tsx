"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export interface Comment {
  id: string
  content: string
  author: string
  createdAt: string
}

export interface CommentsSectionProps {
  /** Array of comments to display */
  comments: Comment[]
  /** Loading state for comments */
  isLoading?: boolean
  /** Loading state for form submission */
  isSubmitting?: boolean
  /** Callback for adding new comment */
  onAddComment?: (author: string, content: string) => void
}

export function CommentsSection({
  comments,
  isLoading = false,
  isSubmitting = false,
  onAddComment
}: CommentsSectionProps) {
  const [newComment, setNewComment] = useState("")
  const [authorName, setAuthorName] = useState("")

  const handleSubmit = () => {
    if (newComment.trim() && authorName.trim()) {
      onAddComment?.(authorName.trim(), newComment.trim())
      setNewComment("")
      setAuthorName("")
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
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
                disabled={isSubmitting}
              />
              <Textarea
                placeholder="Write your comment..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                disabled={isSubmitting}
                rows={4}
              />
              <Button
                onClick={handleSubmit}
                disabled={isSubmitting || !newComment.trim() || !authorName.trim()}
              >
                {isSubmitting ? "Posting..." : "Post Comment"}
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
                    <span>{formatDate(comment.createdAt)}</span>
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