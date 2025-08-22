# Schema-Driven Frontend Development

This document explains how the frontend leverages OpenAPI specifications for type-safe development, automated code generation, and seamless API integration.

## 🎯 Overview

Our frontend follows a **schema-first** approach where all TypeScript types, React Query hooks, and MSW mocks are automatically generated from the OpenAPI specification in `openapi/spec/`. This ensures complete type safety from API contracts down to React components.

### Key Benefits

- ✅ **End-to-end Type Safety**: From API response to React component props
- ✅ **Zero Manual Typing**: All types generated from OpenAPI schemas
- ✅ **Automated Mocks**: MSW handlers with realistic data from OpenAPI examples
- ✅ **React Query Integration**: Type-safe hooks for data fetching and mutations
- ✅ **IntelliSense Support**: Full autocompletion and validation in IDE

## 📁 Frontend Architecture

```
frontend/src/
├── lib/api/
│   ├── generated/                    # 🚫 Auto-generated (don't edit)
│   │   ├── client.ts                 # React Query hooks
│   │   ├── client.msw.ts             # MSW mock handlers  
│   │   └── schemas/                  # TypeScript interfaces
│   │       ├── index.ts              # All type exports
│   │       ├── blogPost.ts           # BlogPost interface
│   │       ├── createPostRequest.ts  # Form types
│   │       └── ...                   # Other generated types
│   ├── customFetch.ts                # Custom fetch with Firebase auth
│   └── posts.ts                      # Custom API logic (optional)
│
├── components/
│   ├── blog/
│   │   ├── BlogPostForm.tsx          # Uses CreatePostRequest type
│   │   ├── PostCard.tsx              # Uses BlogPostSummary type
│   │   └── CommentsSection.tsx       # Uses Comment[] type
│   └── ui/                           # shadcn/ui components
│
├── mocks/
│   ├── handlers/index.ts             # MSW handler setup
│   ├── browser.ts                    # Browser MSW setup
│   └── server.ts                     # Node MSW setup (testing)
│
└── types/                            # Custom frontend-only types
```

## 🔄 Development Workflow

### 1. Schema-to-Code Generation

When OpenAPI schemas change, regenerate frontend code:

```bash
# From project root
pnpm oas:fe
```

This runs:
1. `pnpm oas:bundle` - Bundles OpenAPI spec
2. `pnpm orval:gen` - Generates TypeScript code

### 2. Generated TypeScript Types

**OpenAPI Schema** (`openapi/spec/components/schemas/blog-post.yml`):
```yaml
type: object
properties:
  id:
    type: string
    example: "post-123"
  title:
    type: string
    example: "Getting Started with Next.js"
  status:
    type: string
    enum: [draft, published]
    example: "published"
required: [id, title, status]
```

**Generated TypeScript** (`frontend/src/lib/api/generated/schemas/blogPost.ts`):
```typescript
export interface BlogPost {
  /** Unique identifier for the blog post */
  id: string;
  /** Title of the blog post */
  title: string;
  /** Current status of the blog post */
  status: BlogPostStatus;
}

export type BlogPostStatus = 'draft' | 'published';
```

### 3. Generated React Query Hooks

**Generated Hooks** (`frontend/src/lib/api/generated/client.ts`):
```typescript
// GET /posts hook
export const useGetBlogPosts = (
  params?: GetBlogPostsParams,
  options?: UseQueryOptions<BlogPostListResponse>
) => {
  return useQuery({
    queryKey: ['posts', params],
    queryFn: () => getBlogPosts(params),
    ...options
  });
};

// POST /posts mutation
export const useCreateBlogPost = (
  options?: UseMutationOptions<BlogPostResponse, Error, CreatePostRequest>
) => {
  return useMutation({
    mutationFn: (data: CreatePostRequest) => createBlogPost(data),
    ...options
  });
};
```

### 4. Component Implementation

Use generated types for complete type safety:

**Example**: `frontend/src/components/blog/PostCard.tsx`
```typescript
import type { BlogPostSummary } from '@/lib/api/generated/schemas'

interface PostCardProps {
  post: BlogPostSummary  // ✅ Generated from OpenAPI
  onReadMore?: (postId: string) => void
}

export function PostCard({ post, onReadMore }: PostCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{post.title}</CardTitle>  {/* ✅ Type-safe */}
        <Badge variant={post.status === 'published' ? 'default' : 'secondary'}>
          {post.status}  {/* ✅ Enum validation */}
        </Badge>
      </CardHeader>
      <CardContent>
        <p>{post.excerpt}</p>
        <p className="text-sm text-muted-foreground">
          By {post.author} • {formatDate(post.publishedAt)}
        </p>
      </CardContent>
    </Card>
  )
}
```

