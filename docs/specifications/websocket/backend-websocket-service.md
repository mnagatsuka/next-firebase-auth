# Backend WebSocket Service Implementation

## Table of Contents
- [Overview](#overview)
- [Service Architecture](#service-architecture)
- [API Endpoints](#api-endpoints)
- [WebSocket Service Layer](#websocket-service-layer)
- [Integration with Comments API](#integration-with-comments-api)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Testing](#testing)

## Overview

The backend WebSocket implementation uses an **HTTP-to-WebSocket bridge pattern** where the FastAPI backend triggers WebSocket broadcasts via HTTP requests to AWS Lambda functions. This provides a clean separation between business logic and real-time communication infrastructure.

**Key Components:**
- **FastAPI WebSocket Routes**: Handle WebSocket lifecycle events
- **WebSocket Service**: HTTP client for triggering broadcasts
- **Comments API Integration**: Real-time notifications for comment events
- **Dependency Injection**: Clean service integration
- **Environment Configuration**: Development and production support

## Service Architecture

### HTTP-to-WebSocket Bridge Pattern
```
FastAPI Business Logic → WebSocket Service → HTTP Request → Lambda Function → API Gateway WebSocket → Clients
```

**Benefits:**
- **Decoupled Architecture**: Business logic separated from WebSocket infrastructure
- **Scalable**: AWS Lambda handles WebSocket connections and scaling
- **Simple Integration**: HTTP requests are easier to test and debug than WebSocket connections
- **Environment Agnostic**: Works with both local development and AWS production

## API Endpoints

### WebSocket Lifecycle Endpoints
**Location**: `backend/src/app/api/routes/websocket.py`

#### 1. POST `/websocket/connect`
Handles WebSocket connection events from AWS API Gateway.

```python
@websocket_router.post("/connect")
async def handle_websocket_connect(
    event: WebSocketConnectEvent,
    websocket_service: ApiGatewayWebSocketService = Depends(get_apigateway_websocket_service)
) -> WebSocketResponse:
    """
    Handle WebSocket connection events from API Gateway.
    Called when a client connects to the WebSocket API.
    """
    try:
        connection_id = event.requestContext.connectionId
        await websocket_service.add_connection(connection_id)
        
        return WebSocketResponse(
            statusCode=200,
            body=json.dumps({"message": "Connected successfully"})
        )
    except Exception as e:
        logger.error(f"WebSocket connect error: {str(e)}")
        return WebSocketResponse(
            statusCode=500,
            body=json.dumps({"message": "Connection failed"})
        )
```

#### 2. POST `/websocket/disconnect`  
Handles WebSocket disconnection events.

```python
@websocket_router.post("/disconnect")
async def handle_websocket_disconnect(
    event: WebSocketDisconnectEvent,
    websocket_service: ApiGatewayWebSocketService = Depends(get_apigateway_websocket_service)
) -> WebSocketResponse:
    """
    Handle WebSocket disconnection events from API Gateway.
    Called when a client disconnects from the WebSocket API.
    """
    try:
        connection_id = event.requestContext.connectionId
        await websocket_service.remove_connection(connection_id)
        
        return WebSocketResponse(
            statusCode=200, 
            body=json.dumps({"message": "Disconnected successfully"})
        )
    except Exception as e:
        logger.error(f"WebSocket disconnect error: {str(e)}")
        return WebSocketResponse(
            statusCode=200,  # Return success even if cleanup fails
            body=json.dumps({"message": "Disconnected"})
        )
```

#### 3. GET `/websocket/connections`
Returns WebSocket connection status and health information.

```python
@websocket_router.get("/connections")
async def get_websocket_connections(
    websocket_service: ApiGatewayWebSocketService = Depends(get_apigateway_websocket_service)
) -> dict:
    """
    Get WebSocket connection status and health information.
    Useful for monitoring and debugging.
    """
    try:
        connection_count = await websocket_service.get_connection_count()
        
        return {
            "status": "healthy",
            "connectionCount": connection_count,
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": settings.SERVERLESS_WEBSOCKET_ENDPOINT
        }
    except Exception as e:
        logger.error(f"Failed to get connection status: {str(e)}")
        return {
            "status": "error",
            "connectionCount": 0,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

### Request/Response Models

```python
# WebSocket event models
class WebSocketRequestContext(BaseModel):
    connectionId: str
    requestId: str
    apiId: str
    stage: str

class WebSocketConnectEvent(BaseModel):
    requestContext: WebSocketRequestContext

class WebSocketDisconnectEvent(BaseModel):
    requestContext: WebSocketRequestContext

class WebSocketResponse(BaseModel):
    statusCode: int
    body: str
```

## WebSocket Service Layer

### Core Service Implementation
**Location**: `backend/src/app/application/services/apigateway_websocket_service.py`

```python
class ApiGatewayWebSocketService:
    """Service for broadcasting messages via AWS API Gateway WebSocket."""
    
    def __init__(self):
        self.serverless_endpoint = settings.SERVERLESS_WEBSOCKET_ENDPOINT
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for API calls."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected WebSocket clients."""
        try:
            session = await self._get_session()
            
            async with session.post(
                f"{self.serverless_endpoint}/development/broadcast/comments",
                json=message,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Broadcast successful: {result.get('connectionCount', 0)} connections")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Broadcast failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Broadcast error: {str(e)}")
```

### Broadcasting Methods

#### 1. Generic Message Broadcasting
```python
async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
    """Send any message to all connected clients."""
    # HTTP POST to Lambda broadcast endpoint
```

#### 2. Comment-Specific Broadcasting
```python
async def broadcast_new_comment(self, post_id: str, comment: Dict[str, Any]) -> None:
    """Broadcast new comment creation event."""
    message = {
        "type": "comment.created",
        "data": {
            "postId": post_id,
            "comment": comment
        }
    }
    await self.broadcast_to_all(message)

async def broadcast_comments_list(self, post_id: str, comments: List[Dict[str, Any]]) -> None:
    """Broadcast updated comments list."""
    message = {
        "type": "comments.list", 
        "data": {
            "postId": post_id,
            "comments": comments,
            "count": len(comments)
        }
    }
    await self.broadcast_to_all(message)

async def broadcast_comment_update(self, post_id: str, comment_id: str, action: str) -> None:
    """Broadcast comment update/delete events."""
    message = {
        "type": "comment.updated",
        "data": {
            "postId": post_id,
            "commentId": comment_id,
            "action": action  # 'updated' | 'deleted'
        }
    }
    await self.broadcast_to_all(message)
```

#### 3. Connection Management
```python
async def add_connection(self, connection_id: str) -> None:
    """Register a new WebSocket connection."""
    # In production, this would update DynamoDB
    # For now, it's handled by Lambda functions
    logger.info(f"Connection added: {connection_id}")

async def remove_connection(self, connection_id: str) -> None:
    """Remove a WebSocket connection."""
    # In production, this would update DynamoDB
    # For now, it's handled by Lambda functions
    logger.info(f"Connection removed: {connection_id}")

async def get_connection_count(self) -> int:
    """Get the number of active connections."""
    try:
        session = await self._get_session()
        async with session.get(
            f"{self.serverless_endpoint}/development/connections/count"
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("count", 0)
            return 0
    except Exception:
        return 0
```

#### 4. Session Management
```python
async def close(self) -> None:
    """Close the HTTP session."""
    if self.session and not self.session.closed:
        await self.session.close()
        self.session = None
```

## Integration with Comments API

### Comments Route Integration
**Location**: `backend/src/app/api/routes/comments.py`

```python
@comments_router.post("/{id}/comments")
async def create_comment(
    id: str,
    comment_data: CreateCommentRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    comment_service: CommentApplicationService = Depends(get_comment_application_service),
    websocket_service: ApiGatewayWebSocketService = Depends(get_apigateway_websocket_service)
) -> CreateCommentResponse:
    """Create a new comment with real-time WebSocket notification."""
    
    try:
        # Create comment via business logic
        created_comment = await comment_service.create_comment(
            post_id=id,
            user_id=current_user.user_id,
            content=comment_data.content
        )
        
        # Broadcast new comment via WebSocket
        await websocket_service.broadcast_new_comment(
            post_id=id,
            comment=created_comment
        )
        
        # Return acknowledgment response
        return CreateCommentResponse(
            id=created_comment["id"],
            content=created_comment["content"],
            userId=created_comment["userId"],
            createdAt=created_comment["createdAt"],
            postId=created_comment["postId"]
        )
        
    except PostNotFoundError:
        raise HTTPException(status_code=404, detail="Post not found")
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Dependency Injection
**Location**: `backend/src/app/shared/dependencies.py`

```python
from app.application.services.apigateway_websocket_service import ApiGatewayWebSocketService

# Global service instance
_websocket_service: Optional[ApiGatewayWebSocketService] = None

def get_apigateway_websocket_service() -> ApiGatewayWebSocketService:
    """Dependency injection for WebSocket service."""
    global _websocket_service
    
    if _websocket_service is None:
        _websocket_service = ApiGatewayWebSocketService()
    
    return _websocket_service

# Cleanup on application shutdown
async def cleanup_websocket_service():
    """Close WebSocket service session on shutdown."""
    global _websocket_service
    
    if _websocket_service:
        await _websocket_service.close()
        _websocket_service = None
```

### Application Lifecycle Integration
**Location**: `backend/src/app/main.py`

```python
from app.shared.dependencies import cleanup_websocket_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting FastAPI application...")
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    await cleanup_websocket_service()

app = FastAPI(lifespan=lifespan)

# Include WebSocket routes
app.include_router(
    websocket_router,
    prefix="/api/v1/websocket",
    tags=["websocket"]
)
```

## Configuration

### Environment Variables
**Location**: `backend/src/app/shared/config.py`

```python
class Settings(BaseSettings):
    # WebSocket Configuration
    SERVERLESS_WEBSOCKET_ENDPOINT: str = Field(
        default="http://localhost:3001",
        description="Serverless WebSocket API endpoint for broadcasting"
    )
    
    # AWS Configuration (for production)
    AWS_REGION: str = Field(default="ap-northeast-1")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None)
    
    class Config:
        env_prefix = "APP_"
        env_file = ".env"
```

### Environment-Specific Settings

#### Development Environment
```bash
# backend/.env.development
APP_SERVERLESS_WEBSOCKET_ENDPOINT=http://localhost:3001
APP_AWS_REGION=ap-northeast-1
```

#### Production Environment  
```bash
# Set via AWS Lambda environment variables
APP_SERVERLESS_WEBSOCKET_ENDPOINT=https://api-gateway-id.execute-api.ap-northeast-1.amazonaws.com/production
APP_AWS_REGION=ap-northeast-1
```

## Error Handling

### Service-Level Error Handling

```python
async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
    """Broadcast with comprehensive error handling."""
    try:
        session = await self._get_session()
        
        async with session.post(
            f"{self.serverless_endpoint}/development/broadcast/comments",
            json=message,
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=10)  # 10 second timeout
        ) as response:
            if response.status == 200:
                result = await response.json()
                logger.info(f"✅ Broadcast successful: {result.get('connectionCount', 0)} connections")
            else:
                error_text = await response.text()
                logger.error(f"❌ Broadcast failed: {response.status} - {error_text}")
                
    except aiohttp.ClientTimeout:
        logger.error("❌ Broadcast timeout: WebSocket service not responding")
    except aiohttp.ClientError as e:
        logger.error(f"❌ Broadcast client error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Broadcast unexpected error: {str(e)}")
```

### API Route Error Handling

```python
@comments_router.post("/{id}/comments")
async def create_comment(
    # ... parameters
) -> CreateCommentResponse:
    try:
        # Business logic
        created_comment = await comment_service.create_comment(...)
        
        # WebSocket broadcast (non-blocking)
        try:
            await websocket_service.broadcast_new_comment(...)
        except Exception as ws_error:
            # Log WebSocket error but don't fail the request
            logger.error(f"WebSocket broadcast failed: {str(ws_error)}")
        
        return CreateCommentResponse(...)
        
    except PostNotFoundError:
        raise HTTPException(status_code=404, detail="Post not found")
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Error Handling Strategy:**
- **Non-blocking WebSocket**: WebSocket failures don't block business operations
- **Graceful Degradation**: API continues to work even if WebSocket is unavailable
- **Comprehensive Logging**: All errors logged for monitoring and debugging
- **Timeout Protection**: HTTP requests have reasonable timeouts

## Testing

### Unit Tests

#### 1. WebSocket Service Tests
```python
# backend/tests/unit/services/test_websocket_service.py
import pytest
from unittest.mock import AsyncMock, patch
from app.application.services.apigateway_websocket_service import ApiGatewayWebSocketService

@pytest.fixture
def websocket_service():
    return ApiGatewayWebSocketService()

@pytest.mark.asyncio
async def test_broadcast_new_comment(websocket_service):
    """Test comment broadcasting."""
    with patch.object(websocket_service, 'broadcast_to_all') as mock_broadcast:
        await websocket_service.broadcast_new_comment(
            post_id="test-post",
            comment={"id": "1", "content": "Test comment"}
        )
        
        mock_broadcast.assert_called_once()
        call_args = mock_broadcast.call_args[0][0]
        assert call_args["type"] == "comment.created"
        assert call_args["data"]["postId"] == "test-post"

@pytest.mark.asyncio
async def test_broadcast_error_handling(websocket_service):
    """Test error handling in broadcast."""
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.side_effect = Exception("Network error")
        
        # Should not raise exception
        await websocket_service.broadcast_to_all({"type": "test"})
```

#### 2. API Route Tests
```python
# backend/tests/integration/api/test_websocket_routes.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_websocket_connect():
    """Test WebSocket connect endpoint."""
    connect_event = {
        "requestContext": {
            "connectionId": "test-connection-123",
            "requestId": "test-request",
            "apiId": "test-api",
            "stage": "test"
        }
    }
    
    response = client.post("/api/v1/websocket/connect", json=connect_event)
    assert response.status_code == 200
    assert "Connected successfully" in response.json()["message"]

def test_websocket_connections_status():
    """Test connections status endpoint."""
    response = client.get("/api/v1/websocket/connections")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "connectionCount" in data
    assert "timestamp" in data
```

### Integration Tests

#### 1. Comments + WebSocket Integration
```python
@pytest.mark.asyncio
async def test_create_comment_with_websocket(client, auth_headers, websocket_service_mock):
    """Test comment creation triggers WebSocket broadcast."""
    
    # Mock WebSocket service
    websocket_service_mock.broadcast_new_comment = AsyncMock()
    
    # Create comment
    comment_data = {"content": "Test comment"}
    response = client.post(
        "/api/v1/posts/test-post-id/comments",
        json=comment_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    
    # Verify WebSocket broadcast was called
    websocket_service_mock.broadcast_new_comment.assert_called_once()
    call_args = websocket_service_mock.broadcast_new_comment.call_args
    assert call_args[1]["post_id"] == "test-post-id"
```

### Performance Tests

```python
@pytest.mark.asyncio
async def test_websocket_broadcast_performance():
    """Test WebSocket broadcast performance."""
    import time
    
    websocket_service = ApiGatewayWebSocketService()
    
    start_time = time.time()
    
    # Send 100 messages
    tasks = []
    for i in range(100):
        task = websocket_service.broadcast_to_all({
            "type": "test",
            "data": {"message": f"Test message {i}"}
        })
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Should complete within reasonable time
    assert duration < 5.0, f"Broadcast took too long: {duration}s"
```

This backend implementation provides a robust, scalable, and maintainable WebSocket service that integrates cleanly with FastAPI business logic while maintaining proper separation of concerns.