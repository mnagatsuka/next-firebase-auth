"""WebSocket connection management routes for API Gateway WebSocket integration."""

from fastapi import APIRouter, HTTPException, Request, Depends
import logging
from app.shared.dependencies import get_apigateway_websocket_service

logger = logging.getLogger(__name__)

websocket_router = APIRouter(prefix="/websocket", tags=["websocket"])

@websocket_router.post("/connect")
async def handle_websocket_connect(
    request: Request,
    websocket_service = Depends(get_apigateway_websocket_service)
):
    """Handle WebSocket connection events from API Gateway."""
    try:
        # Extract connection ID from API Gateway request context
        body = await request.json()
        connection_id = body.get("requestContext", {}).get("connectionId")
        
        if not connection_id:
            raise HTTPException(status_code=400, detail="Missing connection ID")
        
        await websocket_service.add_connection(connection_id)
        logger.info(f"WebSocket connection added: {connection_id}")
        
        return {"statusCode": 200, "body": "Connected"}
        
    except Exception as e:
        logger.error(f"Error handling WebSocket connect: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@websocket_router.post("/disconnect")
async def handle_websocket_disconnect(
    request: Request,
    websocket_service = Depends(get_apigateway_websocket_service)
):
    """Handle WebSocket disconnection events from API Gateway."""
    try:
        # Extract connection ID from API Gateway request context
        body = await request.json()
        connection_id = body.get("requestContext", {}).get("connectionId")
        
        if not connection_id:
            raise HTTPException(status_code=400, detail="Missing connection ID")
        
        await websocket_service.remove_connection(connection_id)
        logger.info(f"WebSocket connection removed: {connection_id}")
        
        return {"statusCode": 200, "body": "Disconnected"}
        
    except Exception as e:
        logger.error(f"Error handling WebSocket disconnect: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@websocket_router.get("/connections")
async def get_websocket_connections(
    websocket_service = Depends(get_apigateway_websocket_service)
):
    """Get information about active WebSocket connections."""
    try:
        connection_count = websocket_service.get_connection_count()
        return {
            "active_connections": connection_count,
            "status": "healthy"
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket connections info: {e}")
        raise HTTPException(status_code=500, detail=str(e))