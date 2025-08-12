# User Dashboard

## 1. Page Overview

### Description
- The main landing page for an authenticated user, providing a quick overview of key information and shortcuts.

### URL
- `/dashboard`

### Access
- Authenticated Users only.


## 2. Layout and Structure

This page is composed of the following components. For component details, see the **Storybook**.

### Primary Components
- `Header` (at the top)
- `Sidebar` (left navigation)
- `UserAccountCard` (in the main content area)
- `RecentActivityList` (in the main content area)
- `QuickActionsCard` (in the main content area)

### Responsive Behavior

The main content area uses a two-column grid on desktop, which collapses to a single-column stack on mobile.


## 3. Actions and Interactions

This section defines the unique behavior and logic that integrates the components.

### Upgrade Plan

#### Trigger
- User clicks on the "Upgrade Plan" button within the `UserAccountCard`.

#### Behavior
1. A modal dialog is displayed, showing the `UpgradePlanModal` component.
2. The user can close the modal by clicking the "X" icon or the overlay.

#### Component Reference
- [Link to UpgradePlanModal Storybook entry](https://www.google.com/search?q=http://localhost:6006/%3Fpath%3D/story/upgrade-plan-modal)

### Global Search

#### Trigger
- User types a minimum of 3 characters into the `Header`'s search input.
  
#### Behavior
1. A search dropdown list appears.
2. An **API call is made to the `GET /api/v1/search` endpoint** with the search term.
3. The dropdown populates with the results. A loading state is shown during the API call.


## 4. Data Requirements

This section outlines the API endpoints this page interacts with. For complete request and response schemas, refer to the **OpenAPI spec**.

### `GET /api/v1/dashboard`

#### Description
- Fetches all data required to render the dashboard's primary components.

#### API Spec Reference
- See the `dashboard` endpoint in the [OpenAPI spec](https://www.google.com/search?q=path/to/your/openapi.yaml).

  
### `GET /api/v1/search`

#### Description
- Performs a global search based on the user's input.

#### API Spec Reference
- See the `search` endpoint in the [OpenAPI spec](https://www.google.com/search?q=path/to/your/openapi.yaml).
