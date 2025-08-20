"""Authentication utilities and middleware for Firebase Auth."""

import logging
from typing import Optional
from dataclasses import dataclass

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin.auth

from app.shared.firebase import get_firebase_service, FirebaseService
from app.application.exceptions import AuthenticationError, InvalidTokenError

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    """Authenticated user information from Firebase."""
    uid: str
    email: Optional[str]
    email_verified: bool
    is_anonymous: bool
    provider_data: dict
    custom_claims: dict
    
    @classmethod
    def from_firebase_token(cls, decoded_token: dict) -> "AuthenticatedUser":
        """Create AuthenticatedUser from Firebase decoded token."""
        firebase_data = decoded_token.get("firebase", {})
        return cls(
            uid=decoded_token.get("uid", ""),
            email=decoded_token.get("email"),
            email_verified=decoded_token.get("email_verified", False),
            is_anonymous=firebase_data.get("sign_in_provider") == "anonymous",
            provider_data=firebase_data,
            custom_claims={k: v for k, v in decoded_token.items() 
                         if k not in ["uid", "email", "email_verified", "firebase", "iss", "aud", "auth_time", "user_id", "sub", "iat", "exp"]}
        )
    
    def get_identity(self) -> str:
        """
        Get the user's identity string for use as author/user_id.
        
        Returns:
            User's Firebase UID, which is stable across anonymous -> authenticated transitions
        """
        return self.uid


class AuthService:
    """Authentication service for handling Firebase Auth."""
    
    def __init__(self, firebase_service: FirebaseService):
        self.firebase_service = firebase_service
    
    async def verify_token(self, token: str, check_revoked: bool = False) -> AuthenticatedUser:
        """
        Verify Firebase ID token and return user information.
        
        Args:
            token: Firebase ID token
            check_revoked: Whether to check if token has been revoked
            
        Returns:
            AuthenticatedUser with user information
            
        Raises:
            InvalidTokenError: If token is invalid or expired
            AuthenticationError: For other authentication errors
        """
        try:
            decoded_token = await self.firebase_service.verify_token(token, check_revoked)
            user = AuthenticatedUser.from_firebase_token(decoded_token)
            
            logger.debug("User authenticated successfully", extra={
                "uid": user.uid,
                "email": user.email,
                "is_anonymous": user.is_anonymous
            })
            
            return user
        
        except firebase_admin.auth.InvalidIdTokenError as e:
            logger.warning("Invalid ID token: %s", str(e))
            raise InvalidTokenError("Invalid or malformed token")
        
        except firebase_admin.auth.ExpiredIdTokenError as e:
            logger.warning("Expired ID token: %s", str(e))
            raise InvalidTokenError("Token has expired")
        
        except firebase_admin.auth.RevokedIdTokenError as e:
            logger.warning("Revoked ID token: %s", str(e))
            raise InvalidTokenError("Token has been revoked")
        
        except Exception as e:
            logger.error("Token verification failed: %s", str(e), exc_info=True)
            raise AuthenticationError("Authentication failed")


def get_auth_service(
    firebase_service: FirebaseService = Depends(get_firebase_service)
) -> AuthService:
    """Dependency for getting AuthService."""
    return AuthService(firebase_service)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthenticatedUser:
    """
    Get current authenticated user from Authorization header.
    
    Raises:
        HTTPException: 401 if authentication fails
    """
    if not credentials:
        # Fallback: try session cookie for server-to-server requests
        session_cookie = request.cookies.get("session")
        if session_cookie:
            try:
                firebase_service = get_firebase_service()
                decoded_cookie = auth.verify_session_cookie(session_cookie, check_revoked=True)
                user = AuthenticatedUser.from_firebase_token(decoded_cookie)
                return user
            except Exception:
                # proceed to raise 401 below
                pass
        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        user = await auth_service.verify_token(credentials.credentials)
        return user
    
    except (InvalidTokenError, AuthenticationError) as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[AuthenticatedUser]:
    """
    Get current authenticated user if present, otherwise return None.
    
    This dependency doesn't raise exceptions for missing or invalid tokens.
    """
    if not credentials:
        # Fallback to session cookie for SSR requests
        session_cookie = request.cookies.get("session")
        if session_cookie:
            try:
                decoded_cookie = auth.verify_session_cookie(session_cookie, check_revoked=False)
                return AuthenticatedUser.from_firebase_token(decoded_cookie)
            except Exception:
                return None
        return None
    
    try:
        user = await auth_service.verify_token(credentials.credentials)
        return user
    
    except (InvalidTokenError, AuthenticationError) as e:
        logger.debug("Optional authentication failed: %s", str(e))
        return None


def require_authenticated_user(
    user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """
    Dependency that requires an authenticated user.
    
    Raises:
        HTTPException: 401 if user is not authenticated
    """
    return user


def require_non_anonymous_user(
    user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """
    Dependency that requires a non-anonymous authenticated user.
    
    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is anonymous
    """
    if user.is_anonymous:
        raise HTTPException(
            status_code=403,
            detail="Anonymous users are not allowed for this operation"
        )
    
    return user
