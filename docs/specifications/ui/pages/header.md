# Header

## 1. Page Overview

### Description
- Global site header with branding, primary navigation, and authentication controls. Persistently visible across all pages.

### URL
- N/A (global layout component).

### Access
- Public; visible to all users. Auth control visibility changes based on authentication state.

## 2. Layout and Structure

This layout composes reusable components. For component-level props, refer to Storybook.

### Primary Components
- Branding — logo/site title.
- Navigation — links to Home, Create Post, My Posts, Favorite Posts.
- Auth Controls — shows "Login or Signup" for anonymous users; shows "Logout" for authenticated users.

### Responsive Behavior
- Header content remains in a single row when space allows; collapses appropriately on small screens.
- Auth controls are right-aligned; touch targets are at least 44px.

## 3. Actions and Interactions

### Open Login Modal

#### Trigger
- User clicks "Login or Signup" in the Header.

#### Behavior
1. Open the Login modal centered on the page.
2. Modal provides a link to switch to Sign Up.
3. On successful authentication, close modal and update header controls to show "Logout".

#### Component Reference
- Header, Auth Modals (see `auth-modals.md`).

### Logout

#### Trigger
- User clicks "Logout" in the Header.

#### Behavior
1. Call `POST /api/auth/logout` to clear `__session`.
2. Reset client auth state (Zustand); optionally call `signOut()`.
3. Header re-renders to show "Login or Signup"; anonymous bootstrap may run in the background.

#### Component Reference
- Header.

### Primary Navigation

#### Trigger
- User clicks a navigation link (Home, Create Post, My Posts, Favorite Posts).

#### Behavior
- Navigate to the corresponding route using client-side navigation where available; prefetch may be enabled.

#### Component Reference
- Header, Link components.

## 4. Data Requirements

### `POST /api/auth/logout`

#### Description
- Clears the `__session` cookie on the server; used by the Logout action.

## 5. Accessibility

- Provide clear labels for auth controls (e.g., "Login or Signup", "Logout").
- Maintain keyboard operability (Enter/Space) and visible focus outlines.
- When opening a modal, move focus into the modal; restore focus to the trigger on close.

## 6. State & Visibility Rules

- SSR/RSC: derive initial button visibility from verified `__session` to reduce flicker.
- CSR: hydrate from Zustand; avoid showing incorrect controls during auth transitions (prefer a small skeleton or defer rendering controls briefly).
