# Comments API WebSocket Migration Procedure (API Gateway)

## Overview

This procedure outlines the steps to modify **only the GET comments API** to use **API Gateway WebSocket** for response delivery. The client makes direct REST requests to FastAPI, but responses are delivered via AWS API Gateway WebSocket.

## Architecture

### Request/Response Flow
```
Client REST Request → FastAPI Backend → Process Comments → API Gateway WebSocket → Client
     (Direct)                                                  (Response)
```

### Key Components
- **Client**: Makes direct REST requests to FastAPI (no API Gateway)
- **FastAPI**: Processes requests, sends responses via API Gateway WebSocket
- **API Gateway**: WebSocket endpoint for delivering responses to clients
- **POST comments**: Keep existing REST request/response pattern
- **GET comments**: REST request, API Gateway WebSocket response

## Migration Strategy

### Response Flow for GET Comments Only
```
Client GET Request → FastAPI Endpoint → Process → API Gateway WebSocket Response
     (Direct)                                           ↓
Client ← API Gateway WebSocket ← Lambda Function ← FastAPI Backend
```

## Implementation Steps

### Step 1: Set Up API Gateway WebSocket

**Production**: AWS API Gateway WebSocket API
**Development**: LocalStack API Gateway WebSocket

Create API Gateway WebSocket API with routes:
- `$connect` - Handle client connections
- `$disconnect` - Handle client disconnections

### Step 2: Update Backend Dependencies

Add API Gateway WebSocket client to FastAPI:

```python
# backend/src/app/shared/config.py
from typing import Optional

class Settings:
    # ... existing settings ...
    
    # API Gateway WebSocket settings
    AWS_REGION: str = "us-east-1"
    LOCALSTACK_ENDPOINT: Optional[str] = "http://localhost:4566"  # LocalStack
    API_GATEWAY_WEBSOCKET_URL: str = ""  # Set based on environment
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    def __post_init__(self):
        # Set WebSocket URL based on environment
        if self.LOCALSTACK_ENDPOINT:
            # LocalStack development
            self.API_GATEWAY_WEBSOCKET_URL = f"{self.LOCALSTACK_ENDPOINT}/restapis/your-api-id/dev/_user_request_"
        else:
            # AWS production
            self.API_GATEWAY_WEBSOCKET_URL = "https://your-api-id.execute-api.us-east-1.amazonaws.com/dev"

settings = Settings()
```

```python
# backend/src/app/application/services/apigateway_websocket_service.py
import json
import boto3
from typing import List, Dict, Any
from datetime import datetime
from app.shared.config import settings
import logging
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class ApiGatewayWebSocketService:
    def __init__(self):
        # Initialize API Gateway Management API client
        endpoint_url = settings.LOCALSTACK_ENDPOINT if settings.LOCALSTACK_ENDPOINT else None
        
        self.apigateway_client = boto3.client(
            'apigatewaymanagementapi',
            region_name=settings.AWS_REGION,
            endpoint_url=f"{settings.API_GATEWAY_WEBSOCKET_URL}" if endpoint_url else None,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or "test",  # LocalStack
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or "test"  # LocalStack
        )
        
        # Store active connections (in production, use DynamoDB)
        self.connections = set()
    
    async def add_connection(self, connection_id: str):
        """Add a WebSocket connection"""
        self.connections.add(connection_id)
        logger.info(f"Added connection: {connection_id}")
    
    async def remove_connection(self, connection_id: str):
        """Remove a WebSocket connection"""
        self.connections.discard(connection_id)
        logger.info(f"Removed connection: {connection_id}")
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Send message to all connected clients via API Gateway WebSocket"""
        if not self.connections:
            logger.info("No active connections to broadcast to")
            return
        
        message_data = json.dumps(message)
        disconnected = set()
        
        for connection_id in self.connections:
            try:
                self.apigateway_client.post_to_connection(
                    ConnectionId=connection_id,
                    Data=message_data
                )
                logger.info(f"Sent message to connection: {connection_id}")
            except self.apigateway_client.exceptions.GoneException:
                # Connection is stale, mark for removal
                disconnected.add(connection_id)
                logger.info(f"Connection gone: {connection_id}")
            except Exception as e:
                logger.error(f"Error sending to connection {connection_id}: {e}")
                disconnected.add(connection_id)
        
        # Clean up disconnected clients
        self.connections -= disconnected
    
    async def broadcast_comments_list(self, post_id: str, comments: List[Dict[str, Any]]):
        """Broadcast comments list to all clients via API Gateway WebSocket"""
        message = {
            "type": "comments_list",
            "data": {
                "post_id": post_id,
                "comments": comments,
                "count": len(comments)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_all(message)

# Global instance
apigateway_websocket_service = ApiGatewayWebSocketService()
```

