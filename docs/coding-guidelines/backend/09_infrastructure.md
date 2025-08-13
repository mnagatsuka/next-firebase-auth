# Infrastructure Layer Guidelines (Adapters & Data Access)

## Overview

The infrastructure layer implements the ports defined by the application and domain layers. It contains adapters for external systems like databases, message queues, HTTP clients, and third-party services. This layer handles technical concerns like data persistence, communication protocols, and integration patterns.

## Key Principles

- **Adapter pattern**: Implement domain/application ports with infrastructure-specific adapters
- **Isolation of concerns**: Keep infrastructure details separate from business logic
- **Configuration-driven**: Use dependency injection and configuration for flexibility
- **Resilience patterns**: Implement retries, timeouts, circuit breakers, and graceful degradation
- **Connection management**: Efficient resource usage and connection pooling

## Directory Structure

```
infra/
├── repositories/       # Data access implementations
│   ├── dynamodb/
│   │   ├── user_repository.py
│   │   ├── session_repository.py
│   │   └── base_repository.py
│   └── memory/         # In-memory implementations for testing
│       ├── user_repository.py
│       └── session_repository.py
├── adapters/          # External service adapters
│   ├── aws/
│   │   ├── s3_client.py
│   │   ├── sns_publisher.py
│   │   └── dynamodb_client.py
│   ├── firebase/
│   │   ├── auth_verifier.py
│   │   └── messaging_client.py
│   ├── http/
│   │   ├── base_client.py
│   │   └── webhook_client.py
│   └── email/
│       ├── ses_client.py
│       └── smtp_client.py
├── providers/         # Infrastructure service implementations
│   ├── time_provider.py
│   ├── id_provider.py
│   └── crypto_provider.py
├── messaging/         # Event publishing and message handling
│   ├── event_publisher.py
│   ├── message_handlers.py
│   └── event_store.py
├── persistence/       # Database configuration and migrations
│   ├── dynamodb/
│   │   ├── table_definitions.py
│   │   ├── migrations.py
│   │   └── indexes.py
│   └── models/        # Persistence models (separate from domain)
│       ├── user_model.py
│       └── session_model.py
└── config/           # Infrastructure configuration
    ├── aws_config.py
    ├── database_config.py
    └── client_config.py
```

## DynamoDB Repository Implementation

### Base Repository Pattern

```python
from abc import ABC
from typing import Optional, Dict, Any, List, Type, TypeVar, Generic
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import json
from datetime import datetime

from infra.config.aws_config import DynamoDBConfig
from infra.persistence.models.base_model import BaseModel
from shared.exceptions.infrastructure_errors import RepositoryError, ItemNotFoundError

T = TypeVar('T', bound=BaseModel)


class BaseDynamoDBRepository(Generic[T], ABC):
    """Base repository for DynamoDB operations."""
    
    def __init__(
        self,
        dynamodb_client,
        config: DynamoDBConfig,
        model_class: Type[T],
    ):
        self._client = dynamodb_client
        self._config = config
        self._model_class = model_class
        self._table = dynamodb_client.Table(config.table_name)
    
    async def _put_item(
        self,
        item: Dict[str, Any],
        condition_expression: Optional[str] = None,
    ) -> None:
        """Put item with optional condition."""
        try:
            put_kwargs = {'Item': item}
            if condition_expression:
                put_kwargs['ConditionExpression'] = condition_expression
            
            await self._table.put_item(**put_kwargs)
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise RepositoryError("Condition check failed", "CONDITION_FAILED")
            raise RepositoryError(f"DynamoDB put failed: {str(e)}", "PUT_FAILED")
    
    async def _get_item(
        self,
        key: Dict[str, Any],
        consistent_read: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Get item by key."""
        try:
            response = await self._table.get_item(
                Key=key,
                ConsistentRead=consistent_read,
            )
            return response.get('Item')
            
        except ClientError as e:
            raise RepositoryError(f"DynamoDB get failed: {str(e)}", "GET_FAILED")
    
    async def _query(
        self,
        key_condition: Key,
        filter_condition: Optional[Attr] = None,
        index_name: Optional[str] = None,
        limit: Optional[int] = None,
        exclusive_start_key: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query items with conditions."""
        try:
            query_kwargs = {
                'KeyConditionExpression': key_condition,
            }
            
            if filter_condition:
                query_kwargs['FilterExpression'] = filter_condition
            
            if index_name:
                query_kwargs['IndexName'] = index_name
            
            if limit:
                query_kwargs['Limit'] = limit
            
            if exclusive_start_key:
                query_kwargs['ExclusiveStartKey'] = exclusive_start_key
            
            return await self._table.query(**query_kwargs)
            
        except ClientError as e:
            raise RepositoryError(f"DynamoDB query failed: {str(e)}", "QUERY_FAILED")
    
    def _to_domain_model(self, item: Dict[str, Any]) -> T:
        """Convert DynamoDB item to domain model."""
        return self._model_class.from_dynamodb_item(item)
    
    def _from_domain_model(self, model: T) -> Dict[str, Any]:
        """Convert domain model to DynamoDB item."""
        return model.to_dynamodb_item()
```

