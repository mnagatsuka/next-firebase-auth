# Infrastructure Architecture

This document describes the refactored AWS SAM infrastructure for the Next.js Firebase Auth project.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       CLIENT LAYER                              │
│  Next.js Frontend ←→ FastAPI Backend ←→ WebSocket Client       │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                       API LAYER                                 │
│  HTTP API Gateway v2 ←→ WebSocket API Gateway v2               │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                     COMPUTE LAYER                               │
│  FastAPI Lambda ←→ WebSocket Handlers (Connect/Disconnect/     │
│  (Python + LWA)    Default/Broadcast) - Node.js 20 + SDK v3   │
└─────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  DynamoDB Tables: Posts, Comments, Favorites, WS Connections   │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. **Data Layer - DynamoDB Tables**
- **PostsTable**: Blog posts storage
- **CommentsTable**: Comments on posts
- **FavoritesTable**: User favorites (composite key: user_id + post_id)
- **WebSocketConnectionsTable**: Active WebSocket connections with TTL

### 2. **API Layer - API Gateway v2**
- **HTTP API**: REST endpoints for the FastAPI backend
- **WebSocket API**: Real-time communication for comments
  - `$connect` → WebSocketConnectFunction
  - `$disconnect` → WebSocketDisconnectFunction  
  - `$default` → WebSocketDefaultFunction
- **Broadcasting**: HTTP endpoint `/broadcast/comments` → WebSocketBroadcastFunction

### 3. **Compute Layer - Lambda Functions**

#### FastAPI Backend (`BlogAPIFunction`)
- **Runtime**: Python 3.13 with Lambda Web Adapter
- **Purpose**: Main application logic, REST API endpoints
- **Integration**: HTTP API Gateway with `ANY /{proxy+}`

#### WebSocket Handlers (Node.js 20.x + AWS SDK v3)
- **WebSocketConnectFunction**: Manages new connections
- **WebSocketDisconnectFunction**: Cleans up disconnected clients
- **WebSocketDefaultFunction**: Handles incoming WebSocket messages (echo)
- **WebSocketBroadcastFunction**: HTTP-triggered broadcasting to all clients

### 4. **Shared Utilities Architecture**

```
websocket-handlers/
├── connect.ts          # Connection handler
├── disconnect.ts       # Disconnection handler
├── default.ts          # Message handler
├── broadcast.ts        # Broadcasting handler
├── shared/
│   ├── types.ts        # TypeScript interfaces
│   ├── clients.ts      # AWS SDK clients
│   ├── utils.ts        # Helper functions
│   └── broadcast-service.ts  # Broadcasting business logic
├── package.json        # Dependencies
└── tsconfig.json       # TypeScript configuration
```

## Key Improvements

### ✅ **Code Organization**
- **Shared utilities** eliminate code duplication
- **Consistent error handling** across all handlers
- **Type safety** with comprehensive TypeScript interfaces
- **Service layer** for complex business logic

### ✅ **Performance & Reliability**
- **Chunked broadcasting** prevents API throttling
- **Stale connection cleanup** with 410 error handling
- **Pagination** for large connection tables
- **Connection TTL** for automatic cleanup

### ✅ **Monitoring & Debugging**
- **Structured logging** with configurable log levels
- **Comprehensive error handling** with detailed responses
- **CloudWatch integration** with proper log groups
- **Request/response correlation** for debugging

### ✅ **Security & Best Practices**
- **Environment validation** for required variables
- **CORS configuration** per environment
- **IAM least privilege** with scoped permissions
- **Input validation** for all handler inputs

## Environment Configuration

### Required Environment Variables
```bash
# Core Configuration
AWS_REGION=ap-northeast-1
ENVIRONMENT=development|staging|production

# DynamoDB Configuration  
DYNAMODB_CONNECTIONS_TABLE=stack-name-websocket-connections
DYNAMODB_ENDPOINT=http://localhost:4566  # LocalStack only

# WebSocket Configuration
WEBSOCKET_API_ENDPOINT=https://api-id.execute-api.region.amazonaws.com/stage

# Application Configuration
LOG_LEVEL=DEBUG|INFO|WARN|ERROR
CORS_ORIGIN=http://localhost:3000
FIREBASE_PROJECT_ID=your-project-id
```

## Deployment

### Development
```bash
# Build WebSocket handlers
./build-websocket-handlers.sh

# Deploy with development parameters
sam build
sam deploy --config-file samconfig.toml --config-env development
```

### Production
```bash
# Deploy with production parameters  
sam deploy --config-file samconfig.toml --config-env production --parameter-overrides Environment=production
```

## Cost Optimization

- **DynamoDB**: Pay-per-request billing, PITR disabled
- **Lambda**: Right-sized memory allocation, efficient runtimes
- **API Gateway**: Auto-scaling with usage-based pricing
- **CloudWatch**: Environment-specific log retention (7d development, 30d production)

## Testing Strategy

### Unit Testing
- WebSocket handler functions
- Shared utility functions  
- Error handling scenarios

### Integration Testing
- End-to-end WebSocket communication
- Broadcasting to multiple connections
- Stale connection cleanup

### Load Testing
- High-volume connection handling
- Broadcasting performance under load
- Database performance with large datasets