```python
# backend/src/app/shared/dependencies.py
from app.application.services.apigateway_websocket_service import apigateway_websocket_service

def get_apigateway_websocket_service():
    return apigateway_websocket_service
```

### Step 3: Modify ONLY the GET Comments Endpoint

**POST endpoint remains unchanged** - keep existing REST response pattern.

**GET endpoint modification**:

```python
# backend/src/app/api/routes/comments.py
from app.shared.dependencies import get_apigateway_websocket_service

@comments_router.get("/{id}/comments")
async def get_post_comments(
    id: str,
    limit: int = 10,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional),
    comment_service: CommentApplicationService = Depends(get_comment_application_service),
    websocket_service = Depends(get_apigateway_websocket_service)  # NEW - API Gateway WebSocket
) -> dict:  # Changed return type
    """Get comments for a post. Returns acknowledgment, sends data via API Gateway WebSocket."""
    try:
        comments_data = await comment_service.get_comments_by_post(
            post_id=id,
            limit=limit
        )
        
        comments = []
        for comment_data in comments_data:
            comments.append(Comment(
                id=comment_data["id"],
                content=comment_data["content"],
                userId=comment_data["userId"],
                createdAt=comment_data["createdAt"],
                postId=comment_data["postId"]
            ).model_dump())
        
        # Send response via API Gateway WebSocket
        await websocket_service.broadcast_comments_list(id, comments)
        
        # Return simple acknowledgment
        return {
            "status": "success",
            "message": "Comments retrieved successfully",
            "count": len(comments)
        }
        
    except (PostNotFoundError, NotFoundError):
        raise HTTPException(status_code=404, detail="Post not found")
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**POST endpoint keeps existing code** - no changes needed.

### Step 4: LocalStack Development Setup

Configure LocalStack for local API Gateway WebSocket development:

```yaml
# docker-compose.yml - Add LocalStack service
services:
  localstack:
    container_name: localstack
    image: localstack/localstack:latest
    ports:
      - "127.0.0.1:4566:4566"
      - "127.0.0.1:4510-4559:4510-4559"
    environment:
      - SERVICES=apigateway,dynamodb
      - DEBUG=1
      - DATA_DIR=/var/lib/localstack/data
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "./localstack:/var/lib/localstack"
      - "/var/run/docker.sock:/var/run/docker.sock"

  backend:
    # ... existing backend config
    depends_on:
      - localstack
    environment:
      - LOCALSTACK_ENDPOINT=http://localstack:4566
```

```bash
# scripts/setup-localstack-websocket.sh
#!/bin/bash

# Create API Gateway WebSocket API in LocalStack
awslocal apigatewayv2 create-api \
  --name comments-websocket \
  --protocol-type WEBSOCKET \
  --route-selection-expression '$request.body.action'

# Get the API ID
API_ID=$(awslocal apigatewayv2 get-apis | jq -r '.Items[0].ApiId')

# Create routes
awslocal apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key '$connect'

awslocal apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key '$disconnect'

# Create deployment
awslocal apigatewayv2 create-deployment \
  --api-id $API_ID \
  --stage-name dev

echo "API Gateway WebSocket API ID: $API_ID"
```

### Step 5: Update Frontend WebSocket Handler

Connect to API Gateway WebSocket and handle comments list messages:

```typescript
// frontend/src/components/common/RealtimeNotifications.tsx
export function RealtimeNotifications() {
  const { disconnect } = useWebSocket({
    url: process.env.NODE_ENV === 'development' 
      ? 'ws://localhost:4566'  // LocalStack API Gateway WebSocket
      : 'wss://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/dev',  // AWS API Gateway
    
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
        // ... existing cases
      }
    }
  })

  const handleCommentsList = (data: any) => {
    // Update comments list in UI from API Gateway WebSocket response
    // This could integrate with Zustand store or trigger re-renders
  }

  return null
}
```

### Step 6: Create Comments WebSocket Hook for API Gateway

```typescript
// frontend/src/hooks/useCommentsWebSocket.ts
'use client'