### User Repository Implementation

```python
from typing import Optional, List
from boto3.dynamodb.conditions import Key, Attr

from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.ports.repositories import UserRepository
from infra.repositories.dynamodb.base_repository import BaseDynamoDBRepository
from infra.persistence.models.user_model import UserModel
from infra.config.aws_config import DynamoDBConfig


class DynamoDBUserRepository(BaseDynamoDBRepository[UserModel], UserRepository):
    """DynamoDB implementation of UserRepository."""
    
    def __init__(self, dynamodb_client, config: DynamoDBConfig):
        super().__init__(dynamodb_client, config, UserModel)
    
    async def save(self, user: User) -> None:
        """Save user with optimistic locking."""
        user_model = UserModel.from_domain_entity(user)
        item = user_model.to_dynamodb_item()
        
        # Add timestamps
        now = datetime.utcnow().isoformat()
        item['updated_at'] = now
        
        if user.version == 1:
            # New user - ensure doesn't exist
            condition = Attr('pk').not_exists()
        else:
            # Update existing - check version for optimistic locking
            condition = Attr('version').eq(user.version - 1)
        
        await self._put_item(item, condition)
    
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        key = {
            'pk': f'USER#{user_id.value}',
            'sk': f'USER#{user_id.value}',
        }
        
        item = await self._get_item(key)
        if not item:
            return None
        
        user_model = self._to_domain_model(item)
        return user_model.to_domain_entity()
    
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Find user by email using GSI."""
        response = await self._query(
            key_condition=Key('email').eq(email.value),
            index_name='EmailIndex',
            limit=1,
        )
        
        items = response.get('Items', [])
        if not items:
            return None
        
        user_model = self._to_domain_model(items[0])
        return user_model.to_domain_entity()
    
    async def find_active_users(self, limit: int = 100) -> List[User]:
        """Find active users."""
        response = await self._query(
            key_condition=Key('entity_type').eq('USER'),
            filter_condition=Attr('is_active').eq(True),
            index_name='EntityTypeIndex',
            limit=limit,
        )
        
        users = []
        for item in response.get('Items', []):
            user_model = self._to_domain_model(item)
            users.append(user_model.to_domain_entity())
        
        return users
    
    async def find_paginated(
        self,
        limit: int,
        offset: int = 0,
        active_only: bool = True,
    ) -> List[User]:
        """Find users with pagination."""
        # For offset-based pagination, we need to implement cursor logic
        # This is a simplified version - production should use cursor tokens
        
        filter_condition = None
        if active_only:
            filter_condition = Attr('is_active').eq(True)
        
        response = await self._query(
            key_condition=Key('entity_type').eq('USER'),
            filter_condition=filter_condition,
            index_name='EntityTypeIndex',
            limit=limit + offset,  # Simplified - should use proper cursor pagination
        )
        
        items = response.get('Items', [])[offset:offset + limit]
        
        users = []
        for item in items:
            user_model = self._to_domain_model(item)
            users.append(user_model.to_domain_entity())
        
        return users
    
    async def count(self, active_only: bool = True) -> int:
        """Count users. Note: This is expensive for large tables."""
        filter_condition = None
        if active_only:
            filter_condition = Attr('is_active').eq(True)
        
        response = await self._query(
            key_condition=Key('entity_type').eq('USER'),
            filter_condition=filter_condition,
            index_name='EntityTypeIndex',
        )
        
        return response['Count']
    
    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID."""
        key = {
            'pk': f'USER#{user_id.value}',
            'sk': f'USER#{user_id.value}',
        }
        
        try:
            await self._table.delete_item(
                Key=key,
                ConditionExpression=Attr('pk').exists(),
            )
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            raise
```

