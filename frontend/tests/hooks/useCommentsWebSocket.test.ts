import { renderHook } from '@testing-library/react'
import { useCommentsWebSocket } from '@/hooks/useCommentsWebSocket'
import { vi } from 'vitest'

// Mock the useWebSocket hook
vi.mock('@/hooks/useWebSocket', () => ({
  useWebSocket: vi.fn((options) => {
    // Store the onMessage callback for testing
    (global as any).mockWebSocketOnMessage = options.onMessage
    return { disconnect: vi.fn() }
  })
}))

describe('useCommentsWebSocket', () => {
  beforeEach(() => {
    delete (global as any).mockWebSocketOnMessage
  })

  it('should handle comments_list messages', () => {
    const onCommentsReceived = vi.fn()
    
    renderHook(() => 
      useCommentsWebSocket({
        onCommentsReceived
      })
    )

    // Simulate receiving a comments_list message
    const message = {
      type: 'comments_list',
      data: {
        post_id: 'test-post-123',
        comments: [
          {
            id: 'comment-1',
            content: 'Test comment',
            user_id: 'user-123',
            created_at: '2024-01-01T00:00:00Z',
            post_id: 'test-post-123'
          }
        ],
        count: 1
      },
      timestamp: '2024-01-01T00:00:00Z'
    }

    if ((global as any).mockWebSocketOnMessage) {
      (global as any).mockWebSocketOnMessage(message)
    }

    expect(onCommentsReceived).toHaveBeenCalledWith(
      'test-post-123',
      message.data.comments
    )
  })

  it('should ignore unknown message types', () => {
    const onCommentsReceived = vi.fn()
    
    renderHook(() => 
      useCommentsWebSocket({
        onCommentsReceived
      })
    )

    // Simulate receiving an unknown message type
    const message = {
      type: 'unknown_message_type',
      data: { some: 'data' },
      timestamp: '2024-01-01T00:00:00Z'
    }

    if ((global as any).mockWebSocketOnMessage) {
      (global as any).mockWebSocketOnMessage(message)
    }

    expect(onCommentsReceived).not.toHaveBeenCalled()
  })

  it('should use correct WebSocket URL based on environment', () => {
    const originalEnv = process.env.NODE_ENV
    const originalWebSocketUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL

    // Test development environment
    process.env.NODE_ENV = 'development'
    process.env.NEXT_PUBLIC_WEBSOCKET_URL = 'ws://test-dev:4566'

    renderHook(() => 
      useCommentsWebSocket({
        onCommentsReceived: vi.fn()
      })
    )

    // Test production environment  
    process.env.NODE_ENV = 'production'
    process.env.NEXT_PUBLIC_WEBSOCKET_URL = 'wss://prod-gateway.amazonaws.com/dev'

    renderHook(() => 
      useCommentsWebSocket({
        onCommentsReceived: vi.fn()
      })
    )

    // Restore original environment
    process.env.NODE_ENV = originalEnv
    process.env.NEXT_PUBLIC_WEBSOCKET_URL = originalWebSocketUrl
  })
})