import { useWebSocket, WebSocketMessage } from './useWebSocket'
import { useCallback } from 'react'

export interface Comment {
  id: string
  content: string
  userId: string
  createdAt: string
  postId: string
}

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
      ? 'ws://localhost:4566'  // LocalStack API Gateway
      : 'wss://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/dev',  // AWS API Gateway
    onMessage: handleMessage
  })

  return { disconnect }
}
```

### Step 7: Update API Client

Modify only the GET comments API call:

```typescript
// frontend/src/lib/api/comments.ts

// POST remains unchanged - still returns full Comment object
export async function createComment(postId: string, content: string): Promise<Comment> {
  const response = await customFetch(`/api/v1/posts/${postId}/comments`, {
    method: 'POST',
    body: JSON.stringify({ content }),
    headers: { 'Content-Type': 'application/json' }
  })
  
  // Still returns full Comment object
  return await response.json()
}

// GET modified - returns acknowledgment, data comes via API Gateway WebSocket
export async function getComments(postId: string, limit = 10) {
  const response = await customFetch(`/api/v1/posts/${postId}/comments?limit=${limit}`)
  
  // Now returns acknowledgment, actual data delivered via API Gateway WebSocket
  const result = await response.json()
  return {
    status: result.status,
    message: result.message,
    count: result.count
  }
}
```

## WebSocket Message Formats

### Comments List Message (GET only)
```json
{
  "type": "comments_list", 
  "data": {
    "post_id": "uuid",
    "comments": [
      {
        "id": "uuid",
        "content": "string",
        "userId": "string",
        "createdAt": "2024-01-01T00:00:00Z", 
        "postId": "uuid"
      }
    ],
    "count": 5
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Testing Strategy

### Backend Tests
1. Test GET endpoint returns acknowledgment
2. Test WebSocket broadcast is sent for GET requests
3. Test POST endpoint still returns Comment object (unchanged)
4. Integration tests for WebSocket + REST flow

### Frontend Tests  
1. Test GET API call handles acknowledgment response
2. Test POST API call still handles Comment response  
3. Test WebSocket message handling for comments list
4. Test UI updates from WebSocket messages

## Migration Checklist

### Backend Changes
- [ ] Add API Gateway WebSocket service to FastAPI
- [ ] Configure LocalStack for development environment  
- [ ] Modify GET comments endpoint to return acknowledgment + send via API Gateway
- [ ] Keep POST comments endpoint unchanged
- [ ] Add ApiGatewayWebSocketService.broadcast_comments_list method
- [ ] Update tests for GET endpoint response format
- [ ] Test API Gateway WebSocket broadcasting functionality

### Frontend Changes
- [ ] Create useCommentsWebSocket hook connecting to API Gateway (GET only)
- [ ] Update RealtimeNotifications component for API Gateway WebSocket messages
- [ ] Modify GET comments API client function for acknowledgment responses
- [ ] Keep POST comments API client function unchanged  
- [ ] Update comment components to handle API Gateway WebSocket updates for GET
- [ ] Add error handling for API Gateway WebSocket failures
- [ ] Update tests for new GET API response format

### Infrastructure
- [ ] Set up LocalStack API Gateway WebSocket for development
- [ ] Deploy AWS API Gateway WebSocket for production
- [ ] Configure connection management (DynamoDB for production)
- [ ] Update API documentation for GET endpoint only
- [ ] Test end-to-end flow with LocalStack and AWS
- [ ] Performance testing with multiple clients via API Gateway

## Benefits

1. **Real-time Comments Loading**: All clients receive comments via API Gateway WebSocket instantly
2. **Simplified Migration**: Only GET endpoint changes, POST remains stable
3. **AWS Integration**: Uses managed API Gateway WebSocket service
4. **LocalStack Development**: Full local development with LocalStack
5. **Scalability**: API Gateway handles WebSocket connections and scaling
6. **User Experience**: Instant comments display for all users when someone loads them
7. **Backward Compatibility**: POST requests unchanged for API consumers
8. **Progressive Enhancement**: API Gateway WebSocket enhances GET requests only