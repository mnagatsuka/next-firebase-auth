'use client'

import { useWebSocketSubscription } from './useWebSocketManager'
import { useCallback } from 'react'
import type { Comment } from '@/lib/api/generated/schemas'

export interface CommentsWebSocketHookOptions {
  onNewCommentReceived?: (postId: string, comment: Comment) => void
  onCommentsReceived?: (postId: string, comments: Comment[]) => void
}

export function useCommentsWebSocket({
  onNewCommentReceived,
  onCommentsReceived
}: CommentsWebSocketHookOptions) {
  
  const handleMessage = useCallback((message: any) => {
    console.log('📝 Comments WebSocket received:', message.type, message)
    
    if (message.type === 'comment.created') {
      const postId = message.data?.postId
      const comment = message.data?.comment
      if (onNewCommentReceived && postId && comment) {
        onNewCommentReceived(postId, comment)
      }
      if (onCommentsReceived && postId) {
        // Trigger consumer to refetch comments for this post
        onCommentsReceived(postId, [])
      }
    }
  }, [onNewCommentReceived, onCommentsReceived])

  // Subscribe to NEW_COMMENT messages from the centralized WebSocket
  useWebSocketSubscription('comment.created', handleMessage)

  // Return empty object for compatibility
  return {}
}
