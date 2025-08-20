"""Firebase Admin SDK configuration and initialization."""

import os
import logging
from functools import lru_cache
from typing import Optional

import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin.auth import UserRecord

from app.shared.config import get_settings

logger = logging.getLogger(__name__)


class FirebaseService:
    """Firebase Admin SDK service for authentication."""
    
    def __init__(self):
        self._app: Optional[firebase_admin.App] = None
        self._auth_client: Optional[auth.Client] = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize Firebase Admin SDK."""
        settings = get_settings()
        
        # Set Firebase environment variables that the SDK expects (without APP_ prefix)
        if settings.FIREBASE_PROJECT_ID:
            os.environ["FIREBASE_PROJECT_ID"] = settings.FIREBASE_PROJECT_ID
            
        # Check if Firebase Auth emulator is enabled (development)
        if settings.FIREBASE_AUTH_EMULATOR_HOST:
            logger.info("Using Firebase Auth Emulator at %s", settings.FIREBASE_AUTH_EMULATOR_HOST)
            os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = settings.FIREBASE_AUTH_EMULATOR_HOST
            
            # For emulator, initialize with minimal config using ApplicationDefault
            if not firebase_admin._apps:
                self._app = firebase_admin.initialize_app(
                    credential=None,  # Use default credentials for emulator
                    options={"projectId": settings.FIREBASE_PROJECT_ID or "demo-project"},
                    name="firebase-auth-emulator"
                )
            else:
                self._app = firebase_admin.get_app("firebase-auth-emulator")
        else:
            # Production configuration with service account credentials
            if not settings.FIREBASE_PROJECT_ID:
                raise ValueError("FIREBASE_PROJECT_ID is required")
            
            if not settings.FIREBASE_PRIVATE_KEY or not settings.FIREBASE_CLIENT_EMAIL:
                raise ValueError("Firebase service account credentials are required for production")
            
            # Create credentials dict
            cred_dict = {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": settings.FIREBASE_CLIENT_ID,
                "auth_uri": settings.FIREBASE_AUTH_URI,
                "token_uri": settings.FIREBASE_TOKEN_URI,
                "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
                "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
            }
            
            # Initialize Firebase app
            if not firebase_admin._apps:
                self._app = firebase_admin.initialize_app(
                    credential=credentials.Certificate(cred_dict),
                    name="firebase-backend"
                )
            else:
                self._app = firebase_admin.get_app("firebase-backend")
        
        # Initialize auth client
        self._auth_client = auth.Client(self._app)
        logger.info("Firebase Admin SDK initialized successfully")
    
    async def verify_token(self, id_token: str, check_revoked: bool = False) -> dict:
        """
        Verify Firebase ID token and return decoded claims.
        
        Args:
            id_token: Firebase ID token to verify
            check_revoked: Whether to check if token has been revoked
            
        Returns:
            Decoded token claims containing user information
            
        Raises:
            firebase_admin.auth.InvalidIdTokenError: If token is invalid
            firebase_admin.auth.ExpiredIdTokenError: If token is expired
            firebase_admin.auth.RevokedIdTokenError: If token is revoked
        """
        if not self._auth_client:
            raise RuntimeError("Firebase not initialized")
        
        try:
            # Verify the ID token
            decoded_token = self._auth_client.verify_id_token(id_token, check_revoked=check_revoked)
            logger.debug("Token verified successfully for user: %s", decoded_token.get("uid"))
            return decoded_token
        except Exception as e:
            logger.warning("Token verification failed: %s", str(e))
            raise
    
    async def get_user(self, uid: str) -> UserRecord:
        """
        Get user information by UID.
        
        Args:
            uid: Firebase user UID
            
        Returns:
            User record from Firebase
        """
        if not self._auth_client:
            raise RuntimeError("Firebase not initialized")
        
        try:
            user = self._auth_client.get_user(uid)
            logger.debug("Retrieved user info for: %s", uid)
            return user
        except Exception as e:
            logger.warning("Failed to get user %s: %s", uid, str(e))
            raise


@lru_cache(maxsize=1)
def get_firebase_service() -> FirebaseService:
    """Get singleton Firebase service instance."""
    return FirebaseService()