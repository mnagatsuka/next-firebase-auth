# [Component Name]

## 1. Component Overview

### Description
- A brief description of the component's purpose and its role within the application.
- Note if this is a "dumb" presentational component or a "smart" container component.

### Props & Storybook
- For a detailed list of all props, their types, and default values, please refer to the **Storybook**.
- [Link to Storybook](https://storybook-url.com/?path=/story/category-componentname)
- *Key props that control primary behavior can be mentioned here if necessary.*


## 2. Layout and Structure

This component is composed of the following elements. For implementation details, see Storybook.

### Composition / Sub-Components
- List the smaller components or HTML elements that this component is built from.
- `SubComponent1` (e.g., "Used for the component's title")
- `SubComponent2` (e.g., "Used for the main content area")

### Responsive Behavior
- Describe how the component's layout changes for different screen sizes.
- Detail how elements adapt (e.g., typography scales, elements stack on mobile).


## 3. Actions and Interactions

This section defines the component's specific behaviors.

### [Descriptive Action Name]

#### Trigger
- Describe the specific user action (e.g., "User clicks the 'Close' icon") or prop change that initiates this behavior.

#### Behavior
1. Describe the first step of the interaction (e.g., "The `onClose` callback is fired.").
2. Describe subsequent steps, including internal state changes or visual feedback.
3. *Use numbered lists for clarity.*

#### Emitted Events
- List any callbacks or events that are triggered by this action (e.g., `onClose`, `onSubmit`).


## 4. Data Requirements (Optional)

This section outlines any API endpoints the component interacts with directly.
*Note: This is uncommon. Most components should receive data via props.*

### `[HTTP METHOD] /[endpoint]`
- **Description:** Describe what data this endpoint provides or modifies and why the component needs it.


## 5. State & Visibility Rules (Optional)

Describe how the component's appearance or behavior changes based on application state or data fetching.

- **Visibility Rules:** How does the component render for different user roles or states? (e.g., "Shows 'Logout' button for authenticated users, 'Login' for anonymous users").
- **Loading State:** Describe the visual feedback during data fetching (e.g., "The button shows a spinner.").
- **Empty State:** Describe the condition and what is displayed when there is no data (e.g., "The list shows a 'No items' message.").
- **Error State:** Describe how errors are communicated (e.g., "The input field gets a red border.").


## 6. Accessibility (Optional)

- **Focus Management:** Describe how focus is handled (e.g., "When the modal opens, focus is trapped inside.").
- **ARIA & Roles:** List key ARIA roles and attributes (e.g., `role="dialog"`, `aria-live="polite"`).
- **Keyboard Navigation:** Ensure all interactive elements are keyboard-operable (e.g., "Escape key closes the component.").