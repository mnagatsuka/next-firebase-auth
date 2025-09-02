# Frontend WebSocket Integration Guide

## Table of Contents
- [Overview](#overview)
- [WebSocket Store Architecture](#websocket-store-architecture)
- [Hook System](#hook-system)
- [Component Integration](#component-integration)
- [Message Handling](#message-handling)
- [Error Handling & Reconnection](#error-handling--reconnection)
- [Testing Strategy](#testing-strategy)

## Overview

The frontend WebSocket integration uses a **Zustand store** for centralized state management with a subscription-based message routing system. This provides a scalable way to handle real-time updates across multiple components.

**Key Features:**
- Centralized WebSocket connection management
- Type-safe message handling with TypeScript
- Automatic reconnection with exponential backoff
- Multiple subscribers per message type
- Environment-based WebSocket URL configuration

## WebSocket Store Architecture

### Core Store Implementation
**Location**: `frontend/src/lib/stores/websocket.ts`

```typescript
interface WebSocketStore {
  // Connection state
  socket: WebSocket | null
  isConnected: boolean
  isConnecting: boolean
  connectionAttempts: number
  
  // Subscription management
  subscriptions: Map<string, Set<MessageHandler>>
  
  // Actions
  connect: (url: string) => void
  disconnect: () => void
  subscribe: (messageType: string, handler: MessageHandler) => () => void
  sendMessage: (message: any) => void
}
```

### Store Features

#### 1. Connection Management
- **Automatic Connection**: Connects on first subscription
- **Connection State Tracking**: `isConnected`, `isConnecting` flags
- **Reconnection Logic**: Exponential backoff with max 5 attempts
- **Clean Disconnection**: Proper WebSocket cleanup

#### 2. Subscription System
- **Type-based Routing**: Messages routed by `message.type` field
- **Multiple Subscribers**: Multiple components can subscribe to same message type
- **Automatic Cleanup**: Subscriptions removed when components unmount
- **Handler Registration**: Simple subscribe/unsubscribe pattern

#### 3. Message Processing
- **JSON Parsing**: Automatic parsing of incoming WebSocket messages
- **Error Tolerance**: Continues processing if individual messages fail
- **Type Validation**: Runtime validation of message structure

## Hook System

### 1. useWebSocketManager Hook
**Location**: `frontend/src/hooks/useWebSocketManager.ts`

```typescript
export function useWebSocketManager() {
  const {
    isConnected,
    isConnecting, 
    connectionAttempts,
    connect,
    disconnect,
    subscribe
  } = useWebSocketStore()
  
  // Auto-connect with environment URL
  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:3001'
    connect(wsUrl)
    
    return disconnect
  }, [])
  
  return {
    isConnected,
    isConnecting,
    connectionAttempts,
    subscribe,
    disconnect
  }
}
```

**Features:**
- Environment-based URL configuration
- Automatic connection on mount
- Connection status monitoring
- Clean disconnection on unmount

### 2. useCommentsWebSocket Hook  
**Location**: `frontend/src/hooks/useCommentsWebSocket.ts`

```typescript
interface CommentsWebSocketHookProps {
  onCommentCreated?: (data: CommentCreatedData) => void
  onCommentsListUpdated?: (data: CommentsListData) => void
  enabled?: boolean
}

export function useCommentsWebSocket({
  onCommentCreated,
  onCommentsListUpdated,
  enabled = true
}: CommentsWebSocketHookProps) {
  const { subscribe } = useWebSocketManager()
  
  useEffect(() => {
    if (!enabled) return
    
    const unsubscribeCreated = subscribe('comment.created', (message) => {
      onCommentCreated?.(message.data)
    })
    
    const unsubscribeList = subscribe('comments.list', (message) => {
      onCommentsListUpdated?.(message.data)
    })
    
    return () => {
      unsubscribeCreated()
      unsubscribeList()
    }
  }, [enabled, onCommentCreated, onCommentsListUpdated])
}
```

**Features:**
- Comment-specific message handling
- Optional callback functions
- Enable/disable functionality
- Automatic subscription management

### 3. Basic useWebSocket Hook
**Location**: `frontend/src/hooks/useWebSocket.ts`

Lower-level hook for direct WebSocket management (used internally by the store):

```typescript
export interface UseWebSocketOptions {
  url: string
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
  reconnectAttempts?: number
  reconnectInterval?: number
}

export function useWebSocket(options: UseWebSocketOptions) {
  // WebSocket connection logic with reconnection
  // Used internally by WebSocket store
}
```

## Component Integration

### 1. CommentsSection Component
**Location**: `frontend/src/components/blog/CommentsSection.tsx`

```typescript
export function CommentsSection({ postId }: { postId: string }) {
  const [comments, setComments] = useState<Comment[]>([])
  
  // WebSocket integration for real-time updates
  useCommentsWebSocket({
    onCommentCreated: (data) => {
      if (data.postId === postId) {
        setComments(prev => [data.comment, ...prev])
        toast.success('New comment added!')
      }
    },
    
    onCommentsListUpdated: (data) => {
      if (data.postId === postId) {
        setComments(data.comments)
      }
    }
  })
  
  // Handle comment creation
  const handleCreateComment = async (content: string) => {
    try {
      // POST request returns acknowledgment only
      await createComment(postId, content)
      // Actual comment data comes via WebSocket
    } catch (error) {
      toast.error('Failed to create comment')
    }
  }
  
  return (
    <div>
      <CommentForm onSubmit={handleCreateComment} />
      <CommentList comments={comments} />
    </div>
  )
}
```

**Integration Features:**
- Real-time comment additions
- Post-specific comment filtering
- Toast notifications for user feedback
- Seamless REST + WebSocket workflow

### 2. RealtimeNotifications Component
**Location**: `frontend/src/components/common/RealtimeNotifications.tsx`

```typescript
export function RealtimeNotifications() {
  const { isConnected, isConnecting } = useWebSocketManager()
  
  // Subscribe to various notification types
  useEffect(() => {
    const { subscribe } = useWebSocketStore.getState()
    
    const unsubscribeComment = subscribe('comment.created', (message) => {
      const { postId, comment } = message.data
      toast.info(`New comment on post ${postId.slice(0, 8)}...`, {
        description: comment.content.slice(0, 100)
      })
    })
    
    const unsubscribeBlog = subscribe('blog_update', (message) => {
      const { action, post_id } = message.data
      toast.info(`Blog post ${action}: ${post_id.slice(0, 8)}...`)
    })
    
    const unsubscribeTest = subscribe('test', (message) => {
      toast.success('Test message received', {
        description: message.data.message
      })
    })
    
    return () => {
      unsubscribeComment()
      unsubscribeBlog() 
      unsubscribeTest()
    }
  }, [])
  
  // Connection status indicator (optional)
  return (
    <div className="fixed bottom-4 right-4">
      {isConnecting && (
        <div className="bg-yellow-100 p-2 rounded">
          Connecting to real-time updates...
        </div>
      )}
      {!isConnected && (
        <div className="bg-red-100 p-2 rounded">
          Real-time updates unavailable
        </div>
      )}
    </div>
  )
}
```

**Features:**
- Global notification system
- Connection status monitoring
- Multiple message type subscriptions
- Toast notification integration

### 3. Layout Integration
**Location**: `frontend/src/app/layout.tsx`

```typescript
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div id="root">
          {children}
        </div>
        
        {/* WebSocket integration - loads on all pages */}
        <RealtimeNotifications />
        
        {/* Toast notification container */}
        <Toaster />
      </body>
    </html>
  )
}
```

## Message Handling

### Message Structure
All WebSocket messages follow a consistent structure:

```typescript
interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}
```

### Supported Message Types

#### 1. Comment Created
```typescript
interface CommentCreatedData {
  postId: string
  comment: {
    id: string
    content: string
    userId: string
    createdAt: string
    postId: string
  }
}
```

#### 2. Comments List Updated
```typescript
interface CommentsListData {
  postId: string
  comments: Comment[]
  count: number
}
```

#### 3. Blog Updates
```typescript
interface BlogUpdateData {
  post_id: string
  action: 'created' | 'updated' | 'deleted'
}
```

#### 4. Test Messages
```typescript
interface TestMessageData {
  message: string
}
```

### Message Routing

Messages are automatically routed to subscribed handlers based on the `type` field:

```typescript
// Store processes incoming messages
const handleMessage = (event: MessageEvent) => {
  try {
    const message: WebSocketMessage = JSON.parse(event.data)
    const handlers = subscriptions.get(message.type)
    
    handlers?.forEach(handler => {
      try {
        handler(message)
      } catch (error) {
        console.error(`Handler error for ${message.type}:`, error)
      }
    })
  } catch (error) {
    console.error('Message parsing error:', error)
  }
}
```

## Error Handling & Reconnection

### Reconnection Strategy

```typescript
const reconnect = () => {
  if (connectionAttempts >= maxAttempts) {
    console.error('Max reconnection attempts reached')
    return
  }
  
  const delay = Math.min(1000 * Math.pow(2, connectionAttempts), 30000)
  setTimeout(() => {
    connectionAttempts++
    connect(lastUrl)
  }, delay)
}
```

**Characteristics:**
- **Exponential Backoff**: Doubles delay after each attempt
- **Max Delay**: Capped at 30 seconds
- **Max Attempts**: Limited to 5 attempts
- **Automatic Retry**: Triggered on connection loss

### Error Types & Handling

#### 1. Connection Errors
- **Initial Connection Failures**: Retry with exponential backoff
- **Network Disconnections**: Automatic reconnection attempts
- **Server Unavailable**: User notification with retry option

#### 2. Message Processing Errors
- **JSON Parse Errors**: Log error, continue processing other messages
- **Handler Exceptions**: Isolate errors, don't affect other handlers
- **Unknown Message Types**: Log warning, ignore message

#### 3. User Experience During Errors
- **Connection Status**: Visual indicator in UI
- **Fallback Behavior**: Application remains functional without WebSocket
- **Error Notifications**: Toast notifications for critical failures

### Error Recovery Patterns

```typescript
// Graceful degradation example in CommentsSection
const handleCreateComment = async (content: string) => {
  try {
    const response = await createComment(postId, content)
    
    // If WebSocket is disconnected, show the comment immediately
    if (!isConnected) {
      setComments(prev => [response.comment, ...prev])
      toast.success('Comment added (offline mode)')
    }
    // Otherwise, wait for WebSocket update
    
  } catch (error) {
    toast.error('Failed to create comment')
  }
}
```

## Testing Strategy

### Unit Tests

#### 1. WebSocket Store Tests
```typescript
// Test subscription system
it('should handle multiple subscriptions', () => {
  const handler1 = vi.fn()
  const handler2 = vi.fn()
  
  const unsubscribe1 = store.subscribe('test', handler1)
  const unsubscribe2 = store.subscribe('test', handler2)
  
  // Simulate message
  store.handleMessage({ type: 'test', data: {} })
  
  expect(handler1).toHaveBeenCalled()
  expect(handler2).toHaveBeenCalled()
})
```

#### 2. Hook Tests
```typescript
// Test automatic connection
it('should connect on mount', () => {
  const mockConnect = vi.fn()
  useWebSocketStore.setState({ connect: mockConnect })
  
  renderHook(() => useWebSocketManager())
  
  expect(mockConnect).toHaveBeenCalledWith('ws://localhost:3001')
})
```

### Integration Tests

#### 1. Component Integration
```typescript
// Test comment real-time updates
it('should update comments on WebSocket message', async () => {
  render(<CommentsSection postId="test-post" />)
  
  // Simulate WebSocket message
  const message = {
    type: 'comment.created',
    data: {
      postId: 'test-post',
      comment: { id: '1', content: 'Test comment' }
    }
  }
  
  act(() => {
    useWebSocketStore.getState().handleMessage(message)
  })
  
  expect(screen.getByText('Test comment')).toBeInTheDocument()
})
```

#### 2. E2E Tests
```typescript
// Test real-time comment flow
test('real-time comment updates', async ({ page }) => {
  await page.goto('/posts/test-post')
  
  // Create comment in one tab
  await page.fill('[data-testid="comment-input"]', 'Test comment')
  await page.click('[data-testid="submit-comment"]')
  
  // Verify WebSocket update
  await page.waitForSelector('text=Test comment')
  
  // Verify toast notification
  await page.waitForSelector('text=New comment added!')
})
```

### Testing WebSocket Connection
```typescript
// Mock WebSocket for testing
const mockWebSocket = {
  send: vi.fn(),
  close: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn()
}

global.WebSocket = vi.fn(() => mockWebSocket)
```

This comprehensive frontend integration provides a robust, testable, and user-friendly real-time communication system that gracefully handles both connected and disconnected states.