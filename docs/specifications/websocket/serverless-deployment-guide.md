# Serverless Framework WebSocket Deployment Guide

This document provides a comprehensive guide for migrating from LocalStack to Serverless Framework WebSocket implementation and deploying the complete solution with TypeScript.

## Migration Overview

**Current State**: FastAPI backend attempting to use LocalStack API Gateway V2 (requires Pro)
**Target State**: FastAPI backend communicating with Serverless Framework WebSocket API using TypeScript

Since LocalStack Free Plan doesn't support API Gateway V2 WebSocket APIs, we migrate to Serverless Framework with serverless-offline plugin for local development while maintaining AWS production compatibility.

## Architecture

```
┌─────────────────┐    REST     ┌─────────────────┐    WebSocket    ┌─────────────────┐
│                 │   Request   │                 │   Response      │                 │
│   Frontend      │────────────▶│   FastAPI       │────────────────▶│  Serverless     │
│   (React)       │             │   Backend       │                 │  WebSocket API  │
│                 │◀────────────│                 │◀────────────────│                 │
└─────────────────┘  Acknowledge └─────────────────┘   Broadcast     └─────────────────┘
```

### Request Flow
1. **POST Comment**: Frontend → FastAPI → DynamoDB (REST response)
2. **GET Comments**: Frontend → FastAPI → Serverless WebSocket broadcast → Frontend (WebSocket response)

## Migration Steps from Current Codebase

### Step 1: Update Environment Variables

**Backend `.env.development`** - Add Serverless WebSocket endpoint:
```bash
# ADD: Serverless WebSocket Configuration
APP_SERVERLESS_WEBSOCKET_ENDPOINT="http://localhost:3001"

# KEEP: LocalStack for DynamoDB (working and free)
APP_AWS_ENDPOINT_URL="http://localstack:4566"
APP_AWS_REGION="ap-northeast-1"
APP_AWS_ACCESS_KEY_ID="test" 
APP_AWS_SECRET_ACCESS_KEY="test"

```

**Frontend `.env.development`** - Update WebSocket URL:
```bash
# UPDATE: Point to Serverless WebSocket
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:3001

# KEEP: All other existing configurations unchanged
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
# ... rest of configuration remains the same
```

### Step 2: Update FastAPI Backend Configuration

**A. Add to `backend/src/app/shared/config.py`**:
```python
# ADD: Serverless WebSocket Configuration
SERVERLESS_WEBSOCKET_ENDPOINT: str = Field(
    default="http://localhost:3001",
    description="Serverless WebSocket API endpoint"
)
```

**B. Update `backend/src/app/application/services/apigateway_websocket_service.py`**:

Replace AWS SDK approach with HTTP requests to Serverless endpoint:

```python
"""API Gateway WebSocket service for broadcasting via Serverless Framework."""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from datetime import datetime, timezone

from app.shared.config import settings


class ApiGatewayWebSocketService:
    """Service for broadcasting messages via Serverless WebSocket API."""
    
    def __init__(self):
        self.serverless_endpoint = settings.SERVERLESS_WEBSOCKET_ENDPOINT
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for Serverless API calls."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected WebSocket clients via Serverless."""
        try:
            session = await self._get_session()
            
            async with session.post(
                f"{self.serverless_endpoint}/development/broadcast/comments",
                json=message,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Broadcast successful: {result.get('connectionCount', 0)} connections")
                else:
                    error_text = await response.text()
                    print(f"❌ Broadcast failed: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Broadcast error: {str(e)}")
    
    async def broadcast_comments_list(self, post_id: str, comments: List[Dict[str, Any]]) -> None:
        """Broadcast comments list for a specific post."""
        message = {
            "type": "comments_list", 
            "data": {
                "post_id": post_id,
                "comments": comments,
                "count": len(comments)
            }
        }
        
        await self.broadcast_to_all(message)
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
```

**C. Add HTTP dependency to `backend/pyproject.toml`**:
```bash
cd backend/
uv add aiohttp
```

### Step 3: Update Docker Compose (Hybrid Approach)

**Recommended**: Keep LocalStack for DynamoDB + Add Serverless for WebSocket

Update `docker-compose.yml`:
```yaml
services:
  # KEEP: LocalStack for DynamoDB only (free and stable)
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    env_file:
      - ./backend/.env.development
    environment:
      - SERVICES=dynamodb  # REMOVE apigateway from services
      - DEBUG=1
      - PERSISTENCE=1
    volumes:
      - localstack-data:/var/lib/localstack
      - /var/run/docker.sock:/var/run/docker.sock
      - ./backend/scripts/localstack-init.sh:/etc/localstack/init/ready.d/init-aws.sh
    networks:
      - app-network

  # UPDATE: Backend to use both LocalStack and Serverless
  backend:
    # ... existing configuration
    environment:
      - APP_AWS_ENDPOINT_URL=http://localstack:4566  # DynamoDB via LocalStack
      - APP_SERVERLESS_WEBSOCKET_ENDPOINT=http://host.docker.internal:3001  # WebSocket via Serverless
    depends_on:
      - localstack

  # KEEP: Frontend configuration unchanged
  frontend:
    # ... existing configuration (no changes needed)

# Note: Serverless WebSocket runs outside Docker for easier development
```

### Step 4: Update LocalStack Init Script

Since we're removing API Gateway from LocalStack, update `backend/scripts/localstack-init.sh`:

**Remove WebSocket API Gateway initialization**, keep only DynamoDB tables:
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "[localstack-init] Initializing DynamoDB tables only..."

