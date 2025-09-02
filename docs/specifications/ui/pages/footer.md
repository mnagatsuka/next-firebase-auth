# Footer

## 1. Page Overview

### Description
- Global site footer displayed on every page with site identity and optional links.

### URL
- N/A (global layout component).

### Access
- Public (no authentication required).

## 2. Layout and Structure

This layout composes simple, reusable elements. For component-level details, refer to Storybook.

### Primary Components
- Site Identity — project/site name and current year.
- Optional Links — Terms, Privacy, About, Contact (render only if available).

### Responsive Behavior
- Full-width row; on narrow screens, content stacks and centers.
- Maintain comfortable spacing consistent with header/page gutters.

## 3. Actions and Interactions

### Navigate via Footer Links

#### Trigger
- User clicks a footer link.

#### Behavior
- Navigate using client-side routing when available; open external links in a new tab if specified.

#### Component Reference
- Footer, Link components.

## 4. Data Requirements

- None.

## 5. Accessibility

- Use the `contentinfo` landmark for the footer region.
- Ensure sufficient contrast for text/links and visible focus styles.
