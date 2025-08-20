# Middleware Fix Plan

## Current State Analysis

### Problem
- Two `middleware.ts` files exist: one in `frontend/` (security headers) and one in `frontend/src/` (auth logic)
- Next.js only recognizes the root-level middleware (`frontend/middleware.ts`)
- Auth protection is currently **not working** - anonymous users can access protected routes

### Current Implementation Issues
1. `frontend/src/middleware.ts` is ignored by Next.js (wrong location)
2. Security headers middleware lacks auth protection
3. Missing automatic anonymous user sign-in handling
4. Redirect logic doesn't match the modal-based auth approach (Option C)

## Authentication Model (Clarified)

### User Types
1. **Anonymous Users** (auto-created on first visit)
   - Can view all public content
   - Can save/remove favorite posts
   - Can add comments to published posts
   - **Cannot** create/edit posts, save drafts, or view My Posts page

2. **Authenticated Users** (normal login)
   - Full access to all features and pages

### Auto Authentication Flow
- All users are automatically signed in as anonymous users on first visit
- This happens in the background (no user interaction required)
- Users can upgrade from anonymous to authenticated via modal/popup (Option C)

## Requirements from UI Specifications

### Protected Routes (Anonymous Users Blocked)
- `/create-post` - Create/edit blog post page
- `/my/posts` - My posts management page

### Anonymous User Accessible Routes
- `/` - Home page (public)
- `/posts/[id]` - Blog post detail (public)
- `/my/favorites` - Favorite posts (anonymous users can have favorites)

### Modal-Based Auth Flow (Option C)
- When anonymous users try to access protected features, show authentication modal
- No page redirects - keep user on current page
- After successful auth upgrade, allow access to the feature

## Best Practices Integration

### Next.js Middleware Best Practices
1. Single middleware file at project root (`frontend/middleware.ts`)
2. Combine multiple concerns (security + auth) in one middleware
3. Use proper matcher configuration to avoid unnecessary runs
4. Handle Edge Runtime limitations (no Node.js APIs)

### Security Headers
- Maintain existing CSP with nonce pattern
- Add WebSocket support for real-time features
- Environment-specific HSTS configuration

## Implementation Plan

### Phase 1: Consolidate Middleware Files
1. Merge both middleware implementations into `frontend/middleware.ts`
2. Remove `frontend/src/middleware.ts`
3. Combine security headers + auth logic

### Phase 2: Fix Authentication Logic
1. Update protected routes list based on UI specs
2. Change redirect behavior to support modal auth (Option C)
3. Handle automatic anonymous sign-in flow
4. Add proper cookie/session detection

### Phase 3: Enhance Security
1. Update CSP for WebSocket connections
2. Add proper CORS headers for API communication
3. Environment-specific security configurations

## Design Decisions & Trade-offs

### Decision 1: Modal vs Redirect for Auth
**Chosen:** Modal-based auth (Option C)
- **Pros:** Better UX, no page navigation, maintains context
- **Cons:** More complex state management, requires client-side auth handling
- **Implementation:** Middleware sets headers/flags for client to show modal

### Decision 2: Anonymous User Session Management
**Assumption:** Firebase handles anonymous user sessions automatically
- Middleware checks for any valid Firebase session (anonymous or authenticated)
- Differentiates between anonymous and authenticated users via Firebase claims

### Decision 3: Error Handling Strategy
**Recommended:** Graceful fallback
- If auth check fails, allow access but flag for client-side verification
- Avoid blocking users due to temporary auth service issues

## Questions for Clarification

### High Priority Questions
None - the auth model is now clear based on your explanation.

### Low Priority Questions (for questions.md)
1. Should anonymous users see different UI elements to encourage upgrading to full accounts?
2. What happens to anonymous user's favorites when they upgrade to authenticated account?
3. Should there be rate limiting for anonymous users on comment creation?

## Implementation Steps

### Step 1: Create New Middleware Structure
```typescript
// frontend/middleware.ts
export async function middleware(request: NextRequest) {
  // 1. Generate security nonce
  // 2. Apply security headers
  // 3. Check authentication for protected routes
  // 4. Handle anonymous user restrictions
  // 5. Set client-side flags for modal auth
}
```

### Step 2: Protected Route Configuration
```typescript
const protectedRoutes = [
  '/create-post',
  '/my/posts'
]

const anonymousRestrictedActions = [
  'create-post',
  'edit-post', 
  'save-draft'
]
```

### Step 3: Client-Side Integration
- Add middleware headers to trigger auth modals
- Handle auth state transitions
- Update UI based on user type (anonymous vs authenticated)

## Success Criteria

1. ✅ Single working middleware file at correct location
2. ✅ Security headers working for all routes
3. ✅ Anonymous users blocked from protected routes with modal prompt
4. ✅ Authenticated users have full access
5. ✅ WebSocket connections supported in CSP
6. ✅ No breaking changes to existing functionality

## Implementation Timeline

- **Phase 1:** 30 minutes (file consolidation)
- **Phase 2:** 45 minutes (auth logic fixes) 
- **Phase 3:** 15 minutes (security enhancements)
- **Total:** ~90 minutes

Ready to proceed with implementation once approved.