# Keep existing DynamoDB table creation functions
create_table_if_missing() { ... }  # Keep existing
create_table_composite_if_missing() { ... }  # Keep existing

# KEEP: Create DynamoDB tables
POSTS_TABLE=${APP_DYNAMODB_TABLE_POSTS:-posts}
COMMENTS_TABLE=${APP_DYNAMODB_TABLE_COMMENTS:-comments}
FAVORITES_TABLE=${APP_DYNAMODB_TABLE_FAVORITES:-favorites}

create_table_if_missing "$POSTS_TABLE" id
create_table_if_missing "$COMMENTS_TABLE" id  
create_table_composite_if_missing "$FAVORITES_TABLE" user_id post_id

# REMOVE: All API Gateway WebSocket initialization code
# No longer needed since using Serverless Framework

echo "[localstack-init] DynamoDB initialization complete."
```

### Step 5: Test Migration

**Development workflow order**:
```bash
# Terminal 1: Start LocalStack (DynamoDB only)
docker-compose up localstack

# Terminal 2: Start Serverless WebSocket service (after setup below)
cd infrastructure/serverless/
pnpm install && pnpm run dev

# Terminal 3: Start FastAPI Backend
cd backend/
uv run uvicorn app.main:app --reload

# Terminal 4: Start Frontend
cd frontend/
pnpm dev
```

**Verification checklist**:
- [ ] Frontend connects to `ws://localhost:3001` 
- [ ] Comments creation works via FastAPI REST API
- [ ] Comments updates broadcast via WebSocket
- [ ] DynamoDB operations work via LocalStack
- [ ] No API Gateway errors in logs

## Prerequisites

- Node.js 18+ 
- AWS CLI configured
- Serverless Framework CLI
- Python 3.11+ (for FastAPI backend)

## Installation

### 1. Install Serverless Framework

```bash
# Create and navigate to websocket service directory
mkdir websocket-service
cd websocket-service/

# Initialize pnpm project
pnpm init

# Install Serverless Framework locally (recommended for project consistency)
pnpm add --save-dev serverless serverless-offline

# Install runtime dependencies
pnpm add aws-sdk
```

### 2. Project Structure (Recommended)

```
project/
├── backend/                    # FastAPI application code only
│   ├── src/app/
│   ├── tests/
│   └── pyproject.toml
├── frontend/                   # Next.js application code only
│   ├── src/
│   ├── tests/
│   └── package.json
├── infrastructure/            # All infrastructure as code
│   ├── localstack/           # LocalStack development setup
│   │   ├── docker-compose.yml
│   │   └── scripts/
│   │       └── init-dynamodb.sh
│   ├── serverless/           # Serverless Framework WebSocket
│   │   ├── serverless.yml
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── src/handlers/
│   │   │   ├── connect.ts
│   │   │   ├── disconnect.ts
│   │   │   └── broadcast.ts
│   │   └── dist/             # Compiled JavaScript output
│   └── aws-sam/              # AWS SAM production deployment
│       ├── template.yaml
│       ├── lambda-handlers/
│       └── parameters/
│           ├── dev.json
│           ├── staging.json
│           └── prod.json
└── docs/
    ├── specifications/
    └── deployment/
```

**Benefits of this structure:**
- ✅ **Separation of concerns**: Application code vs Infrastructure code
- ✅ **Environment consistency**: All infrastructure in one place
- ✅ **Easier maintenance**: Single location for infrastructure changes
- ✅ **Better CI/CD**: Clear deployment boundaries
- ✅ **Team collaboration**: Infrastructure team can focus on `/infrastructure`
- ✅ **Technology flexibility**: Can switch between LocalStack/Serverless/SAM easily
- ✅ **Version control**: Infrastructure changes tracked separately
- ✅ **Security**: Infrastructure configurations isolated from application code

### Why Centralized Infrastructure?

1. **LocalStack Development**: `infrastructure/localstack/` contains all development setup
2. **Serverless WebSocket**: `infrastructure/serverless/` for local WebSocket development  
3. **AWS SAM Production**: `infrastructure/aws-sam/` for production deployment
4. **Clean Application Code**: `backend/` and `frontend/` focus only on business logic

### 3. Setup Commands Summary

```bash
# From project root - create infrastructure directory structure
mkdir -p infrastructure/serverless/src/handlers
mkdir -p infrastructure/localstack/scripts
mkdir -p infrastructure/aws-sam/lambda-handlers
mkdir -p infrastructure/aws-sam/parameters

# Setup Serverless WebSocket service with TypeScript
cd infrastructure/serverless/
pnpm init
pnpm add --save-dev serverless serverless-offline typescript @types/node @types/aws-lambda
pnpm add aws-sdk

# Move back to project root for other setup
cd ../../

# Create configuration files (see sections below)
# infrastructure/serverless/serverless.yml
# infrastructure/serverless/tsconfig.json
# infrastructure/serverless/src/handlers/*.ts
# infrastructure/localstack/docker-compose.yml
# infrastructure/aws-sam/template.yaml
```

## Serverless WebSocket Service Setup

### 1. Create Serverless Configuration

Create `infrastructure/serverless/serverless.yml`:

```yaml
service: comments-websocket-api

frameworkVersion: '3'

provider:
  name: aws
  runtime: nodejs18.x
  region: ap-northeast-1
  stage: ${opt:stage, 'development'}
  environment:
    WEBSOCKET_API_ENDPOINT: ${self:custom.websocketApiEndpoint.${self:provider.stage}}
    DYNAMODB_CONNECTIONS_TABLE: ${self:service}-${self:provider.stage}-connections
    CORS_ORIGIN: ${self:custom.corsOrigin.${self:provider.stage}}
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - execute-api:ManageConnections
          Resource: "*"
        - Effect: Allow
          Action:
            - dynamodb:PutItem
            - dynamodb:DeleteItem
            - dynamodb:Scan
          Resource:
            - arn:aws:dynamodb:${self:provider.region}:*:table/${self:provider.environment.DYNAMODB_CONNECTIONS_TABLE}

custom:
  websocketApiEndpoint:
    development: ws://localhost:3001
    staging: wss://${self:service}-${self:provider.stage}.execute-api.${self:provider.region}.amazonaws.com/${self:provider.stage}
    production: wss://${self:service}-${self:provider.stage}.execute-api.${self:provider.region}.amazonaws.com/${self:provider.stage}
  corsOrigin:
    development: http://localhost:3000
    staging: https://staging.yourdomain.com
    production: https://yourdomain.com
  serverless-offline:
    websocketPort: 3001
    httpsProtocol: false

plugins:
  - serverless-offline

functions:
  # WebSocket connection handlers
  connectHandler:
    handler: dist/handlers/connect.handler
    events:
      - websocket:
          route: $connect
  
  disconnectHandler:
    handler: dist/handlers/disconnect.handler
    events:
      - websocket:
          route: $disconnect
  
  defaultHandler:
    handler: dist/handlers/broadcast.handler
    events:
      - websocket:
          route: $default

  # HTTP endpoint for broadcasting from FastAPI
  broadcastComments:
    handler: dist/handlers/broadcast.broadcastToAll
    events:
      - http:
          path: broadcast/comments
          method: post
          cors:
            origin: ${self:custom.corsOrigin.${self:provider.stage}}
            headers:
              - Content-Type
              - Authorization

resources:
  Resources:
    ConnectionsTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:provider.environment.DYNAMODB_CONNECTIONS_TABLE}
        AttributeDefinitions:
          - AttributeName: connectionId
            AttributeType: S
        KeySchema:
          - AttributeName: connectionId
            KeyType: HASH
        BillingMode: PAY_PER_REQUEST
        TimeToLiveSpecification:
          AttributeName: ttl
          Enabled: true
```

### 2. TypeScript Configuration

Create `infrastructure/serverless/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", ".serverless"]
}
```

### 3. Connection Management

Create `infrastructure/serverless/src/handlers/connect.ts`:

```typescript
import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import * as AWS from 'aws-sdk';

const dynamodb = new AWS.DynamoDB.DocumentClient({
  region: process.env.AWS_REGION || 'ap-northeast-1',
  ...(process.env.IS_OFFLINE && {
    endpoint: 'http://localhost:4566',  // LocalStack DynamoDB endpoint
    accessKeyId: 'test',
    secretAccessKey: 'test'
  })
});

export const handler: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const connectionId = event.requestContext.connectionId;
  const tableName = process.env.DYNAMODB_CONNECTIONS_TABLE;

  if (!connectionId) {
    console.error('Missing connectionId in request context');
    return {
      statusCode: 400,
      body: JSON.stringify({ message: 'Missing connection ID' })
    };
  }

  if (!tableName) {
    console.error('Missing DYNAMODB_CONNECTIONS_TABLE environment variable');
    return {
      statusCode: 500,
      body: JSON.stringify({ message: 'Server configuration error' })
    };
  }

  try {
    await dynamodb.put({
      TableName: tableName,
      Item: {
        connectionId,
        timestamp: Date.now(),
        ttl: Math.floor(Date.now() / 1000) + 86400 // 24 hours TTL
      }
    }).promise();

    console.log(`Connection established: ${connectionId}`);
    
    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Connected' })
    };
  } catch (error) {
    console.error('Connection error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        message: 'Failed to connect',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    };
  }
};
```

Create `infrastructure/serverless/src/handlers/disconnect.ts`:

```typescript
import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import * as AWS from 'aws-sdk';

const dynamodb = new AWS.DynamoDB.DocumentClient({
  region: process.env.AWS_REGION || 'ap-northeast-1',
  ...(process.env.IS_OFFLINE && {
    endpoint: 'http://localhost:4566',  // LocalStack DynamoDB endpoint
    accessKeyId: 'test',
    secretAccessKey: 'test'
  })
});

export const handler: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const connectionId = event.requestContext.connectionId;
  const tableName = process.env.DYNAMODB_CONNECTIONS_TABLE;

  if (!connectionId) {
    console.error('Missing connectionId in request context');
    return {
      statusCode: 400,
      body: JSON.stringify({ message: 'Missing connection ID' })
    };
  }

  if (!tableName) {
    console.error('Missing DYNAMODB_CONNECTIONS_TABLE environment variable');
    return {
      statusCode: 500,
      body: JSON.stringify({ message: 'Server configuration error' })
    };
  }

  try {
    await dynamodb.delete({
      TableName: tableName,
      Key: { connectionId }
    }).promise();

    console.log(`Connection removed: ${connectionId}`);
    
    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Disconnected' })
    };
  } catch (error) {
    console.error('Disconnection error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        message: 'Failed to disconnect',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    };
  }
};
```

### 4. Broadcast Handler

Create `infrastructure/serverless/src/handlers/broadcast.ts`:

