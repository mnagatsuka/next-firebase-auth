"""Backend test configuration."""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock
from fastapi.testclient import TestClient

# Add backend to Python path  
backend_path = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_post_repository():
    """Mock post repository."""
    return Mock()


@pytest.fixture
def sample_post_data():
    """Sample post data for testing."""
    return {
        "title": "Test Blog Post",
        "content": "This is a test blog post content with lots of interesting information.",
        "excerpt": "This is a test excerpt for the blog post.",
        "author": "test-author"
    }


@pytest.fixture
def sample_create_post_request():
    """Sample create post request data."""
    return {
        "title": "Test Blog Post",
        "content": "This is a test blog post content with lots of interesting information.",
        "excerpt": "This is a test excerpt for the blog post."
    }