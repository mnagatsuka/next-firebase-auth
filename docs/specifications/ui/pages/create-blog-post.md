# Create/Edit Blog Post Page

## 1. Page Overview

### Description
- An administrative page where a user can write or edit a blog post. This entire page uses **Client-Side Rendering (CSR)** as it's a highly interactive form that handles state, validation, and API calls to save or update data. Since this page is not for public viewing, SEO is not a factor.

### URL
- `/create-post`

### Access
- Authenticated Users only.

## 2. Layout and Structure

This page is composed of the following components. For component details, see the **Storybook**.

### Primary Components
- `Header` (Standard application header, at the top)
- `BlogPostForm` (The main form component containing fields for title, content, tags, etc.)
- `Button` (for "Save Draft", "Publish", "Cancel")

### Responsive Behavior

The main content area (containing the `BlogPostForm`) will use a single-column layout that is responsive and adapts well to various screen sizes, from desktop to mobile. Form fields will stack vertically on smaller screens.

## 3. Actions and Interactions

This section defines the unique behavior and logic that integrates the components.

### Initialize Form for Editing

#### Trigger
- Page loads with a specific blog post ID (e.g., via a query parameter like `/create-post?id=123`).

#### Behavior
1. An API call is made to `GET /posts/[id]` to fetch the existing blog post data.
2. A loading state is displayed while fetching the data.
3. Upon successful fetch, the `BlogPostForm` is pre-filled with the retrieved data.
4. If the post is not found or an error occurs, an appropriate error message is displayed, or the user is redirected.

#### Component Reference
- [Link to BlogPostForm Storybook entry](https://www.google.com/search?q=http://localhost:6006/?path=/story/components-blogpostform) (Placeholder)

### Save Draft / Publish Post

#### Trigger
- User clicks on the "Save Draft" or "Publish" button within the `BlogPostForm`.

#### Behavior
1. Client-side validation is performed on the form data using Zod.
2. If validation fails, error messages are displayed next to the respective form fields.
3. If validation passes:
    a. A loading indicator is shown on the button.
    b. An API call is made:
        - `POST /posts` for new posts.
        - `PUT /posts/[id]` for existing posts (if an ID was provided during initialization).
    c. Upon successful API response:
        - A success notification is displayed.
        - The user is redirected to the newly created/updated post's view page (`/posts/[id]`) or the blog post list page (`/`).
    d. Upon API error:
        - An error notification is displayed.
        - Form fields might be re-enabled for correction.

#### Component Reference
- [Link to BlogPostForm Storybook entry](https://www.google.com/search?q=http://localhost:6006/?path=/story/components-blogpostform) (Placeholder)
- [Link to Button Storybook entry](https://www.google.com/search?q=http://localhost:6006/?path=/story/ui-button) (Placeholder)

### Cancel Editing/Creation

#### Trigger
- User clicks on the "Cancel" button.

#### Behavior
1. A confirmation dialog may appear if there are unsaved changes.
2. If confirmed (or no unsaved changes), the user is navigated back to the previous page or the blog post list page (`/`).

#### Component Reference
- [Link to Button Storybook entry](https://www.google.com/search?q=http://localhost:6006/?path=/story/ui-button) (Placeholder)

## 4. Data Requirements

This section outlines the API endpoints this page interacts with. For complete request and response schemas, refer to the **OpenAPI spec**.

### `GET /posts/[id]`

#### Description
- Fetches the details of a single blog post by its ID. Used to pre-fill the form when editing an existing post.

#### API Spec Reference
- See the `getPostById` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec) (Placeholder)

### `POST /posts`

#### Description
- Creates a new blog post.

#### API Spec Reference
- See the `createPost` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec) (Placeholder)

### `PUT /posts/[id]`

#### Description
- Updates an existing blog post identified by its ID.

#### API Spec Reference
- See the `updatePost` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec) (Placeholder)