```typescript
import { APIGatewayProxyHandler, APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import * as AWS from 'aws-sdk';

// Type definitions
interface BroadcastRequestBody {
  type: string;
  data: {
    post_id: string;
    comments: Array<{
      id: string;
      content: string;
      user_id: string;
      created_at: string;
      post_id: string;
    }>;
    count: number;
  };
}

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

interface ConnectionItem {
  connectionId: string;
}

const dynamodb = new AWS.DynamoDB.DocumentClient({
  region: process.env.AWS_REGION || 'ap-northeast-1',
  ...(process.env.IS_OFFLINE && {
    endpoint: 'http://localhost:4566',  // LocalStack DynamoDB endpoint
    accessKeyId: 'test',
    secretAccessKey: 'test'
  })
});

const apiGateway = new AWS.ApiGatewayManagementApi({
  endpoint: process.env.WEBSOCKET_API_ENDPOINT || 'http://localhost:3001',
  ...(process.env.IS_OFFLINE && {
    accessKeyId: 'test',
    secretAccessKey: 'test'
  })
});

// Default WebSocket message handler
export const handler: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const connectionId = event.requestContext.connectionId;
  
  if (!connectionId) {
    console.error('Missing connectionId in request context');
    return {
      statusCode: 400,
      body: JSON.stringify({ message: 'Missing connection ID' })
    };
  }

  try {
    const message = JSON.parse(event.body || '{}');
    console.log(`Received message from ${connectionId}:`, message);
    
    // Echo back or handle specific message types
    const response: WebSocketMessage = {
      type: 'echo',
      data: { message: 'Message received' },
      timestamp: new Date().toISOString()
    };

    await apiGateway.postToConnection({
      ConnectionId: connectionId,
      Data: JSON.stringify(response)
    }).promise();

    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'Message processed' })
    };
  } catch (error) {
    console.error('Message handling error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        message: 'Failed to process message',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    };
  }
};

// HTTP endpoint for broadcasting from FastAPI
export const broadcastToAll: APIGatewayProxyHandler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const tableName = process.env.DYNAMODB_CONNECTIONS_TABLE;
  
  if (!tableName) {
    console.error('Missing DYNAMODB_CONNECTIONS_TABLE environment variable');
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': process.env.CORS_ORIGIN || '*'
      },
      body: JSON.stringify({ message: 'Server configuration error' })
    };
  }

  try {
    // Parse the broadcast request from FastAPI
    if (!event.body) {
      return {
        statusCode: 400,
        headers: {
          'Access-Control-Allow-Origin': process.env.CORS_ORIGIN || '*'
        },
        body: JSON.stringify({ message: 'Missing request body' })
      };
    }

    const requestBody: BroadcastRequestBody = JSON.parse(event.body);
    const { type, data } = requestBody;
    
    // Get all active connections
    const connections = await dynamodb.scan({
      TableName: tableName,
      ProjectionExpression: 'connectionId'
    }).promise();

    const message: WebSocketMessage = {
      type,
      data,
      timestamp: new Date().toISOString()
    };

    const messageData = JSON.stringify(message);

    // Broadcast to all connections
    const broadcastPromises = (connections.Items as ConnectionItem[] || []).map(async ({ connectionId }) => {
      try {
        await apiGateway.postToConnection({
          ConnectionId: connectionId,
          Data: messageData
        }).promise();
        
        console.log(`Message sent to connection: ${connectionId}`);
      } catch (error: any) {
        if (error.statusCode === 410) {
          // Connection is stale, remove it
          await dynamodb.delete({
            TableName: tableName,
            Key: { connectionId }
          }).promise();
          
          console.log(`Removed stale connection: ${connectionId}`);
        } else {
          console.error(`Failed to send to ${connectionId}:`, error);
        }
      }
    });

    await Promise.all(broadcastPromises);

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': process.env.CORS_ORIGIN || '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
      },
      body: JSON.stringify({
        message: 'Broadcast completed',
        connectionCount: connections.Items?.length || 0
      })
    };
  } catch (error) {
    console.error('Broadcast error:', error);
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': process.env.CORS_ORIGIN || '*'
      },
      body: JSON.stringify({ 
        message: 'Broadcast failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    };
  }
};
```

### 5. Package Configuration

Create `infrastructure/serverless/package.json`:

```json
{
  "name": "comments-websocket-api",
  "version": "1.0.0",
  "description": "WebSocket API for real-time comments",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "build:watch": "tsc --watch",
    "prebuild": "rm -rf dist",
    "predev": "pnpm run build",
    "dev": "pnpm exec serverless offline",
    "deploy": "pnpm run build && pnpm exec serverless deploy",
    "remove": "pnpm exec serverless remove", 
    "logs": "pnpm exec serverless logs -f broadcastComments --tail",
    "info": "pnpm exec serverless info",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage"
  },
  "dependencies": {
    "aws-sdk": "^2.1691.0"
  },
  "devDependencies": {
    "serverless": "^3.38.0",
    "serverless-offline": "^13.8.0",
    "typescript": "^5.3.0",
    "@types/node": "^20.0.0",
    "@types/aws-lambda": "^8.10.0",
    "vitest": "^1.0.0",
    "@vitest/ui": "^1.0.0"
  },
  "packageManager": "pnpm@9.0.0"
}
```

### 6. Vitest Configuration

Create `infrastructure/serverless/vitest.config.ts`:

