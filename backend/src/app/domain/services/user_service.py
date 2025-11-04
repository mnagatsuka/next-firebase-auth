"""User domain service for business logic."""

from datetime import datetime, timezone
from typing import Dict

from app.domain.entities.user import User
from app.domain.exceptions import UserValidationError


class UserDomainService:
    """Domain service for user-related business rules."""
    
    def create_anonymous_user(
        self,
        firebase_uid: str,
        language: str = "en"
    ) -> User:
        """Create anonymous user with domain validation."""
        if not firebase_uid or not firebase_uid.strip():
            raise UserValidationError("Firebase UID cannot be empty")
        
        # Language-specific display names for anonymous users
        anonymous_display_names = {
            "ja": "ゲストユーザー",
            "en": "Guest"
        }
        
        display_name = anonymous_display_names.get(language, "Guest")
        
        return User(
            firebase_uid=firebase_uid.strip(),
            email=None,
            display_name=display_name,
            is_anonymous=True,
            language=language,
            bio="",
            avatar_url=None
        )
    
    def create_authenticated_user(
        self,
        firebase_uid: str,
        email: str,
        display_name: str,
        language: str = "en"
    ) -> User:
        """Create authenticated user with domain validation."""
        if not firebase_uid or not firebase_uid.strip():
            raise UserValidationError("Firebase UID cannot be empty")
        
        if not email or not email.strip():
            raise UserValidationError("Email cannot be empty")
        
        if not display_name or not display_name.strip():
            # Fallback to email prefix for display name
            display_name = email.split('@')[0] if '@' in email else "User"
        
        return User(
            firebase_uid=firebase_uid.strip(),
            email=email.strip().lower(),
            display_name=display_name.strip(),
            is_anonymous=False,
            language=language,
            bio="",
            avatar_url=None
        )
    
    def validate_user_promotion(self, user: User, new_email: str) -> None:
        """Validate business rules for user promotion."""
        if not user.is_anonymous:
            raise UserValidationError("User is already authenticated")
        
        if not new_email or not new_email.strip():
            raise UserValidationError("Email cannot be empty")
        
        # Additional email format validation could be added here
        if '@' not in new_email:
            raise UserValidationError("Invalid email format")
    
    def prepare_api_response_data(self, user: User) -> Dict[str, any]:
        """Convert User entity to API response format."""
        return {
            "account_type": "user",
            "firebase_uuid": user.firebase_uid,
            "email": user.email,
            "email_verified": not user.is_anonymous,  # Anonymous users have unverified email
            "lang": user.language,
            "uuid": user.firebase_uid,  # Using firebase_uid as uuid for compatibility
            "account_name": user.display_name,
            "name": user.display_name,
            "bio": user.bio or "",
            "private": False,  # Default to public profiles
            "image_url": user.avatar_url or "default_image_url",
            "subscription_uuid": "",  # Empty for now
            "is_anonymous": user.is_anonymous
        }