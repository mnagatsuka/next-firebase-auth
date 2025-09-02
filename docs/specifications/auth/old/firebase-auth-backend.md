# Firebase Authentication Implementation

This document describes the Firebase Authentication implementation in the FastAPI backend.

## Overview

The backend implements Firebase Authentication verification following the specifications in `docs/specifications/auth/`. It supports:

- **Bearer token verification** using Firebase Admin SDK
- **Anonymous and authenticated users** with different access levels
- **Development and production environments** with Firebase Auth emulator support
- **Secure token validation** with optional revocation checking

## Architecture

### Key Components

1. **Firebase Service** (`app/shared/firebase.py`)
   - Initializes Firebase Admin SDK
   - Handles development (emulator) and production configurations
   - Provides token verification methods

2. **Authentication Dependencies** (`app/shared/auth.py`)
   - `AuthenticatedUser` dataclass for user information
   - `AuthService` for token verification
   - FastAPI dependencies for different authentication requirements

3. **Configuration** (`app/shared/config.py`)
   - Firebase project settings
   - Environment-specific configuration
   - Support for both emulator and production modes

### Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Firebase
    participant Backend

    Client->>API: Request with Bearer token
    API->>Firebase: Verify ID token
    Firebase->>API: Return user claims
    API->>Backend: Process request with user context
    Backend->>API: Return response
    API->>Client: Return result
```

## Authentication Levels

### 1. Public Endpoints
No authentication required. Examples:
- `GET /posts` - List published posts
- `GET /posts/{id}/comments` - View comments

### 2. Authenticated Endpoints
Require valid Firebase token (anonymous or regular users):
- Uses `get_current_user()` dependency
- Examples: Some read operations that need user context

### 3. Non-Anonymous Endpoints
Require authenticated non-anonymous users:
- Uses `require_non_anonymous_user()` dependency
- Examples: `POST /posts` - Create blog posts

### 4. Authenticated User Endpoints
Require any authenticated user (including anonymous):
- Uses `require_authenticated_user()` dependency
- Examples: `PUT /posts/{id}`, `DELETE /posts/{id}` - Modify user's own content

## Configuration

### Development (Firebase Auth Emulator)

Set in your `.env` file:
```bash
APP_FIREBASE_PROJECT_ID="demo-project"
APP_FIREBASE_AUTH_EMULATOR_HOST="127.0.0.1:9099"
```

### Production

Set Firebase service account credentials:
```bash
APP_FIREBASE_PROJECT_ID="your-project-id"
APP_FIREBASE_CLIENT_EMAIL="firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com"
APP_FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
# ... other service account fields
```

## Dependencies Usage

### In Route Handlers

```python
from app.shared.auth import (
    AuthenticatedUser, 
    get_current_user_optional, 
    require_authenticated_user,
    require_non_anonymous_user
)

# Optional authentication
async def get_posts(
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
):
    # current_user is None if not authenticated
    pass

# Require any authenticated user
async def update_post(
    current_user: AuthenticatedUser = Depends(require_authenticated_user)
):
    # current_user.is_anonymous may be True or False
    user_id = current_user.email or current_user.uid
    pass

# Require non-anonymous user
async def create_post(
    current_user: AuthenticatedUser = Depends(require_non_anonymous_user)
):
    # current_user.is_anonymous is guaranteed to be False
    author = current_user.email or current_user.uid
    pass
```

### AuthenticatedUser Properties

```python
@dataclass
class AuthenticatedUser:
    uid: str                    # Firebase user UID
    email: Optional[str]        # User email (None for anonymous)
    email_verified: bool        # Email verification status
    is_anonymous: bool          # True for anonymous users
    provider_data: dict         # Firebase provider information
    custom_claims: dict         # Custom token claims