```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.{test,spec}.{js,ts}'],
    clearMocks: true,
    restoreMocks: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{ts,js}'],
      exclude: ['**/*.d.ts', 'dist/**', 'tests/**'],
    },
  },
});
```

### 7. Test Setup File

Create `infrastructure/serverless/tests/setup.ts`:

```typescript
import { beforeEach, vi } from 'vitest';

// Mock environment variables
beforeEach(() => {
  vi.stubEnv('AWS_REGION', 'ap-northeast-1');
  vi.stubEnv('DYNAMODB_CONNECTIONS_TABLE', 'test-connections');
  vi.stubEnv('WEBSOCKET_API_ENDPOINT', 'http://localhost:3001');
  vi.stubEnv('CORS_ORIGIN', 'http://localhost:3000');
  vi.stubEnv('IS_OFFLINE', 'true');
});
```

## Backend Integration

### 1. Update FastAPI WebSocket Service

Modify `backend/src/app/application/services/apigateway_websocket_service.py`:

```python
"""API Gateway WebSocket service for broadcasting messages via Serverless Framework."""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from datetime import datetime, timezone

from app.shared.config import settings


class ApiGatewayWebSocketService:
    """Service for broadcasting messages via Serverless WebSocket API."""
    
    def __init__(self):
        self.serverless_endpoint = settings.SERVERLESS_WEBSOCKET_ENDPOINT
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for Serverless API calls."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected WebSocket clients via Serverless."""
        try:
            session = await self._get_session()
            
            async with session.post(
                f"{self.serverless_endpoint}/development/broadcast/comments",  # Include stage path
                json=message,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Broadcast successful: {result.get('connectionCount', 0)} connections")
                else:
                    error_text = await response.text()
                    print(f"❌ Broadcast failed: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Broadcast error: {str(e)}")
    
    async def broadcast_comments_list(self, post_id: str, comments: List[Dict[str, Any]]) -> None:
        """Broadcast comments list for a specific post."""
        message = {
            "type": "comments_list",
            "data": {
                "post_id": post_id,
                "comments": comments,
                "count": len(comments)
            }
        }
        
        await self.broadcast_to_all(message)
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
```

### 2. Update Configuration

Add to `backend/src/app/shared/config.py`:

```python
# Serverless WebSocket Configuration
SERVERLESS_WEBSOCKET_ENDPOINT: str = Field(
    default="http://localhost:3001",
    description="Serverless WebSocket API endpoint"
)
```

### 3. Update Environment Variables

Add to `backend/.env.development`:

```bash
# Serverless WebSocket Configuration
APP_SERVERLESS_WEBSOCKET_ENDPOINT="http://localhost:3001"
```

## Frontend Integration

### 1. Update WebSocket Hook

Modify `frontend/src/hooks/useWebSocket.ts` to handle Serverless endpoint:

```typescript
export function useWebSocket({ url, onMessage, onConnect, onDisconnect, onError }: UseWebSocketOptions) {
  // Use environment variable or fallback to Serverless local
  const wsUrl = url || process.env.NEXT_PUBLIC_WEBSOCKET_URL || 'ws://localhost:3001';
  
  // Rest of the implementation remains the same
  // ...
}
```

### 2. Update Environment Variables

Add to `frontend/.env.development`:

```bash
# Serverless WebSocket Configuration
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:3001
```

## Development Workflow

### 1. Start Serverless WebSocket Service

```bash
cd infrastructure/serverless/
pnpm install
pnpm run dev
```

**Note**: Using pnpm with local Serverless installation ensures:
- ✅ **Version consistency** across team members
- ✅ **No global dependency conflicts**
- ✅ **Project-specific configuration**
- ✅ **Faster installation** with pnpm's efficient dependency management
- ✅ **Easier CI/CD integration**

This starts the WebSocket server on `ws://localhost:3001` and HTTP API on `http://localhost:3001`.

### 2. Start FastAPI Backend

```bash
cd backend/
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start Frontend

```bash
cd frontend/
pnpm dev
```

### 4. Run Tests

```bash
# Test Serverless WebSocket handlers
cd infrastructure/serverless/
pnpm test                    # Run tests once
pnpm test:watch             # Watch mode
pnpm test:ui                # UI mode
pnpm test:coverage          # With coverage

