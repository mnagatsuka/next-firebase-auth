# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictStr, field_validator  # noqa: F401
from typing import Any, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from generated_fastapi_server.models.blog_post_list_response import BlogPostListResponse  # noqa: F401
from generated_fastapi_server.models.blog_post_response import BlogPostResponse  # noqa: F401
from generated_fastapi_server.models.create_post_request import CreatePostRequest  # noqa: F401
from generated_fastapi_server.models.error import Error  # noqa: F401


def test_create_blog_post(client: TestClient):
    """Test case for create_blog_post

    Create Blog Post
    """
    create_post_request = null

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/posts",
    #    headers=headers,
    #    json=create_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_blog_post(client: TestClient):
    """Test case for delete_blog_post

    Delete Blog Post
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/posts/{id}".format(id='post-123'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_blog_post_by_id(client: TestClient):
    """Test case for get_blog_post_by_id

    Get Single Blog Post
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/posts/{id}".format(id='post-123'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_blog_posts(client: TestClient):
    """Test case for get_blog_posts

    Get Blog Posts
    """
    params = [("page", 1),     ("limit", 10),     ("status", published),     ("author", 'John Doe')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/posts",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_update_blog_post(client: TestClient):
    """Test case for update_blog_post

    Update Blog Post
    """
    create_post_request = null

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PUT",
    #    "/posts/{id}".format(id='post-123'),
    #    headers=headers,
    #    json=create_post_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

