'use client'

import { useWebSocket, WebSocketMessage } from './useWebSocket'
import { useCallback } from 'react'
import type { Comment } from '@/lib/api/generated/schemas'

export interface CommentsWebSocketHookOptions {
  onCommentsReceived?: (postId: string, comments: Comment[]) => void
}

export function useCommentsWebSocket({
  onCommentsReceived
}: CommentsWebSocketHookOptions) {
  
  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'comments_list':
        onCommentsReceived?.(message.data.post_id, message.data.comments)
        break
      // No comment_created handler needed - POST still uses REST
    }
  }, [onCommentsReceived])

  const { disconnect } = useWebSocket({
    url: process.env.NODE_ENV === 'development' 
      ? process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:4566'
      : process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'wss://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/dev',
    onMessage: handleMessage,
    
    onConnect: () => {
      console.log('Comments WebSocket connected')
    },
    
    onDisconnect: () => {
      console.warn('Comments WebSocket disconnected')
    },
    
    onError: (error) => {
      console.error('Comments WebSocket error:', error)
    }
  })

  return { disconnect }
}