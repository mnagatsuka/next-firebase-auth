# OpenAPI Specification Updates for WebSocket Migration

## Required Changes

The GET comments endpoint migration to API Gateway WebSocket response requires updates to the OpenAPI specification.

## Current vs New Response

### Current GET `/posts/{id}/comments` Response
```yaml
responses:
  "200":
    description: Successfully retrieved post comments
    content:
      application/json:
        schema:
          $ref: "../openapi.yml#/components/schemas/CommentsResponse"
```

### New GET `/posts/{id}/comments` Response
```yaml
responses:
  "200":
    description: Comments request acknowledged - data delivered via WebSocket
    content:
      application/json:
        schema:
          $ref: "../openapi.yml#/components/schemas/CommentsAcknowledgmentResponse"
```

## Files to Update

### 1. Create New Schema: CommentsAcknowledgmentResponse

```yaml
# docs/specifications/api/openapi/components/schemas/comments-acknowledgment-response.yml
type: object
required:
  - status
  - message
  - count
properties:
  status:
    type: string
    enum: ["success"]
    description: Operation status
  message:
    type: string
    description: Human-readable status message
    example: "Comments retrieved successfully"
  count:
    type: integer
    description: Number of comments that will be delivered via WebSocket
    minimum: 0
    example: 5
additionalProperties: false
```

### 2. Update Main OpenAPI Schema Registry

```yaml
# docs/specifications/api/openapi/openapi.yml - Add to components.schemas
schemas:
  # ... existing schemas ...
  CommentsAcknowledgmentResponse:
    $ref: './components/schemas/comments-acknowledgment-response.yml'
```

### 3. Create New Example

```yaml
# docs/specifications/api/openapi/components/examples/comments-acknowledgment-response.yml
summary: Comments Request Acknowledged
description: Acknowledgment response for comments request - actual comments delivered via WebSocket
value:
  status: "success"
  message: "Comments retrieved successfully"
  count: 5
```

### 4. Update Main OpenAPI Examples Registry

```yaml
# docs/specifications/api/openapi/openapi.yml - Add to components.examples
examples:
  # ... existing examples ...
  CommentsAcknowledgmentResponse:
    $ref: './components/examples/comments-acknowledgment-response.yml'
```

### 5. Update Comments Endpoint Specification

```yaml
# docs/specifications/api/openapi/paths/posts@{id}@comments.yml
get:
  tags:
    - comments
  summary: Get Post Comments
  description: |
    Initiates retrieval of comments for a specific blog post.
    
    **Response Pattern:**
    - HTTP Response: Immediate acknowledgment with comment count
    - WebSocket Delivery: Full comments data delivered via API Gateway WebSocket
    
    **WebSocket Connection:**
    - Development: `ws://localhost:4566` (LocalStack)
    - Production: `wss://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/dev`
    
    **WebSocket Message Format:**
    ```json
    {
      "type": "comments_list",
      "data": {
        "post_id": "string",
        "comments": [...],
        "count": 5
      },
      "timestamp": "2024-01-01T00:00:00Z"
    }
    ```
    
    This endpoint is public and does not require authentication.
  operationId: getPostComments
  security: [] # Public endpoint - no authentication required
  parameters:
    - $ref: "../components/parameters/post-id.yml"
    - name: limit
      in: query
      description: Maximum number of comments to return via WebSocket
      required: false
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 50
  responses:
    "200":
      description: |
        Comments request acknowledged successfully. 
        
        The actual comments data will be delivered via API Gateway WebSocket 
        to all connected clients.
      content:
        application/json:
          schema:
            $ref: "../openapi.yml#/components/schemas/CommentsAcknowledgmentResponse"
          examples:
            default:
              $ref: "../components/examples/comments-acknowledgment-response.yml"
    "404":
      $ref: "../components/responses/not-found.yml"
    "500":
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: "../openapi.yml#/components/schemas/Error"

# POST endpoint remains unchanged
post:
  # ... existing POST specification unchanged ...
```

## Implementation Steps

1. **Create new schema file**: `comments-acknowledgment-response.yml`
2. **Create new example file**: `comments-acknowledgment-response.yml` (examples)
3. **Update main OpenAPI file**: Add schema and example references
4. **Update comments endpoint**: Replace GET response specification
5. **Add WebSocket documentation**: Document WebSocket message format and endpoints
6. **Validate OpenAPI spec**: Ensure no broken references

## Validation

After updates, validate the OpenAPI specification:

```bash
# Install openapi-generator if not already installed
npm install -g @openapitools/openapi-generator-cli

# Validate the specification
openapi-generator-cli validate -i docs/specifications/api/openapi/openapi.yml
```

## API Documentation Impact

### Breaking Change Notice
- **GET `/posts/{id}/comments`** response format changed
- Old: Returns full `CommentsResponse` with comments array
- New: Returns `CommentsAcknowledgmentResponse` with count only
- **WebSocket connection required** to receive actual comments data
- **POST `/posts/{id}/comments`** remains unchanged

### Client Migration Guide
1. **Establish WebSocket connection** to API Gateway endpoint
2. **Make GET request** to `/posts/{id}/comments` for acknowledgment
3. **Listen for WebSocket message** with type `comments_list`
4. **Handle comments data** from WebSocket message payload

## Backward Compatibility

This is a **breaking change** for the GET comments endpoint. Clients will need to:
- Update to handle acknowledgment response instead of full data
- Implement WebSocket connection for receiving comments data
- Update error handling and loading states

Consider versioning the API (e.g., `/api/v2/posts/{id}/comments`) if backward compatibility is required.