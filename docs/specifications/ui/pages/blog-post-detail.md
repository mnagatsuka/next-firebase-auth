# Individual Blog Post Page

## 1. Page Overview

### Description
- Displays the full content of a single blog post. This page uses **Server-Side Rendering (SSR)** for optimal SEO and fast initial page loads. Based on the post's unique ID in the URL, the server fetches and renders the specific post's content.

### URL
- `/posts/[id]`

### Access
- Public (no authentication required).

## 2. Layout and Structure

This page is composed of the following components. For component details, see the **Storybook**.

### Primary Components
- `Header` (Standard application header, at the top)
- `BlogPostContent` (Main article content with title, author, date, and body)
- `FavoriteToggle` (Star icon/button to add or remove from Favorites)
- `CommentsSection` (Client-side rendered comments with add functionality)

### Responsive Behavior

The main content uses a single-column layout optimized for reading. On desktop, the content has comfortable margins. On mobile, the layout adapts with full-width content and appropriate spacing.

## 3. Actions and Interactions

This section defines the unique behavior and logic that integrates the components.

### Initial SSR Render

#### Trigger
- HTTP GET request to `/posts/[id]`.

#### Behavior
1. Server fetches the blog post data using the ID from the URL via `GET /posts/[id]`.
2. Returns fully rendered HTML including post content for optimal SEO.
3. Client hydrates to enable interactive features like comments.
4. If post is not found, displays 404 error page.

#### Component Reference
- [Link to BlogPostContent Storybook entry](https://storybook-link)

### Load Comments

#### Trigger
- Page loads and the `CommentsSection` component mounts (Client-Side Rendering).

#### Behavior
1. The client establishes a WebSocket connection to the comments service.
2. An initial API call to `GET /posts/[id]/comments` is made. This HTTP request does not return the comments directly. Instead, it returns an acknowledgment and triggers the backend to start sending comments over the established WebSocket connection.
3. The client listens for messages on the WebSocket.
4. As comment data arrives via WebSocket messages, the `CommentsSection` is updated in real-time without full page refreshes.

#### Component Reference
- [Link to CommentsSection Storybook entry](https://storybook-link)

### Add Comment

#### Trigger
- User submits a comment through the comment form in `CommentsSection`.

#### Behavior
1. API call to `POST /posts/[id]/comments` is made.
2. Upon success, the new comment is added to the comments list without page refresh.
3. Comment form is cleared.

#### Component Reference
- [Link to CommentsSection Storybook entry](https://storybook-link)

### Favorite / Unfavorite Post

#### Trigger
- User clicks the star icon/button in the `BlogPostContent` header.

#### Behavior
1. If not authenticated, perform anonymous sign-in.
2. Toggle favorite state:
   - If not currently favorited, call `POST /posts/[id]/favorite` and reflect “Favorited”.
   - If currently favorited, call `DELETE /posts/[id]/favorite` and reflect “Favorite”.
3. Use optimistic UI; on error, revert and show a toast.

#### Component Reference
- `FavoriteToggle` (star button), `BlogPostContent`.

## 4. Data Requirements

This section outlines the API endpoints this page interacts with. For complete request and response schemas, refer to the **OpenAPI spec**.

### `GET /posts/[id]`

#### Description
- Fetches the complete details of a single blog post by its ID.

#### API Spec Reference
- See the `getPostById` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec)

### `GET /posts/[id]/comments`

#### Description
- Initiates the retrieval of comments for a specific blog post. This endpoint returns an immediate acknowledgment, and the actual comment data is delivered to the client via an established WebSocket connection.

#### API Spec Reference
- See the `getPostComments` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec)

### `POST /posts/[id]/comments`

#### Description
- Creates a new comment on a specific blog post.

#### API Spec Reference
- See the `createPostComment` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec)

### `POST /posts/[id]/favorite`

#### Description
- Marks a post as a favorite for the current user (anonymous or authenticated).

### `DELETE /posts/[id]/favorite`

#### Description
- Removes a post from the current user’s favorites.