"""DynamoDB implementation of UserRepository."""

import boto3
from typing import Optional
from datetime import datetime
import logging

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


logger = logging.getLogger(__name__)


class DynamoDBUserRepository(UserRepository):
    """DynamoDB implementation of the User repository."""
    
    def __init__(self, table_name: str = "users"):
        self.table_name = table_name
        self.dynamodb = boto3.client('dynamodb')
        # Initialize table if needed in development
        self._ensure_table_exists()
    
    async def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Get user by Firebase UID"""
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={'firebase_uid': {'S': firebase_uid}}
            )
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            return self._item_to_user(item)
            
        except Exception as e:
            logger.error(f"Error getting user by Firebase UID {firebase_uid}: {str(e)}")
            return None
    
    async def create(self, user: User) -> User:
        """Create new user entity"""
        try:
            item = self._user_to_item(user)
            
            # Use condition to prevent overwriting existing users
            self.dynamodb.put_item(
                TableName=self.table_name,
                Item=item,
                ConditionExpression='attribute_not_exists(firebase_uid)'
            )
            
            return user
            
        except self.dynamodb.exceptions.ConditionalCheckFailedException:
            # User already exists
            logger.warning(f"Attempted to create user that already exists: {user.firebase_uid}")
            raise ValueError(f"User with Firebase UID {user.firebase_uid} already exists")
        except Exception as e:
            logger.error(f"Error creating user {user.firebase_uid}: {str(e)}")
            raise
    
    async def update(self, user: User) -> User:
        """Update existing user entity"""
        try:
            # Update the updated_at timestamp
            user.updated_at = datetime.utcnow()
            
            # Build update expression dynamically
            update_expression = "SET updated_at = :updated_at, display_name = :display_name, is_anonymous = :is_anonymous, #lang = :lang"
            expression_values = {
                ':updated_at': {'S': user.updated_at.isoformat()},
                ':display_name': {'S': user.display_name},
                ':is_anonymous': {'BOOL': user.is_anonymous},
                ':lang': {'S': user.language}
            }
            expression_names = {
                '#lang': 'language'  # 'language' is a reserved word in DynamoDB
            }
            
            # Add optional fields if they exist
            if user.email:
                update_expression += ", email = :email"
                expression_values[':email'] = {'S': user.email}
            
            if user.bio:
                update_expression += ", bio = :bio"
                expression_values[':bio'] = {'S': user.bio}
            
            if user.avatar_url:
                update_expression += ", avatar_url = :avatar_url"
                expression_values[':avatar_url'] = {'S': user.avatar_url}
            
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'firebase_uid': {'S': user.firebase_uid}},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ExpressionAttributeNames=expression_names,
                ConditionExpression='attribute_exists(firebase_uid)'  # Ensure user exists
            )
            
            return user
            
        except self.dynamodb.exceptions.ConditionalCheckFailedException:
            logger.error(f"Attempted to update user that doesn't exist: {user.firebase_uid}")
            raise ValueError(f"User with Firebase UID {user.firebase_uid} not found")
        except Exception as e:
            logger.error(f"Error updating user {user.firebase_uid}: {str(e)}")
            raise
    
    async def delete(self, firebase_uid: str) -> bool:
        """Delete user by Firebase UID"""
        try:
            self.dynamodb.delete_item(
                TableName=self.table_name,
                Key={'firebase_uid': {'S': firebase_uid}},
                ConditionExpression='attribute_exists(firebase_uid)'
            )
            return True
            
        except self.dynamodb.exceptions.ConditionalCheckFailedException:
            logger.warning(f"Attempted to delete user that doesn't exist: {firebase_uid}")
            return False
        except Exception as e:
            logger.error(f"Error deleting user {firebase_uid}: {str(e)}")
            return False
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if a user with the given email exists"""
        try:
            # For simplicity, scan the table for email
            # In production, consider using a GSI on email for better performance
            response = self.dynamodb.scan(
                TableName=self.table_name,
                FilterExpression='email = :email',
                ExpressionAttributeValues={
                    ':email': {'S': email}
                },
                Select='COUNT'
            )
            
            return response['Count'] > 0
            
        except Exception as e:
            logger.error(f"Error checking email existence {email}: {str(e)}")
            return False
    
    def _user_to_item(self, user: User) -> dict:
        """Convert User entity to DynamoDB item"""
        item = {
            'firebase_uid': {'S': user.firebase_uid},
            'display_name': {'S': user.display_name},
            'is_anonymous': {'BOOL': user.is_anonymous},
            'language': {'S': user.language},
            'created_at': {'S': user.created_at.isoformat()},
            'updated_at': {'S': user.updated_at.isoformat()}
        }
        
        # Add optional fields if they exist
        if user.email:
            item['email'] = {'S': user.email}
        if user.bio:
            item['bio'] = {'S': user.bio}
        if user.avatar_url:
            item['avatar_url'] = {'S': user.avatar_url}
        
        return item
    
    def _item_to_user(self, item: dict) -> User:
        """Convert DynamoDB item to User entity"""
        return User(
            firebase_uid=item['firebase_uid']['S'],
            email=item.get('email', {}).get('S'),
            display_name=item['display_name']['S'],
            is_anonymous=item['is_anonymous']['BOOL'],
            language=item['language']['S'],
            created_at=datetime.fromisoformat(item['created_at']['S']),
            updated_at=datetime.fromisoformat(item['updated_at']['S']),
            bio=item.get('bio', {}).get('S'),
            avatar_url=item.get('avatar_url', {}).get('S')
        )
    
    def _ensure_table_exists(self):
        """Ensure the users table exists (for development)."""
        try:
            # Check if table exists
            self.dynamodb.describe_table(TableName=self.table_name)
        except self.dynamodb.exceptions.ResourceNotFoundException:
            # Table doesn't exist, create it
            logger.info(f"Creating users table: {self.table_name}")
            try:
                self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'firebase_uid',
                            'KeyType': 'HASH'
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'firebase_uid',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
            except Exception as e:
                logger.warning(f"Could not create users table: {e}")
        except Exception as e:
            logger.warning(f"Could not verify users table existence: {e}")