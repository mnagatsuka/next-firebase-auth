# OpenAPI-First Development Workflow

This document defines the **OpenAPI-first development workflow** for coordinating between the FastAPI backend and Next.js frontend with RSC and TanStack Query.

Our goals are:
- Establish API specifications as the single source of truth
- Enable contract-driven development between backend and frontend teams
- Support both server-side fetching (RSC) and client-side fetching (TanStack Query)
- Maintain consistency between OpenAPI specs, MSW mocks, and implementations


## 1. OpenAPI Specification Structure

We organize OpenAPI specifications in `docs/specifications/api/` with component separation:

```
docs/specifications/api/
├── openapi.yml                 # Main OpenAPI spec (entry point)
├── components/                  # Reusable components
│   ├── schemas/                # Data models
│   │   ├── blog-post.yml
│   │   ├── comment.yml
│   │   └── error.yml
│   ├── responses/              # Reusable responses
│   │   ├── success-response.yml
│   │   ├── error-response.yml
│   │   └── pagination-response.yml
│   ├── parameters/             # Reusable parameters
│   │   ├── pagination.yml
│   │   └── post-id.yml
│   └── examples/               # Example data (matches MSW handlers)
│       ├── blog-post-list.yml
│       ├── blog-post.yml
│       └── error-responses.yml
└── paths/                      # API endpoints
    ├── posts.yml              # /api/posts
    ├── posts@{id}.yml         # /api/posts/{id}
    └── posts@{id}@comments.yml # /api/posts/{id}/comments
```

**Rules:**

- Response format: `{status: 'success'|'error', data?: any, error?: any}`
- Examples must work for both RSC server-side fetch and TanStack Query
- Include pagination schemas for list endpoints
- Error schemas follow RFC 7807 Problem Details format


## 2. Full-Stack Development Workflow

### Step 1: Design API Contract with Frontend Patterns in Mind

```yml
# paths/posts.yml - Designed for both RSC and TanStack Query
/posts:
  get:
    summary: List blog posts
    parameters:
      - name: page
        in: query
        schema:
          type: integer
          minimum: 1
          default: 1
      - name: limit  
        in: query
        schema:
          type: integer
          minimum: 1
          maximum: 100
          default: 10
    responses:
      '200':
        content:
          application/json:
            schema:
              type: object
              required: [status, data]
              properties:
                status:
                  type: string
                  enum: [success]
                data:
                  type: object
                  required: [posts, pagination]
                  properties:
                    posts:
                      type: array
                      items:
                        $ref: '#/components/schemas/BlogPost'
                    pagination:
                      $ref: '#/components/schemas/PaginationInfo'
            examples:
              success:
                value:
                  status: success
                  data:
                    posts:
                      - id: "post-123"
                        title: "Getting Started with Next.js"
                        excerpt: "Learn the basics..."
                        author: "John Doe"
                        publishedAt: "2024-01-15T10:30:00Z"
                    pagination:
                      page: 1
                      limit: 10
                      total: 45
                      hasNext: true
```

### Step 2: Generate TypeScript Types for Frontend

```bash
# Generate TypeScript types from OpenAPI spec
openapi-generator generate \
  -i docs/specifications/api/openapi.yml \
  -g typescript-fetch \
  -o frontend/src/lib/api/generated/ \
  --additional-properties=typescriptThreePlus=true
```

### Step 3: Update MSW Handlers to Match Contract

```typescript
// tests/mocks/handlers/index.ts
import { http, HttpResponse } from 'msw'
import type { BlogPostListResponse } from '../../frontend/src/lib/api/generated'

export const handlers = [
  http.get('/api/posts', ({ request }) => {
    const url = new URL(request.url)
    const page = Number(url.searchParams.get('page')) || 1
    const limit = Number(url.searchParams.get('limit')) || 10

    // Response matches OpenAPI BlogPostListResponse schema
    const response: BlogPostListResponse = {
      status: 'success',
      data: {
        posts: [
          {
            id: 'post-123',
            title: 'Getting Started with Next.js',
            excerpt: 'Learn the basics...',
            author: 'John Doe',
            publishedAt: '2024-01-15T10:30:00Z'
          }
        ],
        pagination: {
          page,
          limit,
          total: 45,
          hasNext: page * limit < 45
        }
      }
    }

    return HttpResponse.json(response)
  })
]
```