## S3 Adapter Implementation

```python
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
from urllib.parse import urljoin
import hashlib
import mimetypes

from domain.ports.storage import FileStorage
from infra.config.aws_config import S3Config
from shared.exceptions.infrastructure_errors import StorageError


class S3FileStorageAdapter(FileStorage):
    """S3 implementation of FileStorage port."""
    
    def __init__(self, s3_client, config: S3Config):
        self._client = s3_client
        self._config = config
    
    async def store_file(
        self,
        file_data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Store file and return content-addressable key."""
        try:
            # Read file data
            content = file_data.read()
            file_data.seek(0)  # Reset for potential re-use
            
            # Generate content hash for deduplication
            content_hash = hashlib.sha256(content).hexdigest()
            
            # Detect content type if not provided
            if not content_type:
                content_type = self._detect_content_type(content)
            
            # Generate key with content addressing
            key = self._generate_key(content_hash, content_type)
            
            # Check if file already exists (deduplication)
            if await self._file_exists(key):
                return key
            
            # Prepare metadata
            upload_metadata = {
                'content-hash': content_hash,
                'upload-time': datetime.utcnow().isoformat(),
                **(metadata or {}),
            }
            
            # Upload to S3
            await self._client.put_object(
                Bucket=self._config.bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type,
                Metadata=upload_metadata,
                ServerSideEncryption='AES256',
            )
            
            return key
            
        except Exception as e:
            raise StorageError(f"Failed to store file: {str(e)}", "STORE_FAILED")
    
    async def retrieve_file(self, key: str) -> Optional[bytes]:
        """Retrieve file content by key."""
        try:
            response = await self._client.get_object(
                Bucket=self._config.bucket_name,
                Key=key,
            )
            
            return await response['Body'].read()
            
        except self._client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            raise StorageError(f"Failed to retrieve file: {str(e)}", "RETRIEVE_FAILED")
    
    async def delete_file(self, key: str) -> bool:
        """Delete file by key."""
        try:
            await self._client.delete_object(
                Bucket=self._config.bucket_name,
                Key=key,
            )
            return True
            
        except Exception as e:
            raise StorageError(f"Failed to delete file: {str(e)}", "DELETE_FAILED")
    
    async def generate_presigned_url(
        self,
        key: str,
        operation: str = 'get_object',
        expiration: int = 3600,
    ) -> str:
        """Generate presigned URL for file access."""
        try:
            url = await self._client.generate_presigned_url(
                operation,
                Params={
                    'Bucket': self._config.bucket_name,
                    'Key': key,
                },
                ExpiresIn=expiration,
            )
            return url
            
        except Exception as e:
            raise StorageError(f"Failed to generate presigned URL: {str(e)}", "URL_FAILED")
    
    async def get_file_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get file metadata."""
        try:
            response = await self._client.head_object(
                Bucket=self._config.bucket_name,
                Key=key,
            )
            
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {}),
                'etag': response.get('ETag', '').strip('"'),
            }
            
        except self._client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            raise StorageError(f"Failed to get metadata: {str(e)}", "METADATA_FAILED")
    
    def _generate_key(self, content_hash: str, content_type: str) -> str:
        """Generate content-addressable key."""
        # Extract file extension from content type
        extension = mimetypes.guess_extension(content_type) or ''
        
        # Use first 2 chars for partitioning
        prefix = content_hash[:2]
        
        return f"{prefix}/{content_hash}{extension}"
    
    def _detect_content_type(self, content: bytes) -> str:
        """Detect content type from file content."""
        # Simple magic number detection
        if content.startswith(b'\xFF\xD8\xFF'):
            return 'image/jpeg'
        elif content.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image/png'
        elif content.startswith(b'GIF8'):
            return 'image/gif'
        elif content.startswith(b'%PDF'):
            return 'application/pdf'
        else:
            return 'application/octet-stream'
    
    async def _file_exists(self, key: str) -> bool:
        """Check if file exists in S3."""
        try:
            await self._client.head_object(
                Bucket=self._config.bucket_name,
                Key=key,
            )
            return True
        except self._client.exceptions.NoSuchKey:
            return False
```

