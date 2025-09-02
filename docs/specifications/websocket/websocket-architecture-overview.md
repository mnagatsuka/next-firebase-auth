# WebSocket Architecture Overview

## Table of Contents
- [Overview](#overview)
- [Architecture Diagram](#architecture-diagram)
- [System Components](#system-components)
- [Message Flow](#message-flow)
- [Implementation Details](#implementation-details)
- [Environment Configuration](#environment-configuration)
- [Deployment Architecture](#deployment-architecture)

## Overview

This project implements a real-time WebSocket communication system for instant comment updates and notifications. The architecture follows a **hybrid approach** combining REST APIs for data operations with WebSocket for real-time notifications.

**Key Characteristics:**
- **Unidirectional WebSocket Communication**: Server-to-client only
- **REST + WebSocket Hybrid**: Data operations via REST, notifications via WebSocket
- **AWS Serverless Infrastructure**: API Gateway WebSocket + Lambda functions
- **Scalable Connection Management**: DynamoDB for connection state
- **Development-friendly**: LocalStack + Serverless Framework support

## Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend (Next.js)"
        A[CommentsSection Component]
        B[WebSocket Store (Zustand)]
        C[useWebSocketManager Hook]
        D[RealtimeNotifications]
    end
    
    subgraph "Backend (FastAPI)"
        E[Comments API Endpoint]
        F[WebSocket Service]
        G[Dependencies]
    end
    
    subgraph "AWS Infrastructure"
        H[API Gateway WebSocket]
        I[Lambda Functions]
        J[DynamoDB Connections]
        K[HTTP Broadcast Endpoint]
    end
    
    A --> B
    B --> C
    C --> H
    D --> C
    
    E --> F
    F --> K
    K --> I
    I --> H
    I --> J
    
    H --> C
```

## System Components

### Frontend Components

#### 1. WebSocket Store (`websocket.ts`)
- **Purpose**: Centralized WebSocket state management using Zustand
- **Features**: 
  - Connection management with automatic reconnection
  - Message subscription system with type-based routing
  - Exponential backoff (max 5 attempts, 3-second intervals)
  - Multiple subscribers per message type

#### 2. WebSocket Hooks
- **`useWebSocket.ts`**: Basic WebSocket connection with reconnection logic
- **`useWebSocketManager.ts`**: Global WebSocket manager integration
- **`useCommentsWebSocket.ts`**: Comment-specific WebSocket handling

#### 3. React Components
- **`CommentsSection.tsx`**: Real-time comment updates in UI
- **`RealtimeNotifications.tsx`**: Global toast notification system

### Backend Components

#### 1. WebSocket Service (`apigateway_websocket_service.py`)
- **Purpose**: HTTP client for triggering WebSocket broadcasts
- **Key Methods**:
  - `broadcast_to_all()` - Generic message broadcasting
  - `broadcast_new_comment()` - Comment creation notifications
  - `broadcast_comments_list()` - Comments list updates
  - `broadcast_comment_update()` - Comment modification events

#### 2. API Routes (`websocket.py`)
- **POST `/websocket/connect`** - Connection event handler
- **POST `/websocket/disconnect`** - Disconnection event handler  
- **GET `/websocket/connections`** - Health check and connection count

#### 3. Comments Integration
- WebSocket broadcasting integrated into comment creation flow
- Returns acknowledgment responses while sending data via WebSocket

### Infrastructure Components

#### 1. AWS API Gateway WebSocket
- **Routes**: `$connect`, `$disconnect`, `$default`
- **Connection Management**: Stores connection IDs in DynamoDB
- **Broadcast Pattern**: HTTP endpoint triggers Lambda function

#### 2. Lambda Functions
- **Connect Handler**: Manages new WebSocket connections
- **Disconnect Handler**: Cleans up closed connections
- **Broadcast Handler**: Sends messages to all connected clients
- **Default Handler**: Echo functionality for testing

#### 3. DynamoDB Tables
- **`websocket-connections`**: Active connection storage with TTL
- **Connection TTL**: 24-hour automatic cleanup

## Message Flow

### 1. Comment Creation Flow
```
1. User creates comment → POST /api/v1/posts/{id}/comments
2. FastAPI processes comment → Saves to DynamoDB  
3. FastAPI calls WebSocket service → HTTP POST to broadcast endpoint
4. Lambda function retrieves connections → Scans DynamoDB connections table
5. Lambda broadcasts message → API Gateway WebSocket to all clients
6. Frontend receives message → Updates UI via WebSocket store
```

### 2. Connection Management Flow
```
1. Frontend connects → WebSocket connection to API Gateway
2. API Gateway triggers → Connect Lambda function
3. Lambda stores connection → DynamoDB with TTL
4. Client disconnect → Triggers disconnect Lambda
5. Lambda removes connection → Cleans up DynamoDB entry
```

## Implementation Details

### Message Types

#### 1. Comment Created
```json
{
  "type": "comment.created",
  "data": {
    "postId": "uuid",
    "comment": {
      "id": "uuid",
      "content": "string", 
      "userId": "string",
      "createdAt": "2024-01-01T00:00:00Z",
      "postId": "uuid"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 2. Comments List Update
```json
{
  "type": "comments.list",
  "data": {
    "postId": "uuid",
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

#### 3. Test Messages
```json
{
  "type": "test",
  "data": {
    "message": "Test message content"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Handling

#### Frontend Error Handling
- **Connection failures**: Automatic reconnection with exponential backoff
- **Message parsing errors**: Logged to console, continues processing
- **WebSocket errors**: Handled gracefully with reconnection attempts

#### Backend Error Handling  
- **HTTP broadcast failures**: Logged with error details
- **Connection cleanup**: Automatic removal of stale connections
- **DynamoDB errors**: Proper error responses and logging

## Environment Configuration

### Development Environment
```bash
# Frontend (.env.development)
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:3001

# Backend (.env.development)
APP_SERVERLESS_WEBSOCKET_ENDPOINT=http://localhost:3001
```

### Production Environment
```bash
# Frontend (Vercel environment variables)
NEXT_PUBLIC_WEBSOCKET_URL=wss://api-gateway-id.execute-api.ap-northeast-1.amazonaws.com/production

# Backend (AWS Lambda environment variables)
APP_SERVERLESS_WEBSOCKET_ENDPOINT=https://api-gateway-id.execute-api.ap-northeast-1.amazonaws.com/production
```

## Deployment Architecture

### Development Stack
- **LocalStack**: DynamoDB simulation
- **Serverless Offline**: WebSocket API simulation at `localhost:3001`  
- **Docker Compose**: Orchestration of development services

### Production Stack
- **AWS API Gateway**: WebSocket API endpoint
- **AWS Lambda**: Serverless compute for handlers
- **AWS DynamoDB**: Connection state management
- **AWS SAM**: Infrastructure as Code deployment

### Infrastructure as Code
- **`template.yml`**: AWS SAM template for complete infrastructure
- **`serverless.yml`**: Serverless Framework configuration for development
- **`docker-compose.yml`**: Local development orchestration

## Performance Characteristics

### Scalability
- **Connection Limits**: AWS API Gateway supports 100,000 concurrent connections per account
- **Message Rate**: Lambda concurrency controls broadcast throughput
- **Auto-scaling**: Automatic scaling based on connection and message volume

### Latency
- **Message Delivery**: Sub-second delivery for most messages
- **Connection Setup**: ~100-200ms for WebSocket handshake
- **Regional Deployment**: ap-northeast-1 (Tokyo) region

### Reliability
- **Connection Persistence**: Automatic reconnection on failures
- **Message Durability**: At-least-once delivery guarantee
- **Health Monitoring**: Connection count and health endpoints

This architecture provides a robust, scalable real-time communication system optimized for comment notifications and real-time updates.