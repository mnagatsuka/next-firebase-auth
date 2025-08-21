"""API Gateway WebSocket service for broadcasting messages to connected clients."""

import json
import boto3
from typing import List, Dict, Any, Set
from datetime import datetime, timezone
import logging
import asyncio
from app.shared.config import settings

logger = logging.getLogger(__name__)

class ApiGatewayWebSocketService:
    """Service for managing WebSocket connections and broadcasting via API Gateway."""
    
    def __init__(self):
        # Initialize API Gateway Management API client
        self.apigateway_client = self._create_client()
        
        # Store active connections (in production, use DynamoDB)
        self.connections: Set[str] = set()
    
    def _create_client(self):
        """Create boto3 client for API Gateway Management API."""
        client_config = {
            'region_name': settings.AWS_REGION,
            'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY
        }
        
        # Determine endpoint URL based on environment
        if settings.AWS_ENDPOINT_URL and "localhost" in settings.AWS_ENDPOINT_URL:
            # LocalStack development - use AWS_ENDPOINT_URL
            client_config['endpoint_url'] = settings.AWS_ENDPOINT_URL
        elif settings.API_GATEWAY_WEBSOCKET_URL:
            # AWS production - use specific WebSocket management API URL
            client_config['endpoint_url'] = settings.API_GATEWAY_WEBSOCKET_URL
        
        return boto3.client('apigatewaymanagementapi', **client_config)
    
    async def add_connection(self, connection_id: str) -> None:
        """Add a WebSocket connection to the active connections set."""
        self.connections.add(connection_id)
        logger.info(f"Added WebSocket connection: {connection_id}. Total connections: {len(self.connections)}")
    
    async def remove_connection(self, connection_id: str) -> None:
        """Remove a WebSocket connection from the active connections set."""
        self.connections.discard(connection_id)
        logger.info(f"Removed WebSocket connection: {connection_id}. Total connections: {len(self.connections)}")
    
    async def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        """Send message to all connected clients via API Gateway WebSocket."""
        if not self.connections:
            logger.info("No active WebSocket connections to broadcast to")
            return
        
        message_data = json.dumps(message)
        disconnected_connections: Set[str] = set()
        
        # Send message to each connected client
        for connection_id in self.connections:
            try:
                await self._send_to_connection(connection_id, message_data)
                logger.debug(f"Sent WebSocket message to connection: {connection_id}")
            except self.apigateway_client.exceptions.GoneException:
                # Connection is stale, mark for removal
                disconnected_connections.add(connection_id)
                logger.info(f"WebSocket connection gone: {connection_id}")
            except Exception as e:
                logger.error(f"Error sending WebSocket message to connection {connection_id}: {e}")
                # Add to disconnected list to clean up
                disconnected_connections.add(connection_id)
        
        # Clean up disconnected clients
        if disconnected_connections:
            self.connections -= disconnected_connections
            logger.info(f"Cleaned up {len(disconnected_connections)} disconnected WebSocket connections")
    
    async def _send_to_connection(self, connection_id: str, message_data: str) -> None:
        """Send message data to a specific connection."""
        # Run boto3 call in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.apigateway_client.post_to_connection(
                ConnectionId=connection_id,
                Data=message_data
            )
        )
    
    async def broadcast_comments_list(self, post_id: str, comments: List[Dict[str, Any]]) -> None:
        """Broadcast comments list to all clients via API Gateway WebSocket."""
        message = {
            "type": "comments_list",
            "data": {
                "post_id": post_id,
                "comments": comments,
                "count": len(comments)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Broadcasting comments list for post {post_id} to {len(self.connections)} connections")
        await self.broadcast_to_all(message)
    
    async def broadcast_comment_update(self, post_id: str, comment_id: str, action: str) -> None:
        """Broadcast comment updates (for future use with POST notifications)."""
        message = {
            "type": "comment_update",
            "data": {
                "post_id": post_id,
                "comment_id": comment_id,
                "action": action
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Broadcasting comment {action} for post {post_id} to {len(self.connections)} connections")
        await self.broadcast_to_all(message)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.connections)

# Global service instance
apigateway_websocket_service = ApiGatewayWebSocketService()