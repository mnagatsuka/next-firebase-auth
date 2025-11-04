"""Implementation of Auth API using clean architecture."""

from typing import Optional
import logging

from fastapi import HTTPException

# Generated models
from generated_fastapi_server.models.firebase_login_response import FirebaseLoginResponse
from generated_fastapi_server.models.firebase_account import FirebaseAccount
from generated_fastapi_server.models.promote_anonymous_request import PromoteAnonymousRequest

# Domain and application layers
from app.application.services.user_service import UserApplicationService
from app.infra.repositories.user_repository import DynamoDBUserRepository
from app.domain.exceptions import (
    UserValidationError,
    AnonymousUserNotFoundError, 
    EmailAlreadyExistsError,
    AccountLinkingConflictError
)
from app.shared.auth import AuthenticatedUser


logger = logging.getLogger(__name__)


class AuthImplementation:
    """Implementation of the Auth API using layered architecture."""
    
    def __init__(self):
        # Infrastructure layer
        self.user_repository = DynamoDBUserRepository()
        # Application layer  
        self.user_service = UserApplicationService(self.user_repository)
    
    async def anonymous_login_get(
        self, 
        authenticated_user: AuthenticatedUser,
        lang: Optional[str] = "en"
    ) -> FirebaseLoginResponse:
        """Handle anonymous user login using clean architecture layers."""
        try:
            # Call application service (use case)
            response_data = await self.user_service.handle_anonymous_login(
                authenticated_user=authenticated_user,
                language=lang or "en"
            )
            
            # Convert domain data to generated API model
            account_data = response_data["account"]
            firebase_account = FirebaseAccount(
                account_type=account_data["account_type"],
                firebase_uuid=account_data["firebase_uuid"], 
                email=account_data["email"],
                email_verified=account_data["email_verified"],
                lang=account_data["lang"],
                uuid=account_data["uuid"],
                account_name=account_data["account_name"],
                name=account_data["name"],
                bio=account_data["bio"],
                private=account_data["private"],
                image_url=account_data["image_url"],
                subscription_uuid=account_data["subscription_uuid"],
                is_anonymous=account_data["is_anonymous"]
            )
            
            return FirebaseLoginResponse(
                msg=response_data["msg"],
                account=firebase_account
            )
            
        except UserValidationError as e:
            logger.warning(f"Anonymous login validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Anonymous login failed: {str(e)}")
            raise HTTPException(status_code=500, detail="User creation failed")
    
    async def promote_anonymous_post(
        self,
        authenticated_user: AuthenticatedUser, 
        request: PromoteAnonymousRequest
    ) -> FirebaseLoginResponse:
        """Handle anonymous user promotion using clean architecture layers."""
        try:
            # Call application service (use case)
            response_data = await self.user_service.handle_user_promotion(
                authenticated_user=authenticated_user,
                anonymous_firebase_uuid=request.anonymous_firebase_uuid,
                language=request.lang or "en"
            )
            
            # Convert domain data to generated API model  
            account_data = response_data["account"]
            firebase_account = FirebaseAccount(
                account_type=account_data["account_type"],
                firebase_uuid=account_data["firebase_uuid"],
                email=account_data["email"],
                email_verified=account_data["email_verified"],
                lang=account_data["lang"],
                uuid=account_data["uuid"],
                account_name=account_data["account_name"],
                name=account_data["name"],
                bio=account_data["bio"],
                private=account_data["private"],
                image_url=account_data["image_url"],
                subscription_uuid=account_data["subscription_uuid"],
                is_anonymous=account_data["is_anonymous"]
            )
            
            return FirebaseLoginResponse(
                msg=response_data["msg"],
                account=firebase_account
            )
            
        except UserValidationError as e:
            logger.warning(f"User promotion validation error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except AnonymousUserNotFoundError as e:
            logger.warning(f"Anonymous user not found during promotion: {str(e)}")
            raise HTTPException(status_code=404, detail="Anonymous user not found in database")
        except EmailAlreadyExistsError as e:
            logger.warning(f"Email conflict during promotion: {str(e)}")
            raise HTTPException(status_code=406, detail=str(e))
        except AccountLinkingConflictError as e:
            logger.warning(f"Account linking conflict: {str(e)}")
            raise HTTPException(status_code=409, detail="Unable to link accounts due to conflicting data")
        except Exception as e:
            logger.error(f"User promotion failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Database update failed")