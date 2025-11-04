# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictStr, field_validator  # noqa: F401
from typing import Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from generated_fastapi_server.models.error import Error  # noqa: F401
from generated_fastapi_server.models.firebase_login_response import FirebaseLoginResponse  # noqa: F401
from generated_fastapi_server.models.promote_anonymous_request import PromoteAnonymousRequest  # noqa: F401


def test_anonymous_login_get(client: TestClient):
    """Test case for anonymous_login_get

    Anonymous user login
    """
    params = [("lang", en)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/anonymous-login",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_promote_anonymous_post(client: TestClient):
    """Test case for promote_anonymous_post

    Promote anonymous user to authenticated user
    """
    promote_anonymous_request = generated_fastapi_server.PromoteAnonymousRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/promote-anonymous",
    #    headers=headers,
    #    json=promote_anonymous_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

