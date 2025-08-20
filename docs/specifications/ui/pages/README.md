# Page Specifications

This directory contains the user interface specifications for our web application. These markdown files serve as the single source of truth for how our application's pages are structured, what components they use, and how users can interact with them.

We use these specifications to align on design, functionality, and user flows before and during the development process.

## 📂 Directory Structure

### `pages/`
This is where you'll find a separate markdown file for each unique page in the application (e.g., `dashboard.md`, `settings.md`).

- Each file outlines the page's purpose, the components it contains, and the specific user actions that can be performed.
- These specifications focus on **page-level composition** and **user flows**, rather than the low-level details of individual components.


## 📄 Application Pages

This section lists the key pages within the application, each with its dedicated specification file.

- [Homepage](/docs/specifications/ui/pages/homepage.md)
- [Individual Post Page](/docs/specifications/ui/pages/individual-post.md)
- [Create/Edit Blog Post Page](/docs/specifications/ui/pages/create-blog-post.md)
- [My Posts](/docs/specifications/ui/pages/my-posts.md)
- [Favorite Posts](/docs/specifications/ui/pages/favorite-posts.md)


## 🎨 Components and Storybook

We use **Storybook** to document and showcase our individual UI components.

- Detailed component specifications—including props, states, and variants—are managed directly in Storybook (`.stories.jsx/tsx` files).
- The `.md` files in this directory link to the relevant Storybook stories. This allows us to keep our page specifications concise and focused on how components are assembled, rather than redefining them every time.
- To view our component library, please visit the [Storybook URL](https://www.google.com/search?q=http://localhost:6006) (or your hosted Storybook instance).


## 🚀 How to Use These Specs

### For Developers
Use these files to understand the requirements for building a new page or feature. Refer to the linked Storybook stories for component-specific implementation details.

### For Designers
Use these files to review and provide feedback on the proposed user experience and page layouts.

### For AI Agents
Use these files to get a clear, structured brief for generating code for new pages, layouts, and user interactions.

By keeping our page specifications here and our component specifications in Storybook, we ensure a clear, efficient, and well-documented development process.
