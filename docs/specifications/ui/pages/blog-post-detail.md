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
- `CommentsSection` (Client-side rendered comments with add functionality)

### Responsive Behavior

The main content uses a single-column layout optimized for reading. On desktop, the content has comfortable margins. On mobile, the layout adapts with full-width content and appropriate spacing.

## 3. Actions and Interactions

This section defines the unique behavior and logic that integrates the components.

### Initial SSR Render

#### Trigger
- HTTP GET request to `/posts/[id]`.

#### Behavior
1. Server fetches the blog post data using the ID from the URL via `GET /api/posts/[id]`.
2. Returns fully rendered HTML including post content for optimal SEO.
3. Client hydrates to enable interactive features like comments.
4. If post is not found, displays 404 error page.

#### Component Reference
- [Link to BlogPostContent Storybook entry](https://storybook-link)

### Load Comments

#### Trigger
- Page loads and the `CommentsSection` component mounts (Client-Side Rendering).

#### Behavior
1. After the main post content is rendered, the comments section loads dynamically.
2. API call to `GET /api/posts/[id]/comments` fetches existing comments.
3. Comments are rendered without full page refreshes.

#### Component Reference
- [Link to CommentsSection Storybook entry](https://storybook-link)

### Add Comment

#### Trigger
- User submits a comment through the comment form in `CommentsSection`.

#### Behavior
1. API call to `POST /api/posts/[id]/comments` is made.
2. Upon success, the new comment is added to the comments list without page refresh.
3. Comment form is cleared.

#### Component Reference
- [Link to CommentsSection Storybook entry](https://storybook-link)

## 4. Data Requirements

This section outlines the API endpoints this page interacts with. For complete request and response schemas, refer to the **OpenAPI spec**.

### `GET /api/posts/[id]`

#### Description
- Fetches the complete details of a single blog post by its ID.

#### API Spec Reference
- See the `getPostById` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec)

### `GET /api/posts/[id]/comments`

#### Description
- Fetches all comments associated with a specific blog post for client-side rendering.

#### API Spec Reference
- See the `getPostComments` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec)

### `POST /api/posts/[id]/comments`

#### Description
- Creates a new comment on a specific blog post.

#### API Spec Reference
- See the `createPostComment` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec)