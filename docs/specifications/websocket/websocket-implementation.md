# WebSocket Implementation Specification

Target: **FastAPI Backend + Next.js Frontend (Local Development)**
Purpose: Enable real-time communication for receive-only client scenarios.

## Overview

This project implements WebSocket communication where:
- **FastAPI backend** sends real-time updates via WebSocket
- **Next.js frontend** receives messages (no client-to-server messaging)
- **Local development** environment with Docker Compose support

## Architecture

```
┌─────────────────┐    WebSocket     ┌──────────────────┐
│   Next.js       │ ◄──────────────── │   FastAPI        │
│   Frontend      │                  │   Backend        │
│   (Client)      │                  │   (Server)       │
└─────────────────┘                  └──────────────────┘
```

### Communication Pattern
- **Unidirectional**: Backend → Frontend only
- **Real-time**: Instant message delivery
- **Event-driven**: Backend sends updates based on application events

## Backend Implementation (FastAPI)

### Dependencies
```python
# infrastructure/aws-sam/requirements.txt
fastapi[all]>=0.104.0
websockets>=12.0
```

### WebSocket Endpoint
```python
# src/app/api/routes/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
        
        disconnected = set()
        message_str = json.dumps(message)
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        self.active_connections -= disconnected

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive (client doesn't send messages)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
```

### Message Broadcasting Service
```python
# src/app/application/services/websocket_service.py
from app.api.routes.websocket import manager
import asyncio
from typing import Any, Dict

class WebSocketService:
    @staticmethod
    async def broadcast_notification(message_type: str, data: Any):
        """Broadcast notification to all connected clients"""
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast(message)

    @staticmethod
    async def broadcast_blog_update(post_id: str, action: str):
        """Broadcast blog post updates"""
        await WebSocketService.broadcast_notification(
            "blog_update",
            {"post_id": post_id, "action": action}
        )

    @staticmethod
    async def broadcast_comment_update(post_id: str, comment_id: str, action: str):
        """Broadcast comment updates"""
        await WebSocketService.broadcast_notification(
            "comment_update",
            {"post_id": post_id, "comment_id": comment_id, "action": action}
        )
```

### Integration with Main App
```python
# src/app/main.py
from app.api.routes import websocket

app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])
```

## Frontend Implementation (Next.js)

### WebSocket Hook
```typescript
// src/hooks/useWebSocket.ts
'use client'

import { useEffect, useRef, useCallback } from 'react'

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

export interface UseWebSocketOptions {
  url: string
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
  reconnectAttempts?: number
  reconnectInterval?: number
}

export function useWebSocket({
  url,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
  reconnectAttempts = 5,
  reconnectInterval = 3000
}: UseWebSocketOptions) {
  const ws = useRef<WebSocket | null>(null)
  const reconnectCount = useRef(0)
  const reconnectTimeout = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(url)

      ws.current.onopen = () => {
        console.log('WebSocket connected')
        reconnectCount.current = 0
        onConnect?.()
      }

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          onMessage?.(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.current.onclose = () => {
        console.log('WebSocket disconnected')
        onDisconnect?.()
        
        // Attempt reconnection
        if (reconnectCount.current < reconnectAttempts) {
          reconnectCount.current++
          console.log(`Attempting reconnection ${reconnectCount.current}/${reconnectAttempts}`)
          reconnectTimeout.current = setTimeout(connect, reconnectInterval)
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        onError?.(error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }, [url, onMessage, onConnect, onDisconnect, onError, reconnectAttempts, reconnectInterval])

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current)
    }
    if (ws.current) {
      ws.current.close()
      ws.current = null
    }
  }, [])

  useEffect(() => {
    connect()
    return disconnect
  }, [connect, disconnect])

  return { disconnect }
}
```

### Real-time Notifications Component
```typescript
// src/components/common/RealtimeNotifications.tsx
'use client'

import { useWebSocket } from '@/hooks/useWebSocket'
import { toast } from 'sonner'

export function RealtimeNotifications() {
  const { disconnect } = useWebSocket({
    url: process.env.NODE_ENV === 'development' 
      ? 'ws://localhost:8000/api/v1/ws'
      : 'wss://your-api-domain.com/api/v1/ws',
    
    onMessage: (message) => {
      switch (message.type) {
        case 'blog_update':
          toast.info(`Blog post ${message.data.action}: ${message.data.post_id}`)
          break
        case 'comment_update':
          toast.info(`New comment on post ${message.data.post_id}`)
          break
        default:
          console.log('Unknown message type:', message.type)
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

  return null // This component only handles background WebSocket connection
}
```

### Layout Integration
```typescript
// src/app/layout.tsx
import { RealtimeNotifications } from '@/components/common/RealtimeNotifications'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <RealtimeNotifications />
      </body>
    </html>
  )
}
```

## Local Development Configuration

### Docker Compose Updates
```yaml
# docker-compose.yml
services:
  backend:
    # ... existing configuration
    ports:
      - "8000:8000"
    environment:
      - WEBSOCKET_ENABLED=true
```

### Environment Variables
```bash
# .env.development (Frontend)
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/ws

# .env (Backend)
WEBSOCKET_ENABLED=true
```

## Message Types

### Blog Updates
```json
{
  "type": "blog_update",
  "data": {
    "post_id": "uuid",
    "action": "created|updated|deleted"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Comment Updates
```json
{
  "type": "comment_update",
  "data": {
    "post_id": "uuid",
    "comment_id": "uuid",
    "action": "created|updated|deleted"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### System Notifications
```json
{
  "type": "system_notification",
  "data": {
    "message": "string",
    "level": "info|warning|error"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Testing

### Backend WebSocket Test
```python
# tests/backend/integration/test_websocket.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_websocket_connection():
    with TestClient(app) as client:
        with client.websocket_connect("/api/v1/ws") as websocket:
            # Test successful connection
            assert websocket
```

### Frontend WebSocket Test
```typescript
// frontend/tests/hooks/useWebSocket.test.ts
import { renderHook } from '@testing-library/react'
import { useWebSocket } from '@/hooks/useWebSocket'

// Mock WebSocket for testing
global.WebSocket = jest.fn()

test('useWebSocket connects successfully', () => {
  const { result } = renderHook(() => 
    useWebSocket({
      url: 'ws://localhost:8000/api/v1/ws'
    })
  )
  
  expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:8000/api/v1/ws')
})
```

## Production Considerations

### API Gateway Integration (AWS)
- Use AWS API Gateway WebSocket API
- Configure route selection expressions
- Handle connection/disconnection in Lambda functions

### Scaling
- Use Redis for message broadcasting across multiple backend instances
- Implement connection state management for high availability

### Security
- Add authentication for WebSocket connections
- Implement rate limiting for connection attempts
- Validate message formats and origins

## Implementation Checklist

### Backend
- [ ] Add WebSocket dependencies
- [ ] Implement connection manager
- [ ] Create WebSocket endpoint
- [ ] Add message broadcasting service
- [ ] Integrate with existing services
- [ ] Add WebSocket tests

### Frontend
- [ ] Create WebSocket custom hook
- [ ] Implement reconnection logic
- [ ] Add real-time notifications component
- [ ] Integrate with layout
- [ ] Add error handling
- [ ] Add WebSocket tests

### Infrastructure
- [ ] Update Docker Compose configuration
- [ ] Configure environment variables
- [ ] Test local development setup
- [ ] Document deployment processl