# Test backend integration
cd ../../backend/
uv run pytest tests/integration/api/test_websocket_integration.py
```

### 5. Test WebSocket Communication

1. **Create Comment**: POST to FastAPI → DynamoDB → REST response
2. **Get Comments**: GET from FastAPI → Broadcast via Serverless → WebSocket response

## Production Deployment with AWS SAM

Since you're using AWS SAM for production deployment, here's the recommended approach:

### 1. Create AWS SAM Template

Create `infrastructure/aws-sam/template.yaml` for unified deployment:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]

Globals:
  Function:
    Runtime: python3.11
    Environment:
      Variables:
        APP_ENVIRONMENT: !Ref Environment

Resources:
  # DynamoDB Tables
  PostsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${Environment}-posts"
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST

  CommentsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${Environment}-comments"
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST

  # WebSocket API
  WebSocketAPI:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: !Sub "${Environment}-comments-websocket"
      ProtocolType: WEBSOCKET
      RouteSelectionExpression: $request.body.action

  # WebSocket Connection Table
  ConnectionsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${Environment}-websocket-connections"
      AttributeDefinitions:
        - AttributeName: connectionId
          AttributeType: S
      KeySchema:
        - AttributeName: connectionId
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST
      TimeToLiveSpecification:
        AttributeName: ttl
        Enabled: true

  # WebSocket Routes
  WebSocketConnectRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref WebSocketAPI
      RouteKey: $connect
      Target: !Sub "integrations/${WebSocketConnectIntegration}"

  WebSocketDisconnectRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref WebSocketAPI
      RouteKey: $disconnect
      Target: !Sub "integrations/${WebSocketDisconnectIntegration}"

  # WebSocket Integrations
  WebSocketConnectIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref WebSocketAPI
      IntegrationType: AWS_PROXY
      IntegrationUri: !Sub "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${WebSocketConnectFunction.Arn}/invocations"

  WebSocketDisconnectIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref WebSocketAPI
      IntegrationType: AWS_PROXY
      IntegrationUri: !Sub "arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${WebSocketDisconnectFunction.Arn}/invocations"

  # WebSocket Deployment and Stage
  WebSocketDeployment:
    Type: AWS::ApiGatewayV2::Deployment
    DependsOn:
      - WebSocketConnectRoute
      - WebSocketDisconnectRoute
    Properties:
      ApiId: !Ref WebSocketAPI

  WebSocketStage:
    Type: AWS::ApiGatewayV2::Stage
    Properties:
      ApiId: !Ref WebSocketAPI
      DeploymentId: !Ref WebSocketDeployment
      StageName: !Ref Environment

  # WebSocket Lambda Functions
  WebSocketConnectFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: websocket-handlers/
      Handler: connect.handler
      Runtime: nodejs18.x
      Environment:
        Variables:
          DYNAMODB_CONNECTIONS_TABLE: !Ref ConnectionsTable
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ConnectionsTable

  WebSocketDisconnectFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: websocket-handlers/
      Handler: disconnect.handler
      Runtime: nodejs18.x
      Environment:
        Variables:
          DYNAMODB_CONNECTIONS_TABLE: !Ref ConnectionsTable
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ConnectionsTable

  # WebSocket Lambda Permissions
  WebSocketConnectPermission:
    Type: AWS::Lambda::Permission
    Properties:
      Action: lambda:InvokeFunction
      FunctionName: !Ref WebSocketConnectFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${WebSocketAPI}/*/*"

  WebSocketDisconnectPermission:
    Type: AWS::Lambda::Permission
    Properties:
      Action: lambda:InvokeFunction
      FunctionName: !Ref WebSocketDisconnectFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${WebSocketAPI}/*/*"

  # HTTP API for WebSocket Broadcasting
  BroadcastFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: websocket-handlers/
      Handler: broadcast.broadcastToAll
      Runtime: nodejs18.x
      Environment:
        Variables:
          DYNAMODB_CONNECTIONS_TABLE: !Ref ConnectionsTable
          WEBSOCKET_API_ENDPOINT: !Sub "https://${WebSocketAPI}.execute-api.${AWS::Region}.amazonaws.com/${Environment}"
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ConnectionsTable
        - Statement:
            - Effect: Allow
              Action:
                - execute-api:ManageConnections
              Resource: !Sub "arn:aws:execute-api:${AWS::Region}:${AWS::AccountId}:${WebSocketAPI}/*/*"
      Events:
        BroadcastAPI:
          Type: Api
          Properties:
            Path: /broadcast/comments
            Method: post
            Cors:
              AllowMethods: "POST,OPTIONS"
              AllowHeaders: "Content-Type,Authorization"
              AllowOrigin: "*"

  # FastAPI Backend
  FastAPIFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: backend/
      Handler: app.main:handler
      Environment:
        Variables:
          APP_DYNAMODB_TABLE_POSTS: !Ref PostsTable
          APP_DYNAMODB_TABLE_COMMENTS: !Ref CommentsTable
          APP_SERVERLESS_WEBSOCKET_ENDPOINT: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}"
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY

Outputs:
  WebSocketURL:
    Description: WebSocket API URL
    Value: !Sub "wss://${WebSocketAPI}.execute-api.${AWS::Region}.amazonaws.com/${Environment}"
    Export:
      Name: !Sub "${Environment}-WebSocketURL"

  RestAPIURL:
    Description: REST API URL
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}"
    Export:
      Name: !Sub "${Environment}-RestAPIURL"
```

### 2. Deploy with AWS SAM

**For Staging Environment:**
```bash
# Navigate to AWS SAM directory
cd infrastructure/aws-sam/

# Build and deploy to staging
sam build
sam deploy --guided --parameter-overrides Environment=staging

# Get outputs
aws cloudformation describe-stacks --stack-name your-staging-stack-name --query 'Stacks[0].Outputs'
```

**For Production Environment:**
```bash
# Build and deploy to production
sam build
sam deploy --guided --parameter-overrides Environment=production

# Get outputs
aws cloudformation describe-stacks --stack-name your-production-stack-name --query 'Stacks[0].Outputs'

# Return to project root
cd ../../
```

**Serverless Framework Cloud Deployment:**
```bash
# Deploy to staging
cd infrastructure/serverless/
pnpm run build
pnpm exec serverless deploy --stage staging

# Deploy to production  
pnpm exec serverless deploy --stage production
```

### 3. Environment Variables by Environment

**Development (Local):**
```bash
# Backend (.env.development)
APP_ENVIRONMENT=development
APP_SERVERLESS_WEBSOCKET_ENDPOINT=http://localhost:3001
APP_AWS_ENDPOINT_URL=http://localstack:4566

# Frontend (.env.development)
NODE_ENV=development
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:3001
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**Staging (Cloud):**
```bash
# Backend (handled by SAM template)
APP_ENVIRONMENT=staging
APP_DYNAMODB_TABLE_POSTS=staging-posts
APP_DYNAMODB_TABLE_COMMENTS=staging-comments
APP_SERVERLESS_WEBSOCKET_ENDPOINT=https://your-staging-api-id.execute-api.ap-northeast-1.amazonaws.com/staging