### Step 4: Create API Client for Both RSC and TanStack Query

```typescript
// frontend/src/lib/api/posts.ts
import type { BlogPostListResponse, BlogPost } from './generated'

const API_BASE = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8000/api' 
  : process.env.NEXT_PUBLIC_API_URL

// For Server Components (RSC)
export async function getPosts(page = 1, limit = 10): Promise<BlogPostListResponse> {
  const url = `${API_BASE}/posts?page=${page}&limit=${limit}`
  
  const response = await fetch(url, {
    next: { 
      revalidate: 300, // Cache for 5 minutes
      tags: ['posts'] 
    }
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch posts')
  }
  
  return response.json()
}

// For Client Components with TanStack Query
export async function getPostsClient(page = 1, limit = 10): Promise<BlogPostListResponse> {
  const url = `/api/posts?page=${page}&limit=${limit}`
  
  const response = await fetch(url)
  
  if (!response.ok) {
    throw new Error('Failed to fetch posts')
  }
  
  return response.json()
}
```

### Step 5: Implement Frontend Components

#### Server Component (RSC)

```tsx
// frontend/src/app/posts/page.tsx (Server Component)
import { getPosts } from '../../lib/api/posts'
import { PostList } from '../../components/blog/PostList'

interface PostsPageProps {
  searchParams: {
    page?: string
    limit?: string
  }
}

export default async function PostsPage({ searchParams }: PostsPageProps) {
  const page = Number(searchParams.page) || 1
  const limit = Number(searchParams.limit) || 10
  
  // Server-side data fetching with caching
  const { data } = await getPosts(page, limit)
  
  return (
    <div>
      <h1>Blog Posts</h1>
      <PostList posts={data.posts} />
    </div>
  )
}
```

#### Client Component with TanStack Query

```tsx
// frontend/src/components/blog/InteractivePostList.tsx
'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getPostsClient, createPost } from '../../lib/api/posts'
import { PostList } from './PostList'
import type { BlogPostListResponse } from '../../lib/api/generated'

interface InteractivePostListProps {
  initialData?: BlogPostListResponse
  page?: number
}

export function InteractivePostList({ initialData, page = 1 }: InteractivePostListProps) {
  const queryClient = useQueryClient()
  
  // TanStack Query with server-fetched initialData
  const { data, isLoading, error } = useQuery({
    queryKey: ['posts', page],
    queryFn: () => getPostsClient(page),
    initialData,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const createPostMutation = useMutation({
    mutationFn: createPost,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] })
    },
  })

  if (error) {
    return <div>Error loading posts: {error.message}</div>
  }

  return (
    <div>
      <PostList 
        posts={data?.data.posts || []} 
        isLoading={isLoading}
      />
    </div>
  )
}
```

### Step 6: Implement Backend Against Contract

```python
# backend/src/app/api/v1/posts.py
from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.application.use_cases.get_posts import GetPostsUseCase
from app.api.models import BlogPostListResponse, PaginationInfo

router = APIRouter()

@router.get("/posts", response_model=BlogPostListResponse)
async def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    get_posts_use_case: GetPostsUseCase = Depends()
):
    """Get paginated blog posts - matches OpenAPI contract and MSW mocks"""
    
    try:
        result = await get_posts_use_case.execute(page=page, limit=limit)
        
        return BlogPostListResponse(
            status="success",
            data={
                "posts": result.posts,
                "pagination": PaginationInfo(
                    page=page,
                    limit=limit,
                    total=result.total,
                    hasNext=page * limit < result.total
                )
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```


## 3. API Linting and Validation

### Spectral Configuration for Full-Stack

Create `.spectral.yml` at project root:

```yml
extends: ["@stoplight/spectral-oas"]
rules:
  # Standard OpenAPI rules
  operation-description: error
  operation-operationId-unique: error
  
  # Custom rules for Next.js + TanStack Query patterns
  consistent-response-format:
    description: "All responses must follow {status, data?, error?} format"
    given: "$.paths.*[*].responses.2*.content.application/json.schema.properties"
    severity: error
    then:
      field: "status"
      function: truthy

  pagination-consistency:
    description: "List endpoints must include pagination in response"
    given: "$.paths.*[get].responses.200.content.application/json.schema.properties.data.properties"
    severity: error
    then:
      field: "pagination"
      function: truthy

  # Ensure examples work for both RSC and TanStack Query
  realistic-examples:
    description: "Examples must be realistic for frontend consumption"
    given: "$.paths.*[*].responses.*.content.application/json.examples.*"
    severity: warn
    then:
      field: "value.status"
      function: enumeration
      functionOptions:
        values: ["success", "error"]
```

### Validation Commands

```bash
# Lint OpenAPI specification
spectral lint docs/specifications/api/openapi.yml

# Check for breaking changes
oasdiff breaking \
  docs/specifications/api/openapi.yml \
  origin/main:docs/specifications/api/openapi.yml

# Validate MSW handlers match OpenAPI
node scripts/validate-msw-contract.js
```


## 4. Contract Testing Across the Stack

### Frontend RSC Contract Tests

```typescript
// tests/frontend/rsc/posts.test.tsx
import { render, screen } from '@testing-library/react'
import PostsPage from '../../../frontend/src/app/posts/page'
import { server } from '../../mocks/server'

describe('Posts Page (RSC)', () => {
  it('renders posts from server-side fetch matching OpenAPI contract', async () => {
    const PostsPageComponent = await PostsPage({ 
      searchParams: { page: '1' } 
    })
    
    render(PostsPageComponent)
    
    expect(screen.getByText('Getting Started with Next.js')).toBeInTheDocument()
    expect(screen.getByText('John Doe')).toBeInTheDocument()
  })
})
```

### Frontend TanStack Query Contract Tests

```typescript
// tests/frontend/tanstack-query/posts.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { InteractivePostList } from '../../../frontend/src/components/blog/InteractivePostList'

describe('Interactive Posts (TanStack Query)', () => {
  it('handles client-side fetching matching OpenAPI contract', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } }
    })

    render(
      <QueryClientProvider client={queryClient}>
        <InteractivePostList />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Getting Started with Next.js')).toBeInTheDocument()
    })
  })
})
```

### Backend Contract Tests

```python
# tests/backend/e2e/contract/test_posts_contract.py
@pytest.mark.contract
async def test_posts_endpoint_matches_frontend_expectations(client):
    """Test backend response matches both RSC and TanStack Query expectations"""
    
    response = await client.get("/api/v1/posts?page=1&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure works for both RSC and TanStack Query
    assert data["status"] == "success"
    assert "data" in data
    assert "posts" in data["data"]
    assert "pagination" in data["data"]
    
    # Verify pagination info is complete for frontend
    pagination = data["data"]["pagination"]
    assert "page" in pagination
    assert "limit" in pagination
    assert "total" in pagination
    assert "hasNext" in pagination
```


## 5. Caching Strategy Coordination

### Server-Side Caching (RSC)

```typescript
// Coordinate caching between Next.js and backend
export async function getPosts(page = 1): Promise<BlogPostListResponse> {
  const response = await fetch(`${API_BASE}/posts?page=${page}`, {
    next: { 
      revalidate: 300,        // Next.js cache: 5 minutes
      tags: ['posts']         // For targeted revalidation
    }
  })
  return response.json()
}

// Server action for revalidation
export async function revalidatePosts() {
  'use server'
  revalidateTag('posts')
}
```

### Client-Side Caching (TanStack Query)

```typescript
// TanStack Query configuration matching backend cache timing
export const postsQueryOptions = {
  queryKey: ['posts'],
  staleTime: 5 * 60 * 1000,    // 5 minutes (matches RSC revalidate)
  cacheTime: 10 * 60 * 1000,   // 10 minutes
}
```

### Backend Cache Headers

```python
# backend/src/app/api/v1/posts.py
from fastapi import Response

@router.get("/posts")
async def get_posts(response: Response, page: int = 1):
    # Set cache headers to coordinate with frontend
    response.headers["Cache-Control"] = "public, s-maxage=300, max-age=300"
    response.headers["ETag"] = generate_etag_for_posts(page)
    
    # ... implementation
```


## 6. Error Handling Coordination

### Consistent Error Format

```yml
# components/schemas/api-error.yml
ApiError:
  type: object
  required: [status, error]
  properties:
    status:
      type: string
      enum: [error]
    error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          enum: [NOT_FOUND, UNAUTHORIZED, VALIDATION_ERROR, INTERNAL_SERVER_ERROR]
        message:
          type: string
        details:
          type: object
          additionalProperties: true
```

### Frontend Error Handling

```typescript
// Both RSC and TanStack Query handle errors consistently
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json()
    throw new ApiError(
      response.status,
      errorData.error?.code || 'UNKNOWN_ERROR',
      errorData.error?.message || 'An error occurred',
      errorData.error?.details
    )
  }
  
  return response.json()
}
```

### Backend Error Handling

```python
# backend/src/app/api/exceptions.py
from fastapi import HTTPException
from fastapi.responses import JSONResponse

class ApiError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, details: dict = None):
        super().__init__(status_code, detail=message)
        self.code = code
        self.details = details

async def api_exception_handler(request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": {
                "code": exc.code,
                "message": exc.detail,
                "details": exc.details
            }
        }
    )
```


## 7. Breaking Change Detection

### Automated CI Checks

```yml
# .github/workflows/api-governance.yml
name: API Governance
on:
  pull_request:
    paths:
      - 'docs/specifications/api/**'
      - 'tests/mocks/handlers/**'

jobs:
  contract-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 2
      
      - name: Check OpenAPI breaking changes
        run: |
          oasdiff breaking \
            docs/specifications/api/openapi.yml \
            origin/main:docs/specifications/api/openapi.yml
      
      - name: Validate MSW handlers match OpenAPI
        run: |
          node scripts/validate-msw-contract.js
      
      - name: Generate TypeScript types
        run: |
          cd frontend
          openapi-generator generate \
            -i ../docs/specifications/api/openapi.yml \
            -g typescript-fetch \
            -o src/lib/api/generated/
```


## 8. Development Commands

### Project Setup Commands

```bash
# Install dependencies
cd backend && uv sync
cd frontend && pnpm install

# Start development servers
docker-compose up -d  # LocalStack and services
cd backend && uv run uvicorn app.main:app --reload
cd frontend && pnpm dev
```

### API Contract Commands

```bash
# Validate OpenAPI spec
spectral lint docs/specifications/api/openapi.yml

# Generate TypeScript types
cd frontend && openapi-generator generate \
  -i ../docs/specifications/api/openapi.yml \
  -g typescript-fetch \
  -o src/lib/api/generated/

# Update MSW handlers (manual step - ensure alignment)
# Edit tests/mocks/handlers/index.ts to match OpenAPI examples
```

### Testing Commands

```bash
# Run contract tests
cd backend && pytest tests/backend/e2e/contract/
cd frontend && pnpm test:contract

# Run full test suite
cd backend && pytest
cd frontend && pnpm test
```


## 9. Team Workflow Integration

### For API Design Changes

1. **Update OpenAPI specification** in `docs/specifications/api/`
2. **Lint and validate** the specification
3. **Update MSW handlers** to match new contract
4. **Regenerate TypeScript types** for frontend
5. **Update frontend API clients** if needed
6. **Implement backend changes** following the contract
7. **Run contract tests** to verify alignment
8. **Submit PR** with all coordinated changes

### For Frontend-First Development

1. **Design component interfaces** based on expected API data
2. **Update MSW handlers** with realistic mock data
3. **Implement frontend components** using MSW mocks
4. **Update OpenAPI specification** to match frontend expectations
5. **Generate backend stubs** from OpenAPI
6. **Implement backend** to fulfill the contract

### For Backend-First Development

1. **Design use cases** and domain models
2. **Update OpenAPI specification** based on domain models
3. **Generate TypeScript types** for frontend
4. **Update MSW handlers** to match OpenAPI examples  
5. **Implement backend** following Clean Architecture
6. **Update frontend** to use new API contract


By following this OpenAPI-first workflow, we ensure tight coordination between frontend and backend development while maintaining contract compliance across MSW mocks, Next.js RSC server-side fetching, TanStack Query client-side state management, and FastAPI backend implementation.