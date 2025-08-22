# 9. Infrastructure Layer (Data Access & External Services)

## Overview

Simple infrastructure layer for data persistence and external service integration. Focus on essential patterns without over-engineering.

## Key Principles

- Keep infrastructure adapters simple and focused
- Use basic connection management
- Handle errors gracefully with retries where appropriate

## Directory Structure

```
infra/
├── repositories/       # Data access implementations
│   ├── user_repository.py
│   └── memory_repository.py  # For testing
├── adapters/          # External service adapters
│   ├── firebase_auth.py
│   ├── s3_storage.py
│   └── http_client.py
└── config.py          # Infrastructure configuration
```

## 1. Repository Implementation

Simple repository pattern for data access:

```python
from abc import ABC, abstractmethod
from typing import Optional, List
import boto3
from botocore.exceptions import ClientError

class UserRepository(ABC):
    """Abstract user repository."""
    
    @abstractmethod
    async def save(self, user) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[dict]:
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[dict]:
        pass


class DynamoDBUserRepository(UserRepository):
    """DynamoDB implementation of user repository."""
    
    def __init__(self, table_name: str, region: str = "ap-northeast-1"):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    async def save(self, user: dict) -> None:
        """Save user to DynamoDB."""
        try:
            self.table.put_item(Item=user)
        except ClientError as e:
            raise Exception(f"Failed to save user: {e}")
    
    async def find_by_id(self, user_id: str) -> Optional[dict]:
        """Find user by ID."""
        try:
            response = self.table.get_item(Key={'id': user_id})
            return response.get('Item')
        except ClientError:
            return None
    
    async def find_by_email(self, email: str) -> Optional[dict]:
        """Find user by email."""
        try:
            response = self.table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError:
            return None
```

## 2. Firebase Auth Adapter

Simple Firebase authentication integration:

```python
import firebase_admin
from firebase_admin import auth, credentials
from typing import Optional

class FirebaseAuthAdapter:
    """Firebase Auth integration."""
    
    def __init__(self, project_id: str, credentials_path: Optional[str] = None):
        if not firebase_admin._apps:
            if credentials_path:
                cred = credentials.Certificate(credentials_path)
            else:
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
    
    async def verify_token(self, token: str) -> Optional[dict]:
        """Verify Firebase ID token."""
        try:
            decoded_token = auth.verify_id_token(token)
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name'),
            }
        except auth.InvalidIdTokenError:
            return None
        except Exception:
            return None
    
    async def get_user(self, uid: str) -> Optional[dict]:
        """Get user by UID."""
        try:
            user_record = auth.get_user(uid)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'email_verified': user_record.email_verified,
                'display_name': user_record.display_name,
                'disabled': user_record.disabled,
            }
        except auth.UserNotFoundError:
            return None
```

## 3. HTTP Client

Simple HTTP client for external API calls:

```python
import aiohttp
from typing import Dict, Any, Optional

class HTTPClient:
    """Simple HTTP client for external services."""
    
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def get(self, url: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request."""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(f"{self.base_url}{url}", headers=headers) as response:
                if response.status >= 400:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
                return await response.json()
    
    async def post(self, url: str, data: Dict[str, Any], headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request."""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(f"{self.base_url}{url}", json=data, headers=headers) as response:
                if response.status >= 400:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
                return await response.json()
```

**Rules:**

* Keep infrastructure adapters simple and focused
* Handle errors gracefully with basic retry logic
* Use standard libraries (boto3, aiohttp, firebase-admin)
* Avoid over-engineering with complex patterns
* Focus on essential functionality for small/medium applications