### 5. Data Fetching

Use generated hooks in page components:

**Example**: `frontend/src/app/page.tsx`
```typescript
import { useGetBlogPosts } from '@/lib/api/generated/client'
import { PostCard } from '@/components/blog/PostCard'

export default function HomePage() {
  const { data, isLoading, error } = useGetBlogPosts({
    page: 1,
    limit: 10
  })

  if (isLoading) return <div>Loading posts...</div>
  if (error) return <div>Error: {error.message}</div>
  if (!data?.data.posts.length) return <div>No posts found</div>

  return (
    <div className="grid gap-6">
      {data.data.posts.map(post => (
        <PostCard key={post.id} post={post} />  {/* ✅ Type-safe */}
      ))}
    </div>
  )
}
```

### 6. Form Handling

Create forms using generated request types:

**Example**: `frontend/src/components/blog/BlogPostForm.tsx`
```typescript
import type { CreatePostRequest } from '@/lib/api/generated/schemas'
import { useCreateBlogPost } from '@/lib/api/generated/client'

export function BlogPostForm() {
  const createMutation = useCreateBlogPost({
    onSuccess: (response) => {
      // response is typed as BlogPostResponse
      console.log('Created post:', response.data.id)
    }
  })
  
  const handleSubmit = (formData: CreatePostRequest) => {
    createMutation.mutate(formData)  // ✅ Type-safe API call
  }

  // Form implementation with validation based on OpenAPI schema
}
```

## 🧪 Testing Integration

### Generated MSW Mocks

MSW handlers are automatically generated from OpenAPI examples:

**Generated** (`frontend/src/lib/api/generated/client.msw.ts`):
```typescript
export const getGetBlogPostsResponseMock = (): BlogPostListResponse => ({
  "status": "success",
  "data": {
    "posts": [{
      "id": "post-123",
      "title": "Getting Started with Next.js",
      "excerpt": "Learn the basics of Next.js...",
      "author": "John Doe",
      "publishedAt": "2024-01-15T10:30:00Z"
      // ✅ Uses examples from OpenAPI spec
    }]
  }
})

export const getBlogPostAPIMock = () => [
  http.get('/posts', () => {
    return HttpResponse.json(getGetBlogPostsResponseMock())
  }),
  // ... other handlers
]
```

### Test Setup

**File**: `frontend/src/mocks/handlers/index.ts`
```typescript
import { getBlogPostAPIMock } from '@/lib/api/generated/client.msw'

// Use generated handlers as base
const apiHandlers = getBlogPostAPIMock()

// Add custom error handlers for testing edge cases
const errorHandlers = [
  http.get('/posts/error-500', () => {
    return HttpResponse.json({
      status: 'error',
      error: { code: 'INTERNAL_SERVER_ERROR', message: 'Something went wrong' }
    }, { status: 500 })
  })
]

export const handlers = [
  ...apiHandlers,
  ...errorHandlers
]
```

### Component Testing

Test components with type-safe mock data:

```typescript
import { render, screen } from '@testing-library/react'
import { PostCard } from './PostCard'
import type { BlogPostSummary } from '@/lib/api/generated/schemas'

const mockPost: BlogPostSummary = {
  id: "post-123",
  title: "Test Post",
  excerpt: "Test excerpt",
  author: "Test Author",
  publishedAt: "2024-01-15T10:30:00Z"
}  // ✅ Type-safe test data

test('renders post card correctly', () => {
  render(<PostCard post={mockPost} />)
  expect(screen.getByText('Test Post')).toBeInTheDocument()
  expect(screen.getByText('Test Author')).toBeInTheDocument()
})
```

## ⚙️ Configuration

### Orval Configuration

