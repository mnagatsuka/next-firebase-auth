import type { Meta, StoryObj } from '@storybook/nextjs-vite'
import { http, HttpResponse } from 'msw'
import { CommentsSection } from './CommentsSection'

const meta: Meta<typeof CommentsSection> = {
  title: 'Blog/CommentsSection',
  component: CommentsSection,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    onAddComment: { action: 'comment-added' },
  },
}

export default meta
type Story = StoryObj<typeof CommentsSection>

const mockComments = [
  {
    id: 'comment-1',
    postId: 'post-123',
    author: 'Alice Johnson',
    content: 'Great article! Very helpful for beginners.',
    createdAt: '2024-01-16T08:30:00Z'
  },
  {
    id: 'comment-2',
    postId: 'post-123',
    author: 'Bob Wilson',
    content: 'Thanks for sharing this. Looking forward to more content like this.',
    createdAt: '2024-01-16T10:15:00Z'
  }
]

export const WithComments: Story = {
  args: {
    comments: mockComments,
    isLoading: false,
  },
  parameters: {
    msw: {
      handlers: [
        http.get('/api/posts/:id/comments', () => {
          return HttpResponse.json({
            status: 'success',
            data: {
              comments: mockComments,
              pagination: {
                page: 1,
                limit: 10,
                total: 2,
                hasNext: false,
              },
            },
          })
        }),
        http.post('/api/posts/:id/comments', async ({ request }) => {
          const body = await request.json() as { author: string; content: string }
          return HttpResponse.json({
            status: 'success',
            data: {
              comment: {
                id: `comment-${Date.now()}`,
                postId: 'post-123',
                author: body.author,
                content: body.content,
                createdAt: new Date().toISOString()
              }
            }
          }, { status: 201 })
        }),
      ],
    },
  },
}

export const NoComments: Story = {
  args: {
    comments: [],
    isLoading: false,
  },
  parameters: {
    msw: {
      handlers: [
        http.get('/api/posts/:id/comments', () => {
          return HttpResponse.json({
            status: 'success',
            data: {
              comments: [],
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
  args: {
    comments: [],
    isLoading: true,
  },
  parameters: {
    msw: {
      handlers: [
        http.get('/api/posts/:id/comments', () => {
          return new Promise(() => {}) // Never resolves to simulate loading
        }),
      ],
    },
  },
}

export const ErrorState: Story = {
  args: {
    comments: [],
    isLoading: false,
  },
  parameters: {
    msw: {
      handlers: [
        http.get('/api/posts/:id/comments', () => {
          return HttpResponse.json({
            status: 'error',
            error: {
              code: 'INTERNAL_SERVER_ERROR',
              message: 'Failed to load comments',
            },
          }, { status: 500 })
        }),
      ],
    },
  },
}