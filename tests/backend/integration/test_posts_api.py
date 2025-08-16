import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_get_posts_list_returns_paginated_data():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/posts", params={"page": 1, "limit": 10})

    assert res.status_code == 200
    body = res.json()

    assert body["status"] == "success"
    assert "data" in body
    assert "posts" in body["data"]
    assert "pagination" in body["data"]

    posts = body["data"]["posts"]
    pagination = body["data"]["pagination"]

    assert isinstance(posts, list)
    assert pagination["page"] == 1
    assert pagination["limit"] == 10
    assert pagination["total"] >= 1
    assert pagination["hasNext"] == (pagination["page"] * pagination["limit"] < pagination["total"])

    # Ensure seeded example is present
    assert any(p.get("id") == "post-123" for p in posts)


@pytest.mark.asyncio
async def test_get_single_post_by_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/posts/post-123")

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert body["data"]["id"] == "post-123"
    assert "title" in body["data"]
    assert "content" in body["data"]