```

## Error Handling

### Authentication Errors

The implementation includes global exception handlers for:

- `AuthenticationError` → 401 Unauthorized
- `InvalidTokenError` → 401 Unauthorized with specific message

### Common HTTP Responses

- **401 Unauthorized**: Invalid or missing token
- **403 Forbidden**: Valid token but insufficient permissions (e.g., anonymous user trying to create posts)

## Security Features

### Token Verification

- **Automatic signature verification** using Firebase public keys
- **Expiration checking** built into Firebase Admin SDK
- **Optional revocation checking** for sensitive operations
- **Emulator support** for development with `"alg": "none"` tokens

### Logging

- **Structured logging** with user context
- **Security event logging** for authentication failures
- **No sensitive data logging** (tokens are not logged)

### Environment Separation

- **Development**: Uses Firebase Auth emulator
- **Production**: Uses real Firebase service account credentials
- **Automatic configuration** based on environment variables

## Implementation Details

### Firebase Admin SDK Initialization

The Firebase service automatically detects the environment:

1. **Development Mode**: If `FIREBASE_AUTH_EMULATOR_HOST` is set
   - Connects to Firebase Auth emulator
   - Uses minimal configuration
   - Accepts unsigned tokens for testing

2. **Production Mode**: If emulator host is not set
   - Uses service account credentials
   - Verifies signed tokens with Firebase public keys
   - Enforces HTTPS and security requirements

### Token Extraction

Tokens are extracted from the `Authorization` header:
```
Authorization: Bearer <firebase-id-token>
```

### User Identification

Users are identified by:
1. **Email** (for authenticated users with email)
2. **UID** (Firebase user ID as fallback)

This ensures compatibility with both anonymous and regular users.

## Testing

### Development Testing

1. Start Firebase Auth emulator:
   ```bash
   npx firebase emulators:start --only auth
   ```

2. Set environment variable:
   ```bash
   export APP_FIREBASE_AUTH_EMULATOR_HOST="127.0.0.1:9099"
   ```

3. Use emulator-generated tokens for testing

### Unit Testing

Mock the Firebase service for unit tests:
```python
from unittest.mock import AsyncMock, patch
from app.shared.auth import AuthenticatedUser

@patch('app.shared.firebase.get_firebase_service')
async def test_authenticated_endpoint(mock_firebase):
    mock_service = AsyncMock()
    mock_service.verify_token.return_value = {
        "uid": "test-user",
        "email": "test@example.com"
    }
    mock_firebase.return_value = mock_service
    # ... test code
```

## Migration Guide

### From Existing Code

Replace hardcoded user IDs with authenticated user information:

```python
# Before
author = "test-author"

# After
author = current_user.email or current_user.uid
```

### Adding Authentication to New Endpoints

1. Add appropriate dependency to route handler
2. Update OpenAPI documentation with authentication requirements
3. Add error handling for authentication failures
4. Test with both authenticated and unauthenticated requests

## Verification Checklist

Based on `docs/specifications/auth/verification-check-list.md`:

- ✅ Bearer token verification implemented
- ✅ Anonymous and regular user support
- ✅ Development emulator configuration
- ✅ Production service account configuration
- ✅ User information extraction from tokens
- ✅ Authentication level enforcement (optional, required, non-anonymous)
- ✅ Proper error handling and logging
- ✅ Security best practices followed

## Troubleshooting

### Common Issues

1. **"Failed to initialize Firebase Admin SDK"**
   - Check environment variables
   - Verify Firebase emulator is running (development)
   - Validate service account credentials (production)

2. **"Invalid or expired token" errors**
   - Check token format (Bearer prefix)
   - Verify emulator configuration in development
   - Check system clock synchronization

3. **"Anonymous users are not allowed" (403 error)**
   - Endpoint uses `require_non_anonymous_user`
   - User must sign in with email/password or other provider

### Debug Logging

Enable debug logging to troubleshoot authentication issues:
```python
import logging
logging.getLogger('app.shared').setLevel(logging.DEBUG)
```

This implementation follows the Firebase Auth specifications and provides a secure, scalable authentication system for the FastAPI backend.