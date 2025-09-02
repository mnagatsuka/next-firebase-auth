"""API Gateway WebSocket service for broadcasting via Serverless Framework."""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from datetime import datetime, timezone
import logging

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

from app.shared.config import settings

logger = logging.getLogger(__name__)

class ApiGatewayWebSocketService:
    """Service for broadcasting messages via Serverless WebSocket API."""
    
    def __init__(self):
        self.serverless_endpoint = settings.SERVERLESS_WEBSOCKET_ENDPOINT
        self.session = None
        logger.info("WebSocket service initialized with endpoint: %s", self.serverless_endpoint)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session for Serverless API calls."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected WebSocket clients via Serverless."""
        try:
            session = await self._get_session()
            
            # Serialize message with datetime support
            json_data = json.dumps(message, cls=DateTimeEncoder)
            
            async with session.post(
                f"{self.serverless_endpoint}",
                data=json_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("Broadcast successful: %d connections", result.get('connectionCount', 0))
                else:
                    error_text = await response.text()
                    logger.error("Broadcast failed: %d - %s", response.status, error_text)
                    
        except Exception as e:
            logger.error("Broadcast error: %s", str(e))
    
    async def broadcast_comments_list(self, post_id: str, comments: List[Dict[str, Any]]) -> None:
        """Broadcast comments list for a specific post using envelope."""
        message = {
            "type": "comments.list",
            "data": {
                "postId": post_id,
                "comments": comments,
                "count": len(comments),
            },
        }
        await self.broadcast_to_all(message)

    async def broadcast_new_comment(self, post_id: str, comment: Dict[str, Any]) -> None:
        """Broadcast a comment.created event with full comment payload.

        Envelope fields like version/id/source are added by the serverless handler.
        """
        message = {
            "type": "comment.created",
            "data": {
                "postId": post_id,
                "comment": comment,
            },
        }
        logger.info("Broadcasting comment.created for post: %s", post_id)
        await self.broadcast_to_all(message)
    
    async def broadcast_comment_update(self, post_id: str, comment_id: str, action: str) -> None:
        """Broadcast comment updates (for future use with POST notifications)."""
        message = {
            "type": "comment_update",
            "data": {
                "post_id": post_id,
                "comment_id": comment_id,
                "action": action
            }
        }
        
        logger.info("Broadcasting comment %s for post: %s", action, post_id)
        await self.broadcast_to_all(message)
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    # Legacy compatibility methods (no-op for Serverless approach)
    async def add_connection(self, connection_id: str) -> None:
        """Legacy method - connections managed by Serverless Framework."""
        logger.debug("Connection management handled by Serverless: %s", connection_id)
    
    async def remove_connection(self, connection_id: str) -> None:
        """Legacy method - connections managed by Serverless Framework."""
        logger.debug("Connection management handled by Serverless: %s", connection_id)
    
    def get_connection_count(self) -> int:
        """Legacy method - connection count managed by Serverless Framework."""
        return 0  # Not available in HTTP broadcast approach

# Global service instance - will be created lazily
apigateway_websocket_service = None

def get_apigateway_websocket_service_instance():
    """Get or create the global WebSocket service instance."""
    global apigateway_websocket_service
    if apigateway_websocket_service is None:
        apigateway_websocket_service = ApiGatewayWebSocketService()
    return apigateway_websocket_service
