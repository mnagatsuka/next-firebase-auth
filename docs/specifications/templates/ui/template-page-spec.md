# [Page Name]

## 1. Page Overview

### Description
- A brief description of the page's purpose and its role in the user's workflow.
- *Consider including the rendering strategy (e.g., **Server-Side Rendering (SSR)** for SEO, **Client-Side Rendering (CSR)** for interactivity) and the rationale behind it.*

### URL
- `/[page-path]` or `/resource/[id]` (e.g., `/dashboard`, `/posts/[id]`)

### Access
- Define who can access this page (e.g., Authenticated Users only, Public, Admin).


## 2. Layout and Structure

This page is composed of the following components. For component details, see the **Storybook**.

### Primary Components
- `ComponentName1` (placement in layout, e.g., "at the top", "main content area")
- `ComponentName2` (placement in layout)
- `ComponentName3` (placement in layout)
- *Add more components as needed, describing their role and placement.*

### Responsive Behavior

Describe how the layout changes for different screen sizes (e.g., grid on desktop, stacked layout on mobile, specific breakpoints). Detail how elements adapt (e.g., typography scales, images resize, navigation collapses).


## 3. Actions and Interactions

This section defines the unique behavior and logic that integrates the components.

### [Descriptive Action Name]

#### Trigger
- Describe the specific user action (e.g., "User clicks 'Submit' button", "Page loads") or system event that initiates this behavior.

#### Behavior
1. Describe the first step of the interaction (e.g., "Client-side validation is performed").
2. Describe subsequent steps, including API calls (e.g., `POST /api/data`), state changes, loading indicators, error handling, and navigation.
3. *Use numbered lists for clarity.*

#### Component Reference
- [Link to relevant Storybook entry](https://storybook-url.com/?path=/story/components-componentname) (e.g., `https://localhost:6006/?path=/story/components-blogpostform`)


## 4. Data Requirements

This section outlines the API endpoints this page interacts with. For complete request and response schemas, refer to the **OpenAPI spec**.

### `[HTTP METHOD] /api/v1/[endpoint]`

#### Description
- Describe what data this endpoint provides or modifies, and its purpose for this page.

#### Query Params (Optional)
- List any query parameters, their types, and default values (e.g., `page` (number, default `1`), `limit` (number, default `10`)). *Only include if applicable for GET requests.*

#### API Spec Reference
- See the `[endpoint name]` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec) (e.g., `getPostById` endpoint in the [OpenAPI spec](https://link-to-your-openapi-spec))