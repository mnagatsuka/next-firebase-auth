import type { Meta, StoryObj } from '@storybook/nextjs-vite'
import { BlogPostContent } from './BlogPostContent'

const meta: Meta<typeof BlogPostContent> = {
  title: 'Blog/BlogPostContent',
  component: BlogPostContent,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof BlogPostContent>

export const Default: Story = {
  args: {
    title: 'Getting Started with Next.js',
    content: `Next.js is a powerful React framework that enables you to build full-stack web applications by extending the latest React features.

Key Features:
- Server-Side Rendering (SSR): Pre-render pages on the server
- Static Site Generation (SSG): Generate static HTML at build time  
- Client-Side Rendering (CSR): Render pages in the browser
- API Routes: Build API endpoints within your Next.js app

Getting Started:
To create a new Next.js project, run:
npx create-next-app@latest my-app
cd my-app
npm run dev

Your application will be available at http://localhost:3000.

Conclusion:
Next.js provides a great developer experience with many features out of the box. It's perfect for building modern web applications.`,
    author: 'John Doe',
    publishedAt: '2024-01-15T10:30:00Z',
    tags: ['Next.js', 'React', 'TypeScript'],
    readingTime: '5 min read',
  },
}

export const LongContent: Story = {
  args: {
    title: 'Advanced React Patterns and State Management Techniques',
    content: `React has evolved significantly over the years, and with it, the patterns we use to build applications. In this comprehensive post, we'll explore some advanced patterns that can help you write more maintainable and scalable React code.

Custom Hooks:
Custom hooks are a powerful way to extract component logic into reusable functions. They allow you to share stateful logic between components without changing your component hierarchy.

When creating custom hooks, follow these best practices:
- Always start with "use" prefix
- Keep hooks focused on a single concern
- Return objects with named properties instead of arrays when returning multiple values
- Use TypeScript for better type safety

Context and Providers:
The Context API provides a way to pass data through the component tree without having to pass props down manually at every level. This is particularly useful for global state like themes, authentication, or user preferences.

State Management:
When your application grows, managing state becomes increasingly important. Consider these patterns:
- Local component state for simple UI state
- Context for component tree-wide state
- External libraries like Zustand or Redux for complex application state

Performance Optimization:
React provides several tools for optimizing performance:
- React.memo for preventing unnecessary re-renders
- useMemo for expensive calculations
- useCallback for stable function references
- Lazy loading for code splitting

Conclusion:
Mastering these patterns will help you build more efficient and maintainable React applications. Remember to always measure performance before optimizing, and choose the right tool for the job.`,
    author: 'Jane Smith',
    publishedAt: '2024-01-14T09:15:00Z',
    tags: ['React', 'Patterns', 'State Management', 'Performance', 'Hooks'],
    readingTime: '12 min read',
  },
}

export const MinimalContent: Story = {
  args: {
    title: 'Quick Tip',
    content: 'This is a short blog post with minimal content.',
    author: 'Bob Johnson',
    publishedAt: '2024-01-13T14:45:00Z',
    tags: ['Tips'],
  },
}

export const NoTags: Story = {
  args: {
    title: 'Post Without Tags',
    content: `Sometimes blog posts don't need tags. This post demonstrates how the content looks without any tags or reading time estimate.

Content can still be rich and informative without needing categorization. The focus should always be on providing value to the reader.`,
    author: 'Alice Wilson',
    publishedAt: '2024-01-12T16:20:00Z',
    tags: [],
  },
}