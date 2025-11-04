# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr, field_validator
from typing import Optional
from typing_extensions import Annotated
from generated_fastapi_server.models.error import Error
from generated_fastapi_server.models.firebase_login_response import FirebaseLoginResponse
from generated_fastapi_server.models.promote_anonymous_request import PromoteAnonymousRequest
from generated_fastapi_server.security_api import get_token_firebaseAuth

class BaseAuthApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAuthApi.subclasses = BaseAuthApi.subclasses + (cls,)
    async def auth_anonymous_login_get(
        self,
        lang: Annotated[Optional[StrictStr], Field(description="Language preference for the user")],
    ) -> FirebaseLoginResponse:
        """Authenticate anonymous users and create user records without email verification.  This endpoint: - Validates the anonymous Firebase token - Creates a user entity in the backend database if it doesn&#39;t exist - Returns user account information for anonymous users  Anonymous users have limited functionality and are encouraged to upgrade their accounts. """
        ...


    async def auth_promote_anonymous_post(
        self,
        promote_anonymous_request: PromoteAnonymousRequest,
    ) -> FirebaseLoginResponse:
        """Convert an anonymous user to an authenticated user with permanent credentials.  This endpoint: - Validates the new permanent Firebase token - Verifies the anonymous user exists in the database - Updates the existing user record with new authentication data - Preserves all existing user data (posts, comments, favorites)  The user&#39;s UID remains the same to maintain data relationships. """
        ...
