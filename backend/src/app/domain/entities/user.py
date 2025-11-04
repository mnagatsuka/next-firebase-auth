"""User domain entity with business rules."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.domain.exceptions import UserValidationError


@dataclass
class User:
    """User domain entity extending Firebase identity with additional metadata"""
    firebase_uid: str  # Primary key - Firebase UID
    email: Optional[str]  # None for anonymous users
    display_name: str  # "Guest" for anonymous, real name for authenticated
    is_anonymous: bool
    language: str  # User language preference
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Optional profile fields
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
    def can_be_updated_by(self, user_id: str) -> bool:
        """Check if user can update this profile"""
        return self.firebase_uid == user_id
    
    def promote_to_authenticated(self, email: str, display_name: str) -> None:
        """Promote anonymous user to authenticated user with business rules validation"""
        if not self.is_anonymous:
            raise UserValidationError("User is already authenticated")
        
        if not email or not email.strip():
            raise UserValidationError("Email cannot be empty")
        
        if not display_name or not display_name.strip():
            raise UserValidationError("Display name cannot be empty")
        
        self.email = email.strip()
        self.display_name = display_name.strip()
        self.is_anonymous = False
        self.updated_at = datetime.now(timezone.utc)
    
    def update_profile(self, display_name: Optional[str] = None, bio: Optional[str] = None, avatar_url: Optional[str] = None) -> None:
        """Update user profile with validation"""
        if display_name is not None:
            if not display_name.strip():
                raise UserValidationError("Display name cannot be empty")
            self.display_name = display_name.strip()
        
        if bio is not None:
            self.bio = bio.strip() if bio.strip() else None
        
        if avatar_url is not None:
            self.avatar_url = avatar_url.strip() if avatar_url.strip() else None
        
        self.updated_at = datetime.now(timezone.utc)