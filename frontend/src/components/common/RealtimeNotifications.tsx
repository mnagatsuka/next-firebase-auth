'use client'

import { useWebSocketManager, useWebSocketSubscription } from '@/hooks/useWebSocketManager'
import { toast } from 'sonner'

export function RealtimeNotifications() {
  // Initialize the global WebSocket connection
  const { lastError } = useWebSocketManager()

  // Subscribe to blog update messages for notifications
  useWebSocketSubscription('blog_update', (message) => {
    toast.info(`Blog post ${message.data.action}: ${message.data.post_id}`)
  })

  // Subscribe to comment created messages for notifications
  useWebSocketSubscription('comment.created', (message) => {
    toast.info(`New comment on post ${message.data.postId}`)
  })

  // Subscribe to test messages for debugging
  useWebSocketSubscription('test', (message) => {
    console.log('🧪 Test message received:', message.data)
  })

  // Show connection status in console
  useWebSocketSubscription('*', (message) => {
    console.log('🔔 Realtime notification:', message.type)
  })

  // Log connection status changes
  if (lastError) {
    console.warn('⚠️ WebSocket error:', lastError)
  }

  return null // This component only handles background WebSocket connection and notifications
}
