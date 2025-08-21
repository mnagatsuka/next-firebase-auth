import { renderHook, act } from '@testing-library/react'
import { useWebSocket } from '@/hooks/useWebSocket'
import { vi } from 'vitest'

// Mock WebSocket
class MockWebSocket {
  url: string
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(url: string) {
    this.url = url
    // Simulate async connection
    setTimeout(() => {
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 0)
  }

  close() {
    if (this.onclose) {
      this.onclose(new CloseEvent('close'))
    }
  }

  send(data: string) {
    // Mock send implementation
  }
}

// Mock global WebSocket
global.WebSocket = MockWebSocket as any

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllTimers()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
  })

  it('should connect to WebSocket successfully', () => {
    const onConnect = vi.fn()
    const { result } = renderHook(() => 
      useWebSocket({
        url: 'ws://localhost:4566',
        onConnect
      })
    )

    // Fast-forward timers to trigger the connection
    act(() => {
      vi.runAllTimers()
    })

    expect(onConnect).toHaveBeenCalled()
    expect(result.current.disconnect).toBeDefined()
  })

  it('should handle WebSocket messages', () => {
    const onMessage = vi.fn()
    const testMessage = {
      type: 'comments_list',
      data: { post_id: 'test-post', comments: [] },
      timestamp: '2024-01-01T00:00:00Z'
    }

    renderHook(() => 
      useWebSocket({
        url: 'ws://localhost:4566',
        onMessage
      })
    )

    // Simulate receiving a message
    act(() => {
      const mockWs = global.WebSocket as any
      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(testMessage)
      })
      
      if (mockWs.prototype.onmessage) {
        mockWs.prototype.onmessage(messageEvent)
      }
    })

    expect(onMessage).toHaveBeenCalledWith(testMessage)
  })

  it('should handle connection disconnection', () => {
    const onDisconnect = vi.fn()
    const { result } = renderHook(() => 
      useWebSocket({
        url: 'ws://localhost:4566',
        onDisconnect
      })
    )

    act(() => {
      result.current.disconnect()
    })

    expect(onDisconnect).toHaveBeenCalled()
  })
})