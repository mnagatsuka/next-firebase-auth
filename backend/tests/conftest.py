"""Backend test configuration with FastAPI DI support."""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add backend to Python path  
backend_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_path))

from app.main import create_app
from app.infra.repositories.posts_repository import InMemoryPostRepository
from app.infra.repositories.comments_repository import InMemoryCommentRepository
from app.application.services.posts_service import PostApplicationService
from app.application.services.comments_service import CommentApplicationService
from app.shared.dependencies import (
    get_post_repository, 
    get_comment_repository,
    get_post_application_service,
    get_comment_application_service,
    get_apigateway_websocket_service
)
from app.shared.auth import (
    AuthenticatedUser,
    require_authenticated_user,
    require_non_anonymous_user,
    get_current_user_optional
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def post_repository():
    """Fresh post repository for each test."""
    return InMemoryPostRepository()


@pytest.fixture
def comment_repository():
    """Fresh comment repository for each test."""
    return InMemoryCommentRepository()


@pytest.fixture
def mock_authenticated_user():
    """Mock authenticated user for testing."""
    return AuthenticatedUser(
        uid="test-user-uid",
        email="test@example.com",
        email_verified=True,
        is_anonymous=False,
        provider_data={"sign_in_provider": "password"},
        custom_claims={}
    )


@pytest.fixture
def mock_authenticated_user_different():
    """Mock different authenticated user for testing unauthorized access."""
    return AuthenticatedUser(
        uid="different-user-uid", 
        email="different@example.com",
        email_verified=True,
        is_anonymous=False,
        provider_data={"sign_in_provider": "password"},
        custom_claims={}
    )


@pytest.fixture
def mock_anonymous_user():
    """Mock anonymous user for testing data inheritance."""
    return AuthenticatedUser(
        uid="anon-user-123",
        email=None,
        email_verified=False,
        is_anonymous=True,
        provider_data={"sign_in_provider": "anonymous"},
        custom_claims={}
    )


@pytest.fixture
def test_app(post_repository, comment_repository, mock_authenticated_user, mock_websocket_service):
    """FastAPI app with test dependencies."""
    app = create_app()
    
    # Override dependencies with test repositories
    app.dependency_overrides[get_post_repository] = lambda: post_repository
    app.dependency_overrides[get_comment_repository] = lambda: comment_repository
    app.dependency_overrides[get_post_application_service] = lambda: PostApplicationService(post_repository, comment_repository)
    app.dependency_overrides[get_comment_application_service] = lambda: CommentApplicationService(comment_repository, post_repository)
    app.dependency_overrides[get_apigateway_websocket_service] = lambda: mock_websocket_service
    
    # Override auth dependencies with mock user
    app.dependency_overrides[require_authenticated_user] = lambda: mock_authenticated_user
    app.dependency_overrides[require_non_anonymous_user] = lambda: mock_authenticated_user
    app.dependency_overrides[get_current_user_optional] = lambda: mock_authenticated_user
    
    yield app
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_app_different_user(post_repository, comment_repository, mock_authenticated_user_different, mock_websocket_service):
    """FastAPI app with different authenticated user for testing authorization."""
    app = create_app()
    
    # Override dependencies with test repositories
    app.dependency_overrides[get_post_repository] = lambda: post_repository
    app.dependency_overrides[get_comment_repository] = lambda: comment_repository
    app.dependency_overrides[get_post_application_service] = lambda: PostApplicationService(post_repository, comment_repository)
    app.dependency_overrides[get_comment_application_service] = lambda: CommentApplicationService(comment_repository, post_repository)
    app.dependency_overrides[get_apigateway_websocket_service] = lambda: mock_websocket_service
    
    # Override auth dependencies with different mock user
    app.dependency_overrides[require_authenticated_user] = lambda: mock_authenticated_user_different
    app.dependency_overrides[require_non_anonymous_user] = lambda: mock_authenticated_user_different
    app.dependency_overrides[get_current_user_optional] = lambda: mock_authenticated_user_different
    
    yield app
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_app_no_auth(post_repository, comment_repository, mock_websocket_service):
    """FastAPI app with no authentication for testing unauthorized access."""
    app = create_app()
    
    # Override dependencies with test repositories
    app.dependency_overrides[get_post_repository] = lambda: post_repository
    app.dependency_overrides[get_comment_repository] = lambda: comment_repository
    app.dependency_overrides[get_post_application_service] = lambda: PostApplicationService(post_repository, comment_repository)
    app.dependency_overrides[get_comment_application_service] = lambda: CommentApplicationService(comment_repository, post_repository)
    app.dependency_overrides[get_apigateway_websocket_service] = lambda: mock_websocket_service
    
    # Don't override auth dependencies - they will raise HTTPException
    
    yield app
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def test_client(test_app):
    """FastAPI test client with dependency injection."""
    return TestClient(test_app)


@pytest.fixture
def test_client_different_user(test_app_different_user):
    """FastAPI test client with different authenticated user."""
    return TestClient(test_app_different_user)


@pytest.fixture
def test_client_no_auth(test_app_no_auth):
    """FastAPI test client with no authentication."""
    return TestClient(test_app_no_auth)


@pytest.fixture
def sample_post_data():
    """Sample post data for testing."""
    return {
        "title": "Test Blog Post",
        "content": "This is a test blog post content with lots of interesting information.",
        "excerpt": "This is a test excerpt for the blog post.",
        "author": "test-author",
        "status": "published"
    }


@pytest.fixture
def sample_create_post_request():
    """Sample create post request data."""
    return {
        "title": "Test Blog Post",
        "content": "This is a test blog post content with lots of interesting information.",
        "excerpt": "This is a test excerpt for the blog post.",
        "status": "published"
    }


@pytest.fixture
def sample_comment_data():
    """Sample comment data for testing."""
    return {
        "content": "This is a test comment with valuable feedback.",
        "author": "test-commenter"
    }


@pytest.fixture
def mock_websocket_service():
    """Mock WebSocket service for testing."""
    mock_service = Mock()
    mock_service.broadcast_comments_list = AsyncMock()
    mock_service.broadcast_comment_update = AsyncMock()
    mock_service.get_connection_count = Mock(return_value=0)
    mock_service.add_connection = AsyncMock()
    mock_service.remove_connection = AsyncMock()
    return mock_service