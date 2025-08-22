# Frontend Directory Structure Guide

This document outlines the recommended directory structure for the Next.js + TypeScript blog post application, based on our coding guidelines and UI specifications.

## 1. Overview

Our frontend follows Next.js 15.x App Router conventions with a focus on:
- **Server Components by default** with selective Client Components
- **Co-location** of related files (components, styles, utilities)
- **Clear separation** between public and authenticated routes
- **Modular architecture** with reusable components

## 2. Frontend Directory Structure

```
frontend/
├── src/
│   ├── app/                     # Next.js App Router (all routes)
│   ├── components/              # Reusable components
│   ├── lib/                     # Shared utilities and configurations
│   ├── hooks/                   # Custom React hooks
│   ├── styles/                  # Global styles and Tailwind config
│   └── types/                   # TypeScript type definitions
├── public/                      # Static assets
├── .env.development                   # Environment variables (not committed)
├── .env.example                 # Example environment variables
├── next.config.ts               # Next.js configuration
├── tsconfig.json                # TypeScript configuration
├── biome.json                   # Biome linter/formatter config
├── tailwind.config.js           # Tailwind CSS configuration
├── package.json                 # Dependencies and scripts
├── docker-compose.yml           # Local development container
└── Dockerfile                   # Container configuration
```

## 3. App Router Structure (`src/app/`)

Based on our UI page specifications, the routing structure follows the blog post application requirements:

```
src/app/
├── layout.tsx                   # Root layout (Server Component)
├── page.tsx                     # Home page - blog post list (SSR)
├── loading.tsx                  # Global loading fallback
├── error.tsx                    # Global error boundary
├── not-found.tsx                # 404 page
├── globals.css                  # Global CSS imports
│
├── posts/                       # Blog post routes
│   ├── [id]/
│   │   ├── page.tsx            # Individual post page (SSR)
│   │   ├── loading.tsx         # Post loading state
│   │   └── error.tsx           # Post error boundary
│   └── layout.tsx              # Optional posts layout
│
├── create-post/                 # Post creation (CSR)
│   ├── page.tsx                # Create post page (Client Component)
│   ├── components/             # Page-specific components
│   │   ├── BlogPostForm.tsx    # Main form component
│   │   ├── RichTextEditor.tsx  # Content editor
│   │   └── PublishControls.tsx # Save/publish buttons
│   └── actions.ts              # Server Actions for post creation
│
└── api/                        # API Route Handlers
    ├── posts/
    │   ├── route.ts            # GET /api/posts, POST /api/posts
    │   └── [id]/
    │       ├── route.ts        # GET/PUT /api/posts/[id]
    │       └── comments/
    │           └── route.ts    # Comments endpoints
    └── auth/                   # Firebase Auth endpoints
        └── route.ts
```

## 4. Components Structure (`src/components/`)

Organized by type and reusability level:

```
src/components/
├── ui/                         # Base UI components (shadcn/ui)
│   ├── button.tsx
│   ├── input.tsx
│   ├── card.tsx
│   ├── toast.tsx
│   └── index.ts               # Barrel exports
│
├── layout/                    # Layout components
│   ├── Header.tsx             # Site header with navigation
│   ├── Footer.tsx             # Site footer
│   └── Navigation.tsx         # Main navigation
│
├── blog/                      # Blog-specific components
│   ├── PostCard.tsx           # Blog post summary card
│   ├── PostList.tsx           # Container for post cards
│   ├── BlogPostContent.tsx    # Full post content display
│   ├── CommentsSection.tsx    # Comments (Client Component)
│   ├── CommentForm.tsx        # Add comment form
│   └── Pagination.tsx         # Pagination controls
│
└── common/                    # Common utility components
    ├── LoadingSpinner.tsx
    ├── ErrorBoundary.tsx
    └── Suspense.tsx
```

## 5. Library Structure (`src/lib/`)

Shared utilities and configurations:

```
src/lib/
├── firebase/                  # Firebase configuration
│   ├── config.ts             # Firebase app initialization
│   ├── auth.ts               # Authentication utilities
│   └── firestore.ts          # Firestore helpers
│
├── api/                       # API utilities
│   ├── client.ts             # API client configuration
│   ├── posts.ts              # Posts API functions
│   └── comments.ts           # Comments API functions
│
├── utils/                     # General utilities
│   ├── cn.ts                 # Tailwind class name utility
│   ├── date.ts               # Date formatting
│   ├── validation.ts         # Zod schemas
│   └── constants.ts          # App constants
│
└── hooks/                     # Custom hooks (if not in top-level hooks/)
    ├── useAuth.ts            # Authentication hook
    ├── usePosts.ts           # Posts data fetching
    └── useLocalStorage.ts    # Local storage hook
```

## 6. Type Definitions (`src/types/`)

```
src/types/
├── index.ts                   # Main type exports
├── blog.ts                    # Blog post types
├── user.ts                    # User types
├── api.ts                     # API response types
└── components.ts              # Component prop types
```

## 7. Styling Structure (`src/styles/`)

```
src/styles/
├── globals.css                # Global styles and Tailwind imports
├── components.css             # Component-specific styles
└── utilities.css              # Custom utility classes
```

## 8. Page-Specific Organization

For complex pages, follow the co-location pattern from `03_routing.md`:

```
src/app/create-post/
├── page.tsx                   # Main page component
├── components/                # Page-specific components
│   ├── BlogPostForm.tsx
│   ├── TagSelector.tsx
│   └── PublishControls.tsx
├── actions.ts                 # Server Actions
├── types.ts                   # Page-specific types
├── utils.ts                   # Page-specific utilities
└── styles.module.css          # Page-specific styles (if needed)
```

## 9. Key Principles

### Server vs Client Components
- **Pages**: Use Server Components for SSR pages (`/`, `/posts/[id]`)
- **Forms**: Use Client Components for interactive pages (`/create-post`)
- **Comments**: Client Components for real-time interactions
- **Navigation**: Server Components with selective client hydration

### File Naming Conventions
- **Components**: PascalCase (`BlogPostForm.tsx`)
- **Directories**: kebab-case (`create-post/`)
- **API Routes**: `route.ts`
- **Pages**: `page.tsx`
- **Utilities**: camelCase (`formatDate.ts`)

### Import Alias
Using `@/*` alias for clean imports:
```typescript
import { Button } from '@/components/ui/button'
import { BlogPostForm } from '@/components/blog/BlogPostForm'
import { createPost } from '@/lib/api/posts'
```

This structure supports our Next.js 15.x + TypeScript + Firebase Auth application while maintaining clear separation of concerns and following modern React patterns.