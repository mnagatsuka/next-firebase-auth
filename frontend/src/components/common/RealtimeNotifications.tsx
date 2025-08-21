'use client'

import { useWebSocket } from '@/hooks/useWebSocket'
import { toast } from 'sonner'

export function RealtimeNotifications() {
  useWebSocket({
    url: process.env.NODE_ENV === 'development' 
      ? process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:4566'
      : process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'wss://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/dev',
    
    onMessage: (message) => {
      switch (message.type) {
        case 'comments_list':
          // Handle comments list response from GET request via API Gateway
          handleCommentsList(message.data)
          break
        case 'blog_update':
          toast.info(`Blog post ${message.data.action}: ${message.data.post_id}`)
          break
        case 'comment_update':
          toast.info(`New comment on post ${message.data.post_id}`)
          break
        default:
          console.log('Unknown WebSocket message type:', message.type)
      }
    },
    
    onConnect: () => {
      console.log('Real-time notifications connected')
    },
    
    onDisconnect: () => {
      console.warn('Real-time notifications disconnected')
    },
    
    onError: (error) => {
      console.error('WebSocket error:', error)
    }
  })

  const handleCommentsList = (data: any) => {
    // Update comments list in UI from API Gateway WebSocket response
    // This will be handled by specific comment components using the comments WebSocket hook
    console.log(`Received ${data.count} comments for post ${data.post_id}`)
  }

  return null // This component only handles background WebSocket connection
}