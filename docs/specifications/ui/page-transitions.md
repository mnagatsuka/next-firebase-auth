# Page Transition Specification

This document outlines the standards and patterns for page transitions within the application. Consistent and smooth transitions are crucial for a good user experience, providing visual feedback and a sense of place.

## General Principles

- **Consistency**: Transitions should be consistent across the application. Similar actions should result in similar transitions.
- **Performance**: Animations should be smooth and performant, primarily using CSS transforms (`translate`, `opacity`, `scale`) to avoid layout recalculations.
- **Clarity**: Transitions should clarify the relationship between pages and user actions, not distract or confuse the user.

## Main Application Flow

The following diagram illustrates the primary navigation paths between the main pages of the application.

```mermaid
stateDiagram-v2
    direction LR

    [*] --> HomePage

    state "Blog Content" as Content {
        HomePage: List of posts
        PostDetailPage: Single post view
    }

    state "Blog Management" as Management {
        MyPostsPage: User-scoped posts list
        FavoritesPage: Favorited posts list
        CreatePostPage: New post form
        EditPostPage: Edit post form
    }

    HomePage --> PostDetailPage: Clicks a post
    PostDetailPage --> HomePage: Navigates back

    HomePage --> MyPostsPage: Clicks "My Posts" (Header)
    HomePage --> FavoritesPage: Clicks "Favorites" (Header)
    MyPostsPage --> PostDetailPage: Clicks a post
    MyPostsPage --> CreatePostPage: Clicks "Create Post"
    FavoritesPage --> PostDetailPage: Clicks a post

    HomePage --> CreatePostPage: Clicks "Create Post"
    PostDetailPage --> EditPostPage: Clicks "Edit"

    CreatePostPage --> PostDetailPage: Post submitted
    EditPostPage --> PostDetailPage: Post updated

    CreatePostPage --> HomePage: Action cancelled
    EditPostPage --> PostDetailPage: Action cancelled

    PostDetailPage --> MyPostsPage: Navigates back (from My Posts)
    PostDetailPage --> FavoritesPage: Navigates back (from Favorites)
```

## Transition Animation Details

### 1. Standard Navigational Transition

This transition is used for navigating between primary pages at the same hierarchical level, such as moving from the `HomePage` to the `PostDetailPage`.

- **Description**: The new page slides in from the right, covering the old page. When navigating back, the old page slides out to the right, revealing the previous page.
- **Use Cases**:
    - `HomePage` -> `PostDetailPage`
    - `HomePage` -> `MyPostsPage` (Header nav)
    - `HomePage` -> `FavoritesPage` (Header nav)
    - `MyPostsPage` -> `PostDetailPage`
    - `MyPostsPage` -> `CreatePostPage`
    - `FavoritesPage` -> `PostDetailPage`
    - `PostDetailPage` -> `EditPostPage`

```mermaid
sequenceDiagram
    participant OldPage
    participant NewPage

    Note over OldPage, NewPage: User clicks a navigation link

    OldPage->>NewPage: Animate Out (Slide Left)
    activate OldPage
    Note right of OldPage: opacity: 1 -> 0<br/>transform: translateX(0) -> translateX(-25%)
    deactivate OldPage

    NewPage->>OldPage: Animate In (Slide From Right)
    activate NewPage
    Note left of NewPage: opacity: 0 -> 1<br/>transform: translateX(100%) -> translateX(0)
    deactivate NewPage
```

### 2. Form Submission & Data Operations

This indicates that the application is processing a user request, like submitting a form or saving data.

- **Description**: The button that triggered the action will display a loading spinner. The form fields will be disabled to prevent further input. Upon completion, a success or error message may be displayed before transitioning to the next page.
- **Default Redirects**:
    - On successful create (from `CreatePostPage`), navigate to `PostDetailPage` of the new post.
    - On successful edit (from `EditPostPage`), remain in `PostDetailPage` and show a success notification.

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Server

    User->>UI: Clicks "Publish" button
    UI->>UI: Disable form fields & show spinner on button
    UI->>Server: POST /posts
    activate Server
    Server-->>UI: Respond with success/error
    deactivate Server
    UI->>UI: Re-enable form & hide spinner
    alt On Success
        UI->>UI: Show success notification
        UI->>UI: Transition to PostDetailPage
    else On Error
        UI->>UI: Show error message
    end
```

### 3. Auth Initialization (My Posts)

This covers the automatic anonymous sign-in used by `MyPostsPage` and `FavoritesPage` when a user is not authenticated.

- **Description**: If no auth session exists, initialize anonymous sign-in before fetching user-scoped posts. During initialization, show a lightweight loading state for the list area; the page chrome (Header/Footer) remains interactive.

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Auth
    participant API

    User->>UI: Navigate to MyPostsPage / FavoritesPage
    UI->>Auth: Ensure session (anonymous if needed)
    alt No session
        Auth-->>UI: Anonymous user created
    else Existing session
        Auth-->>UI: Session ready
    end
    UI->>API: GET /users/[uid]/posts
    API-->>UI: Posts list
    UI->>User: Render list (or EmptyState)
```

## Implementation Notes

- **Library**: It is recommended to use a dedicated animation library like `framer-motion` to handle these transitions in a declarative way.
- **CSS**: Define transition properties and animations in the global CSS file to ensure consistency and reusability.
- **Accessibility**: Ensure that animations do not negatively impact users with motion sensitivity. A `prefers-reduced-motion` media query should be used to disable or simplify animations for these users.
- **Header Navigation**: Add a persistent `My Posts` item to the global `Header`. The Home → My Posts transition uses the standard slide-in animation.
- **Header Navigation**: `My Posts` appears in the global `Header` only for authenticated non-anonymous users. The Home → My Posts transition uses the standard slide-in animation. `Favorites` is available to all users (including anonymous).