## Firebase Auth Verification Adapter

```python
from typing import Optional, Dict, Any
import asyncio
import time
from cachetools import TTLCache

from firebase_admin import auth, credentials, initialize_app
from firebase_admin.exceptions import FirebaseError

from domain.ports.auth import TokenVerifier
from infra.config.firebase_config import FirebaseConfig
from shared.exceptions.infrastructure_errors import AuthVerificationError


class FirebaseTokenVerifier(TokenVerifier):
    """Firebase Auth token verification adapter."""
    
    def __init__(self, config: FirebaseConfig):
        self._config = config
        self._app = None
        self._token_cache = TTLCache(maxsize=1000, ttl=300)  # 5-minute cache
        self._init_firebase()
    
    def _init_firebase(self) -> None:
        """Initialize Firebase Admin SDK."""
        try:
            if self._config.service_account_path:
                cred = credentials.Certificate(self._config.service_account_path)
            else:
                # Use default credentials in cloud environment
                cred = credentials.ApplicationDefault()
            
            self._app = initialize_app(
                cred,
                {
                    'projectId': self._config.project_id,
                },
                name=f'auth-verifier-{int(time.time())}',
            )
            
        except Exception as e:
            raise AuthVerificationError(f"Failed to initialize Firebase: {str(e)}", "INIT_FAILED")
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token."""
        # Check cache first
        cache_key = f"token:{hash(token)}"
        if cache_key in self._token_cache:
            return self._token_cache[cache_key]
        
        try:
            # Verify token in thread pool (Firebase SDK is sync)
            loop = asyncio.get_event_loop()
            decoded_token = await loop.run_in_executor(
                None,
                self._verify_token_sync,
                token,
            )
            
            if decoded_token:
                # Cache successful verification
                self._token_cache[cache_key] = decoded_token
            
            return decoded_token
            
        except FirebaseError as e:
            if e.code in ['INVALID_ARGUMENT', 'UNAUTHENTICATED']:
                return None  # Invalid token, but not an error
            raise AuthVerificationError(f"Token verification failed: {str(e)}", "VERIFICATION_FAILED")
    
    def _verify_token_sync(self, token: str) -> Optional[Dict[str, Any]]:
        """Synchronous token verification."""
        try:
            decoded_token = auth.verify_id_token(token, app=self._app)
            
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'iss': decoded_token['iss'],
                'aud': decoded_token['aud'],
                'auth_time': decoded_token['auth_time'],
                'iat': decoded_token['iat'],
                'exp': decoded_token['exp'],
                'firebase': decoded_token.get('firebase', {}),
            }
            
        except auth.InvalidIdTokenError:
            return None
        except auth.ExpiredIdTokenError:
            return None
        except auth.RevokedIdTokenError:
            return None
    
    async def get_user_info(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user information by UID."""
        try:
            loop = asyncio.get_event_loop()
            user_record = await loop.run_in_executor(
                None,
                lambda: auth.get_user(uid, app=self._app),
            )
            
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'email_verified': user_record.email_verified,
                'display_name': user_record.display_name,
                'photo_url': user_record.photo_url,
                'disabled': user_record.disabled,
                'created_at': user_record.user_metadata.creation_timestamp,
                'last_sign_in': user_record.user_metadata.last_sign_in_timestamp,
            }
            
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            raise AuthVerificationError(f"Failed to get user info: {str(e)}", "USER_INFO_FAILED")
```

## HTTP Client Adapter

