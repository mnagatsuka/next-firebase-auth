# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictStr  # noqa: F401
from typing import Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from generated_fastapi_server.models.comment import Comment  # noqa: F401
from generated_fastapi_server.models.comments_response import CommentsResponse  # noqa: F401
from generated_fastapi_server.models.create_comment_request import CreateCommentRequest  # noqa: F401
from generated_fastapi_server.models.error import Error  # noqa: F401


def test_create_comment(client: TestClient):
    """Test case for create_comment

    Create Comment
    """
    create_comment_request = null

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/posts/{id}/comments".format(id='post-123'),
    #    headers=headers,
    #    json=create_comment_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_post_comments(client: TestClient):
    """Test case for get_post_comments

    Get Post Comments
    """
    params = [("limit", 50)]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/posts/{id}/comments".format(id='post-123'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