# Frontend (Vercel environment variables)
NODE_ENV=production
NEXT_PUBLIC_WEBSOCKET_URL=wss://your-staging-websocket-api-id.execute-api.ap-northeast-1.amazonaws.com/staging
NEXT_PUBLIC_API_BASE_URL=https://your-staging-rest-api-id.execute-api.ap-northeast-1.amazonaws.com/staging
```

**Production (Cloud):**
```bash
# Backend (handled by SAM template)
APP_ENVIRONMENT=production
APP_DYNAMODB_TABLE_POSTS=production-posts
APP_DYNAMODB_TABLE_COMMENTS=production-comments
APP_SERVERLESS_WEBSOCKET_ENDPOINT=https://your-production-api-id.execute-api.ap-northeast-1.amazonaws.com/production

# Frontend (Vercel environment variables)
NODE_ENV=production
NEXT_PUBLIC_WEBSOCKET_URL=wss://your-production-websocket-api-id.execute-api.ap-northeast-1.amazonaws.com/production
NEXT_PUBLIC_API_BASE_URL=https://your-production-rest-api-id.execute-api.ap-northeast-1.amazonaws.com/production
```

## Infrastructure Organization

### 1. Move Docker Compose to Infrastructure Directory

Create `infrastructure/localstack/docker-compose.yml`:

```yaml
services:
  # LocalStack for DynamoDB only (free tier)
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    env_file:
      - ../../backend/.env.development
    environment:
      - SERVICES=dynamodb  # Only DynamoDB, no API Gateway
      - DEBUG=1
      - PERSISTENCE=1
    volumes:
      - localstack-data:/var/lib/localstack
      - /var/run/docker.sock:/var/run/docker.sock
      - ./scripts/init-dynamodb.sh:/etc/localstack/init/ready.d/init-aws.sh
    networks:
      - app-network

  # Backend application
  backend:
    build: 
      context: ../../
      dockerfile: ./backend/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ../../backend/.env.development
    environment:
      - APP_AWS_ENDPOINT_URL=http://localstack:4566  # DynamoDB via LocalStack
      - APP_SERVERLESS_WEBSOCKET_ENDPOINT=http://host.docker.internal:3001  # WebSocket via Serverless
    depends_on:
      - localstack
    networks:
      - app-network

  # Frontend application  
  frontend:
    build:
      context: ../../
      dockerfile: ./frontend/Dockerfile
    ports:
      - "3000:3000"
    env_file:
      - ../../frontend/.env.development
    networks:
      - app-network

volumes:
  localstack-data:

networks:
  app-network:
    driver: bridge
```

### 2. Development Commands

```bash
# Start LocalStack and applications
cd infrastructure/localstack/
docker-compose up -d

# Start Serverless WebSocket service
cd ../serverless/
pnpm run dev

# Note: Serverless runs outside Docker for easier development
```

### 3. Create DynamoDB Init Script for LocalStack

Since we're using LocalStack only for DynamoDB, create `infrastructure/localstack/scripts/init-dynamodb.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "[localstack-init] Initializing DynamoDB tables..."

# Helper to create a table if it does not exist
create_table_if_missing() {
  local TABLE_NAME="$1"
  local KEY_NAME="$2"

  if awslocal dynamodb describe-table --table-name "$TABLE_NAME" >/dev/null 2>&1; then
    echo "[localstack-init] Table '$TABLE_NAME' already exists. Skipping."
    return 0
  fi

  echo "[localstack-init] Creating table '$TABLE_NAME'..."
  awslocal dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName="$KEY_NAME",AttributeType=S \
    --key-schema AttributeName="$KEY_NAME",KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
}

# Helper to create a table with composite key if it does not exist
create_table_composite_if_missing() {
  local TABLE_NAME="$1"
  local HASH_KEY_NAME="$2"
  local RANGE_KEY_NAME="$3"

  if awslocal dynamodb describe-table --table-name "$TABLE_NAME" >/dev/null 2>&1; then
    echo "[localstack-init] Table '$TABLE_NAME' already exists. Skipping."
    return 0
  fi

  echo "[localstack-init] Creating composite-key table '$TABLE_NAME'..."
  awslocal dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName="$HASH_KEY_NAME",AttributeType=S AttributeName="$RANGE_KEY_NAME",AttributeType=S \
    --key-schema AttributeName="$HASH_KEY_NAME",KeyType=HASH AttributeName="$RANGE_KEY_NAME",KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST
}

# Default names match docker-compose env
POSTS_TABLE=${APP_DYNAMODB_TABLE_POSTS:-posts}
COMMENTS_TABLE=${APP_DYNAMODB_TABLE_COMMENTS:-comments}
FAVORITES_TABLE=${APP_DYNAMODB_TABLE_FAVORITES:-favorites}
WEBSOCKET_CONNECTIONS_TABLE=${DYNAMODB_CONNECTIONS_TABLE:-comments-websocket-api-dev-connections}

create_table_if_missing "$POSTS_TABLE" id
create_table_if_missing "$COMMENTS_TABLE" id
create_table_composite_if_missing "$FAVORITES_TABLE" user_id post_id
create_table_if_missing "$WEBSOCKET_CONNECTIONS_TABLE" connectionId

