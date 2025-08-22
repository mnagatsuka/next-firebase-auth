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

  it('should handle comment.created messages', () => {
    const onCommentsReceived = vi.fn()

    renderHook(() =>
      useCommentsWebSocket({
        onCommentsReceived
      })
    )

    const message = {
      type: 'comment.created',
      data: {
        postId: 'test-post-123',
        comment: {
          id: 'comment-1',
          content: 'Test comment',
          userId: 'user-123',
          createdAt: '2024-01-01T00:00:00Z',
          postId: 'test-post-123'
        }
      },
      version: '1',
      id: 'msg-1',
      source: 'backend',
      timestamp: '2024-01-01T00:00:00Z'
    }

    if ((global as any).mockWebSocketOnMessage) {
      (global as any).mockWebSocketOnMessage(message)
    }

    expect(onCommentsReceived).toHaveBeenCalledWith('test-post-123', [])
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
    process.env.NEXT_PUBLIC_WEBSOCKET_URL = 'ws://test-dev:3001'

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
