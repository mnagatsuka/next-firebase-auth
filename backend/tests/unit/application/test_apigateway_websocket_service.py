"""Unit tests for API Gateway WebSocket service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime

from app.application.services.apigateway_websocket_service import ApiGatewayWebSocketService


class TestApiGatewayWebSocketService:
    """Test cases for API Gateway WebSocket service."""

    def test_init(self):
        """Test WebSocket service initialization."""
        service = ApiGatewayWebSocketService()
        assert service.connections == set()
        assert hasattr(service, 'apigateway_client')

    @pytest.mark.asyncio
    async def test_add_connection(self):
        """Test adding a WebSocket connection."""
        service = ApiGatewayWebSocketService()
        connection_id = "test-connection-123"
        
        await service.add_connection(connection_id)
        
        assert connection_id in service.connections
        assert service.get_connection_count() == 1

    @pytest.mark.asyncio
    async def test_remove_connection(self):
        """Test removing a WebSocket connection."""
        service = ApiGatewayWebSocketService()
        connection_id = "test-connection-123"
        
        # Add then remove
        await service.add_connection(connection_id)
        await service.remove_connection(connection_id)
        
        assert connection_id not in service.connections
        assert service.get_connection_count() == 0

    @pytest.mark.asyncio
    async def test_remove_nonexistent_connection(self):
        """Test removing a connection that doesn't exist."""
        service = ApiGatewayWebSocketService()
        connection_id = "nonexistent-connection"
        
        # Should not raise error
        await service.remove_connection(connection_id)
        assert service.get_connection_count() == 0

    def test_get_connection_count(self):
        """Test getting connection count."""
        service = ApiGatewayWebSocketService()
        
        assert service.get_connection_count() == 0
        
        # Add connections synchronously for testing
        service.connections.add("conn-1")
        service.connections.add("conn-2")
        
        assert service.get_connection_count() == 2

    @pytest.mark.asyncio
    async def test_broadcast_to_all_no_connections(self):
        """Test broadcasting when no connections exist."""
        service = ApiGatewayWebSocketService()
        message = {"type": "test", "data": {"test": "data"}}
        
        # Should not raise error
        await service.broadcast_to_all(message)

    @pytest.mark.asyncio
    @patch('app.application.services.apigateway_websocket_service.asyncio.get_event_loop')
    async def test_broadcast_to_all_with_connections(self, mock_get_loop):
        """Test broadcasting to all connections."""
        # Mock the event loop and executor
        mock_loop = Mock()
        mock_executor = AsyncMock()
        mock_loop.run_in_executor = mock_executor
        mock_get_loop.return_value = mock_loop
        
        service = ApiGatewayWebSocketService()
        service.apigateway_client = Mock()
        
        # Add test connections
        connection_ids = ["conn-1", "conn-2"]
        for conn_id in connection_ids:
            service.connections.add(conn_id)
        
        message = {"type": "test", "data": {"test": "data"}}
        
        await service.broadcast_to_all(message)
        
        # Verify run_in_executor was called for each connection
        assert mock_executor.call_count == len(connection_ids)

    @pytest.mark.asyncio
    @patch('app.application.services.apigateway_websocket_service.asyncio.get_event_loop')
    async def test_broadcast_handles_gone_exception(self, mock_get_loop):
        """Test broadcasting handles GoneException for stale connections."""
        # Mock the event loop and executor to raise GoneException
        mock_loop = Mock()
        
        def mock_executor_side_effect(*args, **kwargs):
            # Simulate post_to_connection call that raises GoneException
            lambda_func = args[1]
            service.apigateway_client.exceptions.GoneException = Exception
            raise service.apigateway_client.exceptions.GoneException("Connection gone")
        
        mock_loop.run_in_executor = AsyncMock(side_effect=mock_executor_side_effect)
        mock_get_loop.return_value = mock_loop
        
        service = ApiGatewayWebSocketService()
        service.apigateway_client = Mock()
        service.apigateway_client.exceptions.GoneException = Exception
        
        connection_id = "stale-connection"
        service.connections.add(connection_id)
        
        message = {"type": "test", "data": {"test": "data"}}
        
        await service.broadcast_to_all(message)
        
        # Stale connection should be removed
        assert connection_id not in service.connections

    @pytest.mark.asyncio
    async def test_broadcast_comments_list(self):
        """Test broadcasting comments list."""
        service = ApiGatewayWebSocketService()
        
        # Mock the broadcast_to_all method to capture the message
        captured_message = None
        
        async def mock_broadcast(message):
            nonlocal captured_message
            captured_message = message
        
        service.broadcast_to_all = mock_broadcast
        
        post_id = "post-123"
        comments = [
            {
                "id": "comment-1",
                "content": "Test comment",
                "userId": "user-123",
                "createdAt": "2024-01-01T00:00:00Z",
                "postId": post_id
            }
        ]
        
        await service.broadcast_comments_list(post_id, comments)
        
        # Verify message structure
        assert captured_message is not None
        assert captured_message["type"] == "comments_list"
        assert captured_message["data"]["post_id"] == post_id
        assert captured_message["data"]["comments"] == comments
        assert captured_message["data"]["count"] == len(comments)
        assert "timestamp" in captured_message

    @pytest.mark.asyncio
    async def test_broadcast_comment_update(self):
        """Test broadcasting comment update."""
        service = ApiGatewayWebSocketService()
        
        # Mock the broadcast_to_all method to capture the message
        captured_message = None
        
        async def mock_broadcast(message):
            nonlocal captured_message
            captured_message = message
        
        service.broadcast_to_all = mock_broadcast
        
        post_id = "post-123"
        comment_id = "comment-456"
        action = "created"
        
        await service.broadcast_comment_update(post_id, comment_id, action)
        
        # Verify message structure
        assert captured_message is not None
        assert captured_message["type"] == "comment_update"
        assert captured_message["data"]["post_id"] == post_id
        assert captured_message["data"]["comment_id"] == comment_id
        assert captured_message["data"]["action"] == action
        assert "timestamp" in captured_message

    @pytest.mark.asyncio
    async def test_broadcast_comments_list_empty(self):
        """Test broadcasting empty comments list."""
        service = ApiGatewayWebSocketService()
        
        captured_message = None
        
        async def mock_broadcast(message):
            nonlocal captured_message
            captured_message = message
        
        service.broadcast_to_all = mock_broadcast
        
        post_id = "post-123"
        comments = []
        
        await service.broadcast_comments_list(post_id, comments)
        
        # Verify message structure for empty list
        assert captured_message is not None
        assert captured_message["type"] == "comments_list"
        assert captured_message["data"]["post_id"] == post_id
        assert captured_message["data"]["comments"] == []
        assert captured_message["data"]["count"] == 0