echo "[localstack-init] DynamoDB initialization complete."
echo "[localstack-init] Tables created: $POSTS_TABLE, $COMMENTS_TABLE, $FAVORITES_TABLE, $WEBSOCKET_CONNECTIONS_TABLE"
```

### 4. Create Serverless Dockerfile (Optional)

Create `infrastructure/serverless/Dockerfile`:

```dockerfile
FROM node:18-alpine

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile --prod

COPY . .

EXPOSE 3001

CMD ["pnpm", "run", "dev"]
```

## Testing

### 1. Unit Tests

Test WebSocket handlers with TypeScript using Vitest:

```typescript
// infrastructure/serverless/tests/handlers.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { APIGatewayProxyEvent } from 'aws-lambda';
import { handler as connectHandler } from '../src/handlers/connect';
import { broadcastToAll } from '../src/handlers/broadcast';

// Mock AWS SDK
vi.mock('aws-sdk', () => ({
  DynamoDB: {
    DocumentClient: vi.fn(() => ({
      put: vi.fn(() => ({ promise: vi.fn().mockResolvedValue({}) })),
      delete: vi.fn(() => ({ promise: vi.fn().mockResolvedValue({}) })),
      scan: vi.fn(() => ({ promise: vi.fn().mockResolvedValue({ Items: [] }) }))
    }))
  },
  ApiGatewayManagementApi: vi.fn(() => ({
    postToConnection: vi.fn(() => ({ promise: vi.fn().mockResolvedValue({}) }))
  }))
}));

describe('WebSocket Handlers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should handle connection', async () => {
    const event: Partial<APIGatewayProxyEvent> = {
      requestContext: { 
        connectionId: 'test-connection-id',
        requestId: 'test-request-id',
        stage: 'development',
        apiId: 'test-api-id'
      } as any
    };
    
    const result = await connectHandler(event as APIGatewayProxyEvent);
    expect(result.statusCode).toBe(200);
    expect(JSON.parse(result.body).message).toBe('Connected');
  });

  it('should handle missing connection ID', async () => {
    const event: Partial<APIGatewayProxyEvent> = {
      requestContext: {} as any
    };
    
    const result = await connectHandler(event as APIGatewayProxyEvent);
    expect(result.statusCode).toBe(400);
    expect(JSON.parse(result.body).message).toBe('Missing connection ID');
  });

  it('should broadcast to all connections', async () => {
    const event: Partial<APIGatewayProxyEvent> = {
      body: JSON.stringify({
        type: 'comments_list',
        data: { post_id: 'test-post', comments: [] }
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    const result = await broadcastToAll(event as APIGatewayProxyEvent);
    expect(result.statusCode).toBe(200);
    expect(JSON.parse(result.body).message).toBe('Broadcast completed');
  });

  it('should handle missing request body in broadcast', async () => {
    const event: Partial<APIGatewayProxyEvent> = {
      body: null,
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    const result = await broadcastToAll(event as APIGatewayProxyEvent);
    expect(result.statusCode).toBe(400);
    expect(JSON.parse(result.body).message).toBe('Missing request body');
  });
});
```

### 2. Integration Tests

Test FastAPI → Serverless integration:

```python
# backend/tests/integration/test_websocket_integration.py
import pytest
import asyncio
from app.application.services.apigateway_websocket_service import ApiGatewayWebSocketService

@pytest.mark.asyncio
async def test_websocket_broadcast():
    service = ApiGatewayWebSocketService()
    
    await service.broadcast_comments_list(
        post_id="test-post",
        comments=[{"id": "1", "content": "test"}]
    )
    
    await service.close()
```

## Monitoring and Logging

### 1. Serverless Logs

```bash
# Watch function logs (from infrastructure/serverless directory)
cd infrastructure/serverless/
pnpm run logs

# Watch specific function logs
pnpm exec serverless logs -f connectHandler --tail
pnpm exec serverless logs -f disconnectHandler --tail

# Get service info
pnpm run info
```

### 2. AWS CloudWatch (Production)

Monitor WebSocket connections, message counts, and error rates through CloudWatch metrics automatically created by Serverless Framework.

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check Serverless service is running on correct port
2. **CORS Errors**: Verify CORS configuration in `serverless.yml`
3. **DynamoDB Errors**: Ensure DynamoDB table is created and accessible
4. **Broadcast Failures**: Check FastAPI can reach Serverless HTTP endpoint

### Debug Commands

```bash
# Check Serverless service status
curl -X POST http://localhost:3001/development/broadcast/comments \
  -H "Content-Type: application/json" \
  -d '{"type":"test","data":{}}'

# Test WebSocket connection
wscat -c ws://localhost:3001

# Check DynamoDB connections table (LocalStack)
aws dynamodb scan --table-name comments-websocket-api-dev-connections --endpoint-url http://localhost:4566
```

## Conclusion

This Serverless Framework approach provides:

- ✅ **LocalStack Alternative**: Works without LocalStack Pro subscription
- ✅ **Production Ready**: Direct deployment to AWS API Gateway V2
- ✅ **Real WebSockets**: Full WebSocket support for development and production
- ✅ **Scalable**: Auto-scaling WebSocket connections with AWS Lambda
- ✅ **Cost Effective**: Pay-per-use pricing model

The implementation maintains the same FastAPI backend architecture while providing a robust WebSocket solution that works in both development and production environments.
