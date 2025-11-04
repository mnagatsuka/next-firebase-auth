"""Auth API routes using generated models."""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Optional
from pydantic import Field
from typing_extensions import Annotated

# Generated models - following the existing pattern
import sys
from pathlib import Path
generated_path = Path(__file__).parent.parent.parent / "generated" / "src"
sys.path.insert(0, str(generated_path))

from generated_fastapi_server.models.firebase_login_response import FirebaseLoginResponse
from generated_fastapi_server.models.promote_anonymous_request import PromoteAnonymousRequest
from generated_fastapi_server.models.error import Error

from app.api.auth_implementation import AuthImplementation
from app.shared.auth import get_current_user, AuthenticatedUser

auth_router = APIRouter(prefix="/auth", tags=["auth"])  # group auth routes under /auth

def get_auth_impl():
    """Get AuthImplementation instance - called at request time for proper mocking."""
    return AuthImplementation()


@auth_router.get("/anonymous-login", response_model=FirebaseLoginResponse)
async def anonymous_login(
    lang: Annotated[Optional[str], Field(description="Language preference for the user")] = Query(
        "en", 
        description="Language preference for the user"
    ),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> FirebaseLoginResponse:
    """
    Anonymous user login.
    
    Authenticate anonymous users and create user records without email verification.
    
    This endpoint:
    - Validates the anonymous Firebase token
    - Creates a user entity in the backend database if it doesn't exist  
    - Returns user account information for anonymous users
    
    Anonymous users have limited functionality and are encouraged to upgrade their accounts.
    """
    auth_impl = get_auth_impl()
    return await auth_impl.anonymous_login_get(current_user, lang)


@auth_router.post("/promote-anonymous", response_model=FirebaseLoginResponse)
async def promote_anonymous(
    request: PromoteAnonymousRequest = Body(..., description="Promotion request data"),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> FirebaseLoginResponse:
    """
    Promote anonymous user to authenticated user.
    
    Convert an anonymous user to an authenticated user with permanent credentials.
    
    This endpoint:
    - Validates the new permanent Firebase token
    - Verifies the anonymous user exists in the database
    - Updates the existing user record with new authentication data
    - Preserves all existing user data (posts, comments, favorites)
    
    The user's UID remains the same to maintain data relationships.
    """
    auth_impl = get_auth_impl()
    return await auth_impl.promote_anonymous_post(current_user, request)
