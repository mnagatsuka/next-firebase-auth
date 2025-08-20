# My Posts Page

## 1. Page Overview

### Description
- Displays only the current user’s blog posts. This page is available to authenticated non-anonymous users only. Anonymous users cannot access this page.

### URL
- `/my/posts`

### Access
- Authenticated (non-anonymous) users only. Anonymous users are redirected (e.g., to Home or Signup).

## 2. Layout and Structure

This page composes existing, reusable components. For component prop-level details, refer to Storybook.

### Primary Components
- `Header` — global site header with brand and navigation.
- `Toolbar` — contains a status filter (All/Published/Drafts) and optional search input.
- `PostList` — list container rendering user-owned posts as `PostRow`/`PostCard` items.
- `EmptyState` — shown when the user has no posts for the current filter.
- `Pagination` — next/previous (and page number) controls.
- `Footer` — global site footer.

### Responsive Behavior
- Single-column flow on narrow screens; items stack vertically.
- On wider viewports, cards/rows use comfortable spacing; controls remain reachable and at least 44px touch targets.

## 3. Actions and Interactions

### Enter via Header Navigation

#### Trigger
- User clicks "My Posts" in `Header` from any page (e.g., Home).

#### Behavior
1. Navigate to `/my/posts`.
2. If no auth session exists, perform anonymous sign-in.
3. After auth is ready, fetch and render the user’s posts; show a lightweight skeleton during auth/data fetch.

#### Component Reference
- `Header`, `PostList`.

### Initialize and Load User Posts (CSR)

#### Trigger
- Page mounts at `/my/posts`.

#### Behavior
1. Verify user is authenticated and non-anonymous; if anonymous, redirect.
2. Obtain the current user ID (`uid`) from auth state.
3. Read querystring for `page`, `limit`, and `status` (optional) to initialize UI state.
4. Fetch the first page of posts for `uid` using the selected status filter (default: All).
5. Show a lightweight skeleton while loading; on error, show a non-blocking inline error with retry.

#### Component Reference
- `Toolbar`, `PostList`, `Pagination`, `EmptyState` (see Storybook entries).

### Filter by Status (All / Published / Drafts)

#### Trigger
- User selects a status in `Toolbar`.

#### Behavior
1. Update internal state and sync the `status` querystring parameter.
2. Reset pagination to page 1.
3. Re-fetch posts for the selected status; display skeleton during load.

#### Component Reference
- `Toolbar`, `PostList`.

### Paginate

#### Trigger
- User clicks a page number or next/previous in `Pagination`.

#### Behavior
1. Update the `page` querystring and fetch the corresponding results.
2. While loading, show a skeleton for list items.
3. Move focus to the list container after content updates for accessibility.

#### Component Reference
- `Pagination`, `PostList`.

### Navigate to View Post

#### Trigger
- User clicks a post title or a “View” action on a list item.

#### Behavior
- Navigate to `/posts/[id]` (details page). Use standard link navigation; client prefetch may be enabled when available.

#### Component Reference
- `PostRow`/`PostCard`.

### Navigate to Edit Post

#### Trigger
- User clicks an “Edit” action on a list item.

#### Behavior
- Navigate to `/create-post?id=[id]` to edit the existing post (only for non-anonymous users).

#### Component Reference
- `PostRow`/`PostCard`.

## 4. Data Requirements

This page reads user-scoped post data. For complete request/response schemas, refer to the OpenAPI spec.

### `GET /users/[uid]/posts`

#### Description
- Returns a paginated list of posts owned by the specified user.

#### Query Params
- `status` (optional: `published` | `draft`), `page` (number, default `1`), `limit` (number, default `10`).

#### Notes
- If the backend does not expose a user-scoped route, an equivalent query such as `GET /posts?ownerId=[uid]&status=&page=&limit=` can be used.

### `GET /posts/[id]` (linked page)

#### Description
- Linked for navigation to the details page.

### `PUT /posts/[id]` (linked page)

#### Description
- Used by the edit page referenced here for navigation only.

## 5. Error States and Empty States

- Empty: Show `EmptyState` with copy like “No posts yet” and a link to “Create a Post”.
- Load Error: Inline error with a “Retry” action; preserve current filter/pagination state.
- Auth Error: Display a generic error and provide a “Try Again” action to re-initiate auth.

## 6. Accessibility

- Manage focus on content updates (e.g., after pagination/filter changes).
- Provide `aria-live="polite"` regions for loading and result counts.
- Ensure keyboard navigation for filters, pagination, and item actions.
