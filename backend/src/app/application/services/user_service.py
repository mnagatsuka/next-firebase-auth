"""Application service for user-related use cases."""

from typing import Dict, Any, Optional
import logging

from app.domain.entities.user import User
from app.domain.services.user_service import UserDomainService
from app.domain.repositories.user_repository import UserRepository
from app.domain.exceptions import (
    AnonymousUserNotFoundError, 
    EmailAlreadyExistsError,
    AccountLinkingConflictError,
    UserValidationError
)
from app.shared.auth import AuthenticatedUser


logger = logging.getLogger(__name__)


class UserApplicationService:
    """Application service for user-related use cases."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.user_domain_service = UserDomainService()
    
    async def handle_anonymous_login(
        self, 
        authenticated_user: AuthenticatedUser, 
        language: str = "en"
    ) -> Dict[str, Any]:
        """Handle anonymous user login and create user entity if needed."""
        try:
            # Validate that user is actually anonymous
            if not authenticated_user.is_anonymous:
                raise UserValidationError("User is not anonymous")
            
            firebase_uid = authenticated_user.get_identity()
            
            # Check if user entity already exists
            existing_user = await self.user_repository.get_by_firebase_uid(firebase_uid)
            
            if existing_user:
                logger.info(f"Existing anonymous user found: {firebase_uid}")
                user_entity = existing_user
            else:
                # Create new anonymous user entity
                logger.info(f"Creating new anonymous user: {firebase_uid}")
                user_entity = self.user_domain_service.create_anonymous_user(
                    firebase_uid=firebase_uid,
                    language=language
                )
                user_entity = await self.user_repository.create(user_entity)
            
            # Return API response data
            return {
                "msg": "Anonymous user logged in",
                "account": self.user_domain_service.prepare_api_response_data(user_entity)
            }
            
        except UserValidationError:
            raise
        except Exception as e:
            logger.error(f"Error handling anonymous login for {authenticated_user.get_identity()}: {str(e)}")
            raise Exception("Failed to create anonymous user entity")
    
    async def handle_user_promotion(
        self,
        authenticated_user: AuthenticatedUser,
        anonymous_firebase_uuid: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Handle promotion of anonymous user to authenticated user."""
        try:
            # Validate that current user is authenticated (not anonymous)
            if authenticated_user.is_anonymous:
                raise UserValidationError("Current user is still anonymous")
            
            current_firebase_uid = authenticated_user.get_identity()
            current_email = authenticated_user.email
            
            if not current_email:
                raise UserValidationError("Authenticated user must have an email")
            
            # Check if the anonymous user exists and belongs to the same UID
            # (Firebase account linking maintains the same UID)
            if anonymous_firebase_uuid != current_firebase_uid:
                logger.warning(f"UID mismatch during promotion: {anonymous_firebase_uuid} vs {current_firebase_uid}")
            
            # Get the existing user entity (should exist from anonymous login)
            user_entity = await self.user_repository.get_by_firebase_uid(current_firebase_uid)
            
            if not user_entity:
                # Create a new user entity if somehow missing (edge case)
                logger.warning(f"User entity missing during promotion, creating new one: {current_firebase_uid}")
                user_entity = self.user_domain_service.create_authenticated_user(
                    firebase_uid=current_firebase_uid,
                    email=current_email,
                    display_name=current_email.split('@')[0],  # Use email prefix as display name
                    language=language
                )
                user_entity = await self.user_repository.create(user_entity)
            else:
                # Validate promotion business rules
                self.user_domain_service.validate_user_promotion(user_entity, current_email)
                
                # Check if email already exists (conflict prevention)
                email_exists = await self.user_repository.exists_by_email(current_email)
                if email_exists:
                    # This shouldn't happen with proper Firebase account linking, but handle gracefully
                    logger.error(f"Email already exists during promotion: {current_email}")
                    raise EmailAlreadyExistsError(f"Email {current_email} is already associated with another account")
                
                # Promote the user
                display_name = current_email.split('@')[0] if '@' in current_email else "User"
                user_entity.promote_to_authenticated(current_email, display_name)
                
                # Update in repository
                user_entity = await self.user_repository.update(user_entity)
            
            logger.info(f"User promoted successfully: {current_firebase_uid}")
            
            # Return API response data
            return {
                "msg": "Anonymous user promoted successfully", 
                "account": self.user_domain_service.prepare_api_response_data(user_entity)
            }
            
        except (UserValidationError, EmailAlreadyExistsError):
            raise
        except Exception as e:
            logger.error(f"Error promoting user {anonymous_firebase_uuid}: {str(e)}")
            raise Exception("Failed to promote anonymous user")
    
    async def get_or_create_user_entity(self, authenticated_user: AuthenticatedUser) -> Optional[User]:
        """Get existing user entity or create one if it doesn't exist."""
        try:
            firebase_uid = authenticated_user.get_identity()
            
            # Try to get existing user
            user_entity = await self.user_repository.get_by_firebase_uid(firebase_uid)
            
            if user_entity:
                return user_entity
            
            # Create new user entity based on authentication state
            if authenticated_user.is_anonymous:
                user_entity = self.user_domain_service.create_anonymous_user(
                    firebase_uid=firebase_uid,
                    language="en"  # Default language
                )
            else:
                email = authenticated_user.email or f"user-{firebase_uid}@example.com"
                display_name = email.split('@')[0] if '@' in email else "User"
                user_entity = self.user_domain_service.create_authenticated_user(
                    firebase_uid=firebase_uid,
                    email=email,
                    display_name=display_name,
                    language="en"
                )
            
            return await self.user_repository.create(user_entity)
            
        except Exception as e:
            logger.error(f"Error getting or creating user entity for {authenticated_user.get_identity()}: {str(e)}")
            return None