"""User repository interface for the domain layer."""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.user import User


class UserRepository(ABC):
    """Abstract repository interface for User entities."""
    
    @abstractmethod
    async def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Get user by Firebase UID"""
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create new user entity"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update existing user entity"""
        pass
    
    @abstractmethod
    async def delete(self, firebase_uid: str) -> bool:
        """Delete user by Firebase UID"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if a user with the given email exists"""
        pass