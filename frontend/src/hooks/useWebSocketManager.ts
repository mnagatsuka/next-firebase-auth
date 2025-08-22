'use client'

import { useEffect } from 'react'
import { useWebSocketStore, WebSocketMessage } from '@/lib/stores/websocket'

/**
 * Hook to initialize and manage the global WebSocket connection
 * Should be used once at the app level
 */
export function useWebSocketManager() {
  const { connect, disconnect, isConnected, lastError } = useWebSocketStore()

  useEffect(() => {
    const url = process.env.NODE_ENV === 'development' 
      ? process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:3001'
      : process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'wss://your-api-gateway-id.execute-api.ap-northeast-1.amazonaws.com/dev'

    connect(url)

    // Cleanup on unmount
    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    lastError
  }
}

/**
 * Hook to subscribe to specific WebSocket message types
 * Can be used in multiple components
 */
export function useWebSocketSubscription(
  messageType: string,
  callback: (message: WebSocketMessage) => void
) {
  const subscribe = useWebSocketStore(state => state.subscribe)

  useEffect(() => {
    const unsubscribe = subscribe(messageType, callback)
    return unsubscribe
  }, [subscribe, messageType, callback])
}

/**
 * Hook to get WebSocket connection status
 */
export function useWebSocketStatus() {
  const isConnected = useWebSocketStore(state => state.isConnected)
  const lastError = useWebSocketStore(state => state.lastError)
  const reconnectAttempts = useWebSocketStore(state => state.reconnectAttempts)

  return {
    isConnected,
    lastError,
    reconnectAttempts
  }
}