```python
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

from domain.ports.http_client import HTTPClient
from infra.config.client_config import HTTPConfig
from shared.exceptions.infrastructure_errors import HTTPClientError


class AIOHTTPClientAdapter(HTTPClient):
    """aiohttp-based HTTP client adapter."""
    
    def __init__(self, config: HTTPConfig):
        self._config = config
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=self._config.max_connections,
                limit_per_host=self._config.max_connections_per_host,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            timeout = aiohttp.ClientTimeout(
                total=self._config.total_timeout,
                connect=self._config.connect_timeout,
            )
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': self._config.user_agent,
                },
            )
        
        return self._session
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make GET request with retry logic."""
        return await self._request('GET', url, params=params, headers=headers)
    
    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make POST request with retry logic."""
        return await self._request('POST', url, data=data, json=json_data, headers=headers)
    
    async def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make PUT request with retry logic."""
        return await self._request('PUT', url, data=data, json=json_data, headers=headers)
    
    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make DELETE request with retry logic."""
        return await self._request('DELETE', url, headers=headers)
    
    async def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry and error handling."""
        session = await self._get_session()
        
        # Merge headers
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # Retry logic with exponential backoff
        for attempt in range(self._config.max_retries + 1):
            try:
                async with session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json,
                    headers=request_headers,
                ) as response:
                    
                    # Handle different response types
                    if response.status >= 500 and attempt < self._config.max_retries:
                        # Server error - retry with backoff
                        await self._backoff(attempt)
                        continue
                    
                    response_data = await self._parse_response(response)
                    
                    if not response.ok:
                        raise HTTPClientError(
                            f"HTTP {response.status}: {response_data}",
                            "HTTP_ERROR",
                            {'status_code': response.status, 'response': response_data},
                        )
                    
                    return response_data
                    
            except aiohttp.ClientError as e:
                if attempt == self._config.max_retries:
                    raise HTTPClientError(f"HTTP request failed: {str(e)}", "REQUEST_FAILED")
                
                await self._backoff(attempt)
        
        raise HTTPClientError("Max retries exceeded", "MAX_RETRIES_EXCEEDED")
    
    async def _parse_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Parse response based on content type."""
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/json' in content_type:
            return await response.json()
        elif 'text/' in content_type:
            text = await response.text()
            return {'text': text}
        else:
            content = await response.read()
            return {'content': content, 'content_type': content_type}
    
    async def _backoff(self, attempt: int) -> None:
        """Exponential backoff with jitter."""
        base_delay = self._config.base_delay
        max_delay = self._config.max_delay
        
        delay = min(base_delay * (2 ** attempt), max_delay)
        
        # Add jitter (±20%)
        jitter = delay * 0.2
        delay = delay + (jitter * (2 * asyncio.get_event_loop().time() % 1 - 0.5))
        
        await asyncio.sleep(max(0, delay))
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
```

## Event Publisher Implementation

```python
import json
from typing import List, Dict, Any
from datetime import datetime

from domain.events.base import DomainEvent
from application.ports.output.event_publisher import EventPublisher
from infra.config.aws_config import SNSConfig
from shared.exceptions.infrastructure_errors import EventPublishError


class SNSEventPublisher(EventPublisher):
    """SNS-based event publisher."""
    
    def __init__(self, sns_client, config: SNSConfig):
        self._client = sns_client
        self._config = config
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish single domain event."""
        try:
            message = self._serialize_event(event)
            
            await self._client.publish(
                TopicArn=self._config.topic_arn,
                Message=json.dumps(message),
                MessageAttributes={
                    'event_type': {
                        'DataType': 'String',
                        'StringValue': event.__class__.__name__,
                    },
                    'aggregate_id': {
                        'DataType': 'String',
                        'StringValue': event.aggregate_id,
                    },
                },
            )
            
        except Exception as e:
            raise EventPublishError(f"Failed to publish event: {str(e)}", "PUBLISH_FAILED")
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple events in batch."""
        if not events:
            return
        
        try:
            # SNS doesn't support batch operations, so we publish individually
            # In production, consider using SQS batch operations or event store
            for event in events:
                await self.publish(event)
                
        except Exception as e:
            raise EventPublishError(f"Failed to publish event batch: {str(e)}", "BATCH_PUBLISH_FAILED")
    
    def _serialize_event(self, event: DomainEvent) -> Dict[str, Any]:
        """Serialize domain event for transport."""
        return {
            'event_id': str(uuid.uuid4()),
            'event_type': event.__class__.__name__,
            'aggregate_id': event.aggregate_id,
            'occurred_at': event.occurred_at.isoformat(),
            'event_version': event.event_version,
            'payload': event.to_dict(),
            'published_at': datetime.utcnow().isoformat(),
        }
```

