# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from generated_fastapi_server.apis.auth_api_base import BaseAuthApi
import generated_fastapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from generated_fastapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictStr, field_validator
from typing import Optional
from typing_extensions import Annotated
from generated_fastapi_server.models.error import Error
from generated_fastapi_server.models.firebase_login_response import FirebaseLoginResponse
from generated_fastapi_server.models.promote_anonymous_request import PromoteAnonymousRequest
from generated_fastapi_server.security_api import get_token_firebaseAuth

router = APIRouter()

ns_pkg = generated_fastapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/auth/anonymous-login",
    responses={
        200: {"model": FirebaseLoginResponse, "description": "Anonymous user authenticated successfully"},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        406: {"model": Error, "description": "Rate limit exceeded"},
        500: {"model": Error, "description": "User creation failed"},
    },
    tags=["auth"],
    summary="Anonymous user login",
    response_model_by_alias=True,
)
async def auth_anonymous_login_get(
    lang: Annotated[Optional[StrictStr], Field(description="Language preference for the user")] = Query(en, description="Language preference for the user", alias="lang"),
    token_firebaseAuth: TokenModel = Security(
        get_token_firebaseAuth
    ),
) -> FirebaseLoginResponse:
    """Authenticate anonymous users and create user records without email verification.  This endpoint: - Validates the anonymous Firebase token - Creates a user entity in the backend database if it doesn&#39;t exist - Returns user account information for anonymous users  Anonymous users have limited functionality and are encouraged to upgrade their accounts. """
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().auth_anonymous_login_get(lang)


@router.post(
    "/auth/promote-anonymous",
    responses={
        200: {"model": FirebaseLoginResponse, "description": "Anonymous user promoted successfully"},
        400: {"model": Error, "description": "Bad Request. The request data is invalid."},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        404: {"model": Error, "description": "Anonymous user not found"},
        406: {"model": Error, "description": "Email already exists with different account"},
        409: {"model": Error, "description": "Account linking conflict"},
        500: {"model": Error, "description": "Database update failed"},
    },
    tags=["auth"],
    summary="Promote anonymous user to authenticated user",
    response_model_by_alias=True,
)
async def auth_promote_anonymous_post(
    promote_anonymous_request: PromoteAnonymousRequest = Body(None, description=""),
    token_firebaseAuth: TokenModel = Security(
        get_token_firebaseAuth
    ),
) -> FirebaseLoginResponse:
    """Convert an anonymous user to an authenticated user with permanent credentials.  This endpoint: - Validates the new permanent Firebase token - Verifies the anonymous user exists in the database - Updates the existing user record with new authentication data - Preserves all existing user data (posts, comments, favorites)  The user&#39;s UID remains the same to maintain data relationships. """
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().auth_promote_anonymous_post(promote_anonymous_request)
