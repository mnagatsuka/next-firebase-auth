# Home Page

## 1. Page Overview

### Description
- Public landing page listing recent blog posts. Optimized for speed and SEO with Server-Side Rendering (SSR). Hydrates on the client for interactions like pagination and navigation.

### URL
- `/`

### Access
- Public (no authentication required).

## 2. Layout and Structure

This page composes existing, reusable components. For component prop-level details, refer to Storybook.

### Primary Components
- `Header` — global site header with brand and navigation.
- `PostList` — container that renders a list of `PostCard` items.
- `PostCard` — shows title, excerpt, author, published date, and a "Read more" action.
- `Pagination` — next/previous (and page number) controls.
- `Footer` — global site footer.

### Responsive Behavior
- Uses a single-column flow; `PostCard` items stack vertically on small screens and form a two-column grid on wider viewports when space allows.
- Touch targets remain at least 44px; typography scales with container width.

## 3. Actions and Interactions

### Initial SSR Render

#### Trigger
- HTTP GET to `/`.

#### Behavior
1. Server fetches the first page of posts (e.g., `GET /posts?limit=10&page=1`).
2. Returns fully rendered HTML for better SEO and fast first paint.
3. Client hydrates to enable pagination and navigation interactions.

#### Component Reference
- `PostList`, `PostCard` (see Storybook entries).

### Paginate Posts

#### Trigger
- User clicks a page number or next/previous in `Pagination`.

#### Behavior
1. Update the query string (e.g., `/?page=2`) and request the corresponding data.
2. While loading, show a lightweight skeleton for `PostCard` items.
3. Replace `PostList` with new results; focus moves to the list container for accessibility.

#### Component Reference
- `Pagination`, `PostList`.

### Navigate to Post Details

#### Trigger
- User clicks a `PostCard` title or "Read more".

#### Behavior
- Navigate to `/posts/[id]` (details page). Use standard link navigation for crawlability; client prefetch may be enabled when available.

#### Component Reference
- `PostCard`.

### Navigate to My Posts

#### Trigger
- User clicks "My Posts" in `Header` (visible only for non-anonymous users).

#### Behavior
- Navigate to `/my/posts`. Use standard link navigation; client prefetch may be enabled when available.

#### Component Reference
- `Header`.

### Navigate to Favorite Posts

#### Trigger
- User clicks "Favorites" in `Header`.

#### Behavior
- Navigate to `/my/favorites`. Use standard link navigation; client prefetch may be enabled when available.

#### Component Reference
- `Header`.

## 4. Data Requirements

### `GET /posts`

#### Description
- Returns a paginated list of posts for listing on the home page.

#### Query Params
- `page` (number, default `1`), `limit` (number, default `10`).

#### API Spec Reference
- See `listPosts` in the OpenAPI specification (placeholder link).

### `GET /posts/[id]` (linked page)

#### Description
- Used by the details page; referenced here for navigation completeness.

#### API Spec Reference
- See `getPostById` in the OpenAPI specification (placeholder link).