## Provider Implementations

### Time Provider

```python
from datetime import datetime
import time

from domain.ports.time_provider import TimeProvider


class SystemTimeProvider(TimeProvider):
    """System-based time provider."""
    
    def now(self) -> datetime:
        """Get current UTC datetime."""
        return datetime.utcnow()
    
    def timestamp(self) -> float:
        """Get current Unix timestamp."""
        return time.time()


class FakeTimeProvider(TimeProvider):
    """Fake time provider for testing."""
    
    def __init__(self, fixed_time: datetime):
        self._fixed_time = fixed_time
    
    def now(self) -> datetime:
        return self._fixed_time
    
    def timestamp(self) -> float:
        return self._fixed_time.timestamp()
    
    def advance(self, seconds: int) -> None:
        """Advance time for testing."""
        self._fixed_time = self._fixed_time.replace(
            second=self._fixed_time.second + seconds
        )
```

### ID Provider

```python
import uuid
from ulid import ULID

from domain.ports.id_provider import IdProvider


class ULIDProvider(IdProvider):
    """ULID-based ID provider."""
    
    def generate_ulid(self) -> str:
        """Generate ULID string."""
        return str(ULID())
    
    def generate_uuid4(self) -> str:
        """Generate UUID4 string."""
        return str(uuid.uuid4())


class FakeIdProvider(IdProvider):
    """Fake ID provider for testing."""
    
    def __init__(self, fixed_ids: List[str]):
        self._fixed_ids = fixed_ids
        self._index = 0
    
    def generate_ulid(self) -> str:
        id_value = self._fixed_ids[self._index % len(self._fixed_ids)]
        self._index += 1
        return id_value
    
    def generate_uuid4(self) -> str:
        return self.generate_ulid()
```

## Configuration

### AWS Configuration

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class DynamoDBConfig:
    """DynamoDB configuration."""
    table_name: str
    region: str = 'us-east-1'
    endpoint_url: Optional[str] = None  # For LocalStack
    
    
@dataclass
class S3Config:
    """S3 configuration."""
    bucket_name: str
    region: str = 'us-east-1'
    endpoint_url: Optional[str] = None  # For LocalStack


@dataclass
class SNSConfig:
    """SNS configuration."""
    topic_arn: str
    region: str = 'us-east-1'
    endpoint_url: Optional[str] = None  # For LocalStack


@dataclass
class AWSConfig:
    """Combined AWS configuration."""
    dynamodb: DynamoDBConfig
    s3: S3Config
    sns: SNSConfig
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None
```

## Best Practices

### Repository Design

- **Single-table design**: Use DynamoDB single-table pattern for related entities
- **Optimistic locking**: Use version fields for concurrent update protection  
- **Conditional writes**: Use condition expressions to prevent race conditions
- **Efficient queries**: Design partition keys and sort keys for query patterns
- **Connection reuse**: Reuse DynamoDB client connections across requests

### HTTP Client Best Practices

- **Connection pooling**: Reuse HTTP connections for performance
- **Timeout configuration**: Set appropriate timeouts for different operations
- **Retry with backoff**: Implement exponential backoff with jitter
- **Circuit breaker**: Implement circuit breaker pattern for resilience
- **Request/response logging**: Log requests and responses for debugging

### Error Handling

- **Specific exceptions**: Create specific exception types for different error conditions
- **Error context**: Include relevant context in exception details
- **Retry strategies**: Implement appropriate retry strategies for transient errors
- **Graceful degradation**: Handle partial failures gracefully

### Testing Infrastructure

```python
import pytest
from moto import mock_dynamodb2, mock_s3
import boto3

@pytest.fixture
def dynamodb_table():
    """Create mock DynamoDB table for testing."""
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'pk', 'KeyType': 'HASH'},
                {'AttributeName': 'sk', 'KeyType': 'RANGE'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pk', 'AttributeType': 'S'},
                {'AttributeName': 'sk', 'AttributeType': 'S'},
            ],
            BillingMode='PAY_PER_REQUEST',
        )
        
        yield table
```

This infrastructure layer provides robust, scalable implementations of all external integrations while maintaining clean separation from business logic through the port-adapter pattern.