**File**: `orval.config.ts` (project root)
```typescript
import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: {
      target: "openapi/dist/openapi.yml",  // Bundled OpenAPI spec
    },
    output: {
      target: "frontend/src/lib/api/generated/client.ts",
      schemas: "frontend/src/lib/api/generated/schemas",
      client: "react-query",
      httpClient: "fetch",
      mode: "split",                        // Separate files for schemas
      clean: true,                          // Clean output directory
      mock: {
        type: "msw",
        useExamples: true,                  // Use OpenAPI examples
        generateEachHttpStatus: false,      // Avoid faker dependency
      },
      override: {
        query: {
          useQuery: true,
          useMutation: true,
        },
        mutator: {
          path: "frontend/src/lib/api/customFetch.ts",
          name: "customFetch",              // Custom fetch with auth
        },
      },
    },
  },
});
```

### Custom Fetch with Firebase Auth

**File**: `frontend/src/lib/api/customFetch.ts`
```typescript
export const customFetch = async <T>(
  url: string,
  options: RequestInit = {}
): Promise<T> => {
  // Add Firebase auth token to requests
  const token = await getAuthToken()
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}
```

## 📋 Best Practices

### 1. Type Usage

```typescript
// ✅ Good: Import specific types
import type { BlogPost, CreatePostRequest } from '@/lib/api/generated/schemas'

// ✅ Good: Use generated types for props
interface PostCardProps {
  post: BlogPost
}

// ❌ Bad: Manual type definitions that duplicate OpenAPI
interface ManualPostType {
  id: string
  title: string
  // ...
}
```

### 2. Hook Usage

```typescript
// ✅ Good: Use generated hooks with proper error handling
const { data, isLoading, error } = useGetBlogPosts({ page: 1, limit: 10 })

if (error) {
  // error is properly typed
  console.error('API Error:', error.message)
}

// ✅ Good: Mutations with callbacks
const createMutation = useCreateBlogPost({
  onSuccess: (response) => {
    // response.data is properly typed as BlogPost
    router.push(`/posts/${response.data.id}`)
  },
  onError: (error) => {
    // Handle error
  }
})
```

### 3. Mock Usage

```typescript
// ✅ Good: Extend generated mocks for specific test cases
const customHandlers = [
  ...getBlogPostAPIMock(),
  http.get('/posts/special-case', () => {
    return HttpResponse.json({
      status: 'success',
      data: { /* custom test data */ }
    })
  })
]
```

## 🚀 Development Commands

### Daily Workflow

```bash
# 1. When OpenAPI schemas change, regenerate frontend code
pnpm oas:fe

# 2. Start development server (with MSW mocking)
cd frontend && pnpm dev

# 3. Type check
cd frontend && pnpm typecheck

# 4. Run tests with generated mocks
cd frontend && pnpm test
```

### Validation

```bash
# Ensure generated code compiles without errors
cd frontend && pnpm typecheck

# Verify MSW handlers work correctly
cd frontend && pnpm test src/components/blog/
```

## 🔍 Troubleshooting

### Common Issues

1. **Types Not Updating After Schema Changes**
   ```bash
   # Solution: Regenerate types
   pnpm oas:fe
   cd frontend && pnpm typecheck
   ```

2. **MSW Mocks Not Working**
   - Check: MSW is properly set up in `src/mocks/browser.ts`
   - Verify: Mock handlers are imported in `src/mocks/handlers/index.ts`
   - Update: Run `pnpm orval:gen` to regenerate mocks

3. **Authentication Errors**
   - Ensure: `customFetch.ts` properly adds Firebase auth tokens
   - Check: Firebase auth is initialized before API calls

4. **Type Errors in Components**
   - Import: Use generated types from `@/lib/api/generated/schemas`
   - Verify: Component props match generated interface exactly

## 📚 Related Files

- **OpenAPI Specification**: `openapi/spec/openapi.yml`
- **Schema Guidelines**: `openapi/openapi-schema-guideline.md`
- **Generated Types**: `frontend/src/lib/api/generated/schemas/`
- **Generated Hooks**: `frontend/src/lib/api/generated/client.ts`
- **Generated Mocks**: `frontend/src/lib/api/generated/client.msw.ts`

## ✅ Success Checklist

A properly implemented schema-driven frontend should have:

- [ ] **Zero manual type definitions** for API data structures
- [ ] **IntelliSense support** for all API-related code
- [ ] **Compile-time validation** of API contracts in components
- [ ] **Automated mock generation** with realistic examples from OpenAPI
- [ ] **Type-safe error handling** using generated error types
- [ ] **Consistent data fetching** patterns using generated React Query hooks
- [ ] **Up-to-date generated code** that matches current OpenAPI specification

This approach ensures robust, maintainable frontend code with excellent developer experience and complete type safety from API to UI.