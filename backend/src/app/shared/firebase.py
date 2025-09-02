"""Firebase Admin SDK configuration and initialization."""

import os
import logging
from functools import lru_cache
from typing import Optional

import firebase_admin
import boto3
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
        
        def _normalize_private_key(raw: Optional[str]) -> str:
            """Normalize PEM private key from environment/secret.

            Handles common formatting pitfalls when storing keys in
            Secrets Manager or env files:
            - Strips wrapping quotes
            - Converts literal "\\n" to real newlines
            - Normalizes CRLF/CR to LF
            - Trims surrounding whitespace
            """
            if not raw:
                return ""
            pk = str(raw).strip()
            # Strip single or double quotes that wrap the whole string
            if (pk.startswith("\"") and pk.endswith("\"")) or (pk.startswith("'") and pk.endswith("'")):
                pk = pk[1:-1].strip()
            # Normalize line endings
            pk = pk.replace("\r\n", "\n").replace("\r", "\n")
            # Convert escaped newlines to real newlines
            pk = pk.replace("\\n", "\n").strip()
            # If PEM header exists, sanitize and rewrap body to 64-char lines
            if "BEGIN PRIVATE KEY" in pk or "BEGIN RSA PRIVATE KEY" in pk:
                try:
                    import re
                    lines = pk.splitlines()
                    header = lines[0].strip()
                    footer = lines[-1].strip()
                    body = "".join(lines[1:-1])
                    # Remove all non-base64 chars
                    body = re.sub(r"[^A-Za-z0-9+/=]", "", body)
                    # Rewrap at 64 chars per PEM convention
                    wrapped = "\n".join([body[i:i+64] for i in range(0, len(body), 64)])
                    pk = f"{header}\n{wrapped}\n{footer}"
                except Exception:
                    # Best-effort; fall back to pk as processed so far
                    pass
            return pk

        def _log_key_hint(pk: str) -> None:
            try:
                lines = pk.splitlines()
                first = lines[0] if lines else ""
                last = lines[-1] if lines else ""
                logger.info(
                    "[firebase] Private key hint - first: %r last: %r length: %d",
                    first,
                    last,
                    len(pk),
                )
            except Exception:
                pass
        
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
            # Production/staging configuration: Load credentials JSON from Secrets Manager at runtime
            region = getattr(settings, "AWS_REGION", None) or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
            sm = boto3.client("secretsmanager", region_name=region) if region else boto3.client("secretsmanager")
            env_name = getattr(settings, "ENVIRONMENT", "staging")
            secret_id = settings.FIREBASE_CREDENTIALS_SECRET_ID or f"/blogapp/{env_name}/firebase-credentials"

            try:
                resp = sm.get_secret_value(SecretId=secret_id)
                secret_str = resp.get("SecretString") or "{}"
            except Exception as e:
                logger.error("Failed to retrieve Firebase credentials secret '%s': %s", secret_id, e)
                secret_str = "{}"

            import json
            creds_json: dict = {}
            try:
                creds_json = json.loads(secret_str)
            except Exception as e:
                logger.error("Invalid JSON in Firebase credentials secret '%s': %s", secret_id, e)
                creds_json = {}

            json_project_id = creds_json.get("project_id")
            json_client_email = creds_json.get("client_email")
            json_private_key = creds_json.get("private_key")

            # Fallback to env if secret missing fields (maintain backward compatibility)
            project_id = json_project_id or settings.FIREBASE_PROJECT_ID
            client_email = json_client_email or settings.FIREBASE_CLIENT_EMAIL
            private_key_raw = json_private_key or settings.FIREBASE_PRIVATE_KEY

            if not project_id or not client_email or not private_key_raw:
                raise ValueError("Firebase credentials are not fully configured. Provide JSON secret or env values.")

            private_key = _normalize_private_key(private_key_raw)
            if "BEGIN PRIVATE KEY" not in private_key and "BEGIN RSA PRIVATE KEY" not in private_key:
                _log_key_hint(private_key)
                raise ValueError("Firebase private key appears misformatted after normalization.")

            # Prefer Settings token_uri default if present
            token_uri = settings.FIREBASE_TOKEN_URI

            cred_dict = {
                "type": "service_account",
                "project_id": project_id,
                "client_email": client_email,
                "private_key": private_key,
                "token_uri": token_uri,
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
