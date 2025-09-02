# Auth Modals (Login / Sign Up)

## 1. Page Overview

### Description
- Centered overlay modals that handle user authentication. Triggered from the Header: Login modal with a link to switch to Sign Up.

### URL
- N/A (modal overlays, not standalone pages).

### Access
- Public; behavior varies based on whether the current user is anonymous or authenticated.

## 2. Layout and Structure

This flow composes standard modal and form components. For component prop details, refer to Storybook.

### Primary Components
- Modal — overlay container with title, content, and actions.
- Text Fields — email, password (and confirm password if required).
- Buttons — submit, cancel/close, provider buttons (optional, e.g., Google/GitHub).
- Link — in-modal switch between Login and Sign Up.

### Responsive Behavior
- Modal centered with dimmed backdrop; responsive width, scrollable content if needed.
- Ensure comfortable tap targets and readable spacing on mobile.

## 3. Actions and Interactions

### Open Login Modal

#### Trigger
- User clicks "Login or Signup" in the Header.

#### Behavior
1. Open the Login modal and focus the first input.
2. Provide a link to switch to the Sign Up modal.

#### Component Reference
- Header, Modal.

### Submit Login

#### Trigger
- User submits the Login form.

#### Behavior
1. Call Firebase `signIn` with provided credentials (or provider sign-in if enabled).
2. Obtain ID token; POST `/api/auth/login` to set/refresh `__session`.
3. Close modal; update header controls to show "Logout"; retry any pending action.
4. On error, show inline message and keep inputs for retry.

#### Component Reference
- Modal, Text Fields, Buttons.

### Switch to Sign Up

#### Trigger
- User clicks the link in the Login modal.

#### Behavior
- Replace modal content with the Sign Up form while keeping the same overlay.

#### Component Reference
- Modal, Link.

### Submit Sign Up (Promotion if Anonymous)

#### Trigger
- User submits the Sign Up form.

#### Behavior
1. If `currentUser.isAnonymous`, link account with credential/provider (Promotion) and force-refresh ID token.
2. Otherwise, create/sign in the user via Firebase and obtain ID token.
3. POST `/api/auth/login` to set/refresh `__session`.
4. Close modal; update header controls; retry any pending action.
5. On error (e.g., credential-in-use), show inline message and suggest switching to Login.

#### Component Reference
- Modal, Text Fields, Buttons.

## 4. Data Requirements

### `POST /api/auth/login`

#### Description
- Sets or refreshes the `__session` cookie using the current Firebase ID token after login or signup.

## 5. Accessibility

- Apply `aria-modal` and `role="dialog"`; trap focus within the modal.
- Set initial focus to the title or first input; ESC closes the modal.
- Restore focus to the trigger (header button) on close.
