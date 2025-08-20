# Favorite Posts Page

## 1. Page Overview

### Description
- Displays the current user’s favorited blog posts (supports both anonymous and authenticated users). If a visitor is not authenticated, the app performs automatic anonymous sign-in, then loads favorites linked to that anonymous user’s UID. This page uses Client-Side Rendering (CSR).

### URL
- Assumption: `/my/favorites` (to mirror `/my/posts`). Please confirm.

### Access
- Public (auto anonymous sign-in if unauthenticated). Content is user-specific by Firebase UID.

## 2. Layout and Structure

This page composes existing, reusable components. For component prop-level details, refer to Storybook.

### Primary Components
- `Header` — global site header with brand and navigation (includes Favorites link).
- `PostList` — list container rendering favorited posts as `PostCard` items.
- `EmptyState` — shown when the user has no favorites.
- `Pagination` — next/previous (and page number) controls.
- `Footer` — global site footer.

### Responsive Behavior
- Single-column flow on narrow screens; items stack vertically.
- On wider viewports, cards use a comfortable grid; touch targets remain at least 44px.

## 3. Actions and Interactions

### Initialize and Load Favorites (CSR)

#### Trigger
- Page mounts at `/my/favorites`.

#### Behavior
1. Ensure a Firebase auth session exists; if none, perform anonymous sign-in.
2. Obtain the current user ID (`uid`) from auth state.
3. Read querystring for `page` and `limit` (optional) to initialize UI state.
4. Fetch the first page of favorited posts for `uid`.
5. Show a lightweight skeleton while loading; on error, show a non-blocking inline error with retry.

#### Component Reference
- `PostList`, `Pagination`, `EmptyState`.

### Favorite/Unfavorite from Post Detail

#### Trigger
- User toggles “Favorite” on the Post Detail page (`/posts/[id]`).

#### Behavior
1. If not authenticated, perform anonymous sign-in.
2. Toggle favorite state:
   - If not currently favorited, send `POST /posts/[id]/favorite`.
   - If currently favorited, send `DELETE /posts/[id]/favorite`.
3. Update UI state (optimistic where reasonable); show toast on failure and revert.

### Remove from Favorites (List)

#### Trigger
- User clicks “Remove” on an item within the Favorites list.

#### Behavior
1. Send `DELETE /posts/[id]/favorite`.
2. Optimistically update the list or refetch; on error, show toast and revert.

### Navigate to Post Details

#### Trigger
- User clicks a `PostCard` title or “View”.

#### Behavior
- Navigate to `/posts/[id]`. Use standard link navigation; client prefetch may be enabled when available.

#### Component Reference
- `PostCard`.

## 4. Data Requirements

This page reads and mutates user-scoped favorites. For complete request/response schemas, refer to the OpenAPI spec when available.

### `GET /users/[uid]/favorites`

#### Description
- Returns a paginated list of posts favorited by the specified user.

#### Query Params
- `page` (number, default `1`), `limit` (number, default `10`).

### `POST /posts/[id]/favorite`

#### Description
- Marks a post as a favorite for the current user (anonymous or authenticated).

### `DELETE /posts/[id]/favorite`

#### Description
- Removes a post from the current user’s favorites.

## 5. Error States and Empty States

- Empty: Show `EmptyState` with copy like “No favorites yet” and a suggestion to “Browse posts”.
- Load Error: Inline error with a “Retry” action; preserve pagination state.
- Auth Error: Display a generic error and provide a “Try Again” action to re-initiate auth (anonymous sign-in).

## 6. Accessibility

- Manage focus on content updates (e.g., after pagination changes).
- Provide `aria-live="polite"` regions for loading and result counts.
- Ensure keyboard navigation for list items and remove actions.

## 7. Navigation

- Add a persistent `Favorites` link to the global `Header` that routes to `/my/favorites` (Assumption; confirm). The transition follows the standard slide-in animation.

