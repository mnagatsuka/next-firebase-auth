import type { Meta, StoryObj } from '@storybook/nextjs-vite'
import { http, HttpResponse } from 'msw'
import { PostList } from './PostList'

const meta: Meta<typeof PostList> = {
  title: 'Blog/PostList',
  component: PostList,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof PostList>

const mockPosts = [
  {
    id: 'post-123',
    title: 'Getting Started with Next.js',
    excerpt: 'Learn the basics of Next.js in this comprehensive guide covering SSR, SSG, and CSR.',
    author: 'John Doe',
    publishedAt: '2024-01-15T10:30:00Z',
    tags: ['Next.js', 'React', 'TypeScript'],
  },
  {
    id: 'post-124',
    title: 'Advanced React Patterns',
    excerpt: 'Explore advanced React patterns including hooks, context, and state management techniques.',
    author: 'Jane Smith',
    publishedAt: '2024-01-14T09:15:00Z',
    tags: ['React', 'Patterns', 'Hooks'],
  },
  {
    id: 'post-125',
    title: 'TypeScript Best Practices',
    excerpt: 'Learn TypeScript best practices for building scalable and maintainable applications.',
    author: 'Bob Johnson',
    publishedAt: '2024-01-13T14:45:00Z',
    tags: ['TypeScript', 'Best Practices'],
  },
]

export const Default: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/posts', () => {
          return HttpResponse.json({
            status: 'success',
            data: {
              posts: mockPosts,
              pagination: {
                page: 1,
                limit: 10,
                total: 3,
                hasNext: false,
              },
            },
          })
        }),
      ],
    },
  },
}

export const Empty: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/posts', () => {
          return HttpResponse.json({
            status: 'success',
            data: {
              posts: [],
              pagination: {
                page: 1,
                limit: 10,
                total: 0,
                hasNext: false,
              },
            },
          })
        }),
      ],
    },
  },
}

export const Loading: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/posts', () => {
          return new Promise(() => {}) // Never resolves to simulate loading
        }),
      ],
    },
  },
}

export const ErrorState: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get('/api/posts', () => {
          return HttpResponse.json({
            status: 'error',
            error: {
              code: 'INTERNAL_SERVER_ERROR',
              message: 'Something went wrong',
            },
          }, { status: 500 })
        }),
      ],
    },
  },
}