# 16. Storybook & UI Development

This section defines the rules and best practices for setting up and using **Storybook** in our Next.js projects with **Tailwind CSS** and **shadcn/ui**.

Our goals are:
- Provide an isolated environment for building and testing UI components
- Enable visual documentation for designers, developers, and stakeholders
- Facilitate visual regression testing and design system consistency
- Keep stories maintainable and aligned with the production UI


## 1. Setting up Storybook in a Next.js Project

Install Storybook and required dependencies:

```bash
pnpm dlx storybook@latest init --builder @storybook/builder-vite
````

> We use the Vite builder for faster startup and refresh times.

Install additional dependencies for Tailwind and shadcn/ui support:

```bash
pnpm add -D postcss autoprefixer tailwindcss
```

Configure Tailwind for Storybook by ensuring `postcss.config.js` and `tailwind.config.js` are present and that Storybook’s `.storybook/preview.ts` imports the global CSS:

```ts
// .storybook/preview.ts
import '../src/styles/globals.css'
import type { Preview } from '@storybook/react'

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: '^on.*' },
    controls: { expanded: true }
  }
}

export default preview
```


## 2. Writing Stories for Components and Pages

**Rules:**

* Each component should have its own `.stories.tsx` file in the same folder.
* Stories should represent **realistic usage scenarios**.
* Use `args` to make stories interactive in the Storybook UI.

**Example:**

```tsx
// src/components/ui/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './button'

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  args: {
    children: 'Click me'
  }
}

export default meta
type Story = StoryObj<typeof Button>

export const Default: Story = {}

export const Primary: Story = {
  args: {
    variant: 'default'
  }
}

export const Destructive: Story = {
  args: {
    variant: 'destructive'
  }
}
```


## 3. Using Storybook for Visual Regression Testing

Integrate visual regression testing tools like [Chromatic](https://www.chromatic.com/) or Playwright’s image snapshot feature.

**Rules:**

* Run visual regression tests as part of CI/CD for components in the design system.
* Approve changes only when they are intentional and documented.
* Keep snapshots up to date with design changes.


## 4. Integrating with Design Systems and Figma

**Guidelines:**

* For shadcn/ui components, document any Tailwind overrides in the story description.
* Link to the relevant Figma frame or page in the Storybook docs tab for reference.
* Keep component stories aligned with the design system tokens (colors, spacing, typography).


## 5. Best Practices for Organizing Stories and Decorators

**Structure:**

* Organize stories by feature or component type:

  * `UI/` for atomic components
  * `Forms/` for form controls
  * `Pages/` for full-page layouts

**Example folder structure:**

```
src/components/
  ui/
    button.tsx
    button.stories.tsx
  forms/
    input.tsx
    input.stories.tsx
src/pages/
  home.stories.tsx
```

**Decorators:**

* Use decorators to wrap stories with global providers (ThemeProvider, QueryClientProvider, etc.).
* Keep `.storybook/preview.ts` clean; move complex decorators into `/storybook/decorators/`.

**Example:**

```ts
// .storybook/preview.ts
import '../src/styles/globals.css'
import type { Preview } from '@storybook/react'
import { withQueryProvider } from './decorators/withQueryProvider'

const preview: Preview = {
  decorators: [withQueryProvider],
  parameters: {
    actions: { argTypesRegex: '^on.*' },
    controls: { expanded: true }
  }
}

export default preview
```

```ts
// .storybook/decorators/withQueryProvider.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'

const client = new QueryClient()

export const withQueryProvider = (Story: React.FC) => (
  <QueryClientProvider client={client}>
    <Story />
  </QueryClientProvider>
)
```


## 6. General Guidelines

* Keep stories **minimal but illustrative**—focus on the component, not unrelated features.
* Use Storybook’s Docs mode to add usage notes, props tables, and interactive examples.
* Use `args` and `controls` to enable live configuration in the Storybook UI.
* Avoid hardcoding theme-dependent values in stories; use Tailwind and design tokens.


By following these guidelines, Storybook becomes a **single source of truth for UI components**, making it easier to maintain consistency, communicate with designers, and prevent regressions in our Next.js applications.
