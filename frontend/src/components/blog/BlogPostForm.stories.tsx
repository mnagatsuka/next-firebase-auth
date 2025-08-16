import type { Meta, StoryObj } from '@storybook/nextjs-vite'
import { http, HttpResponse } from 'msw'
import { BlogPostForm } from './BlogPostForm'

const meta: Meta<typeof BlogPostForm> = {
  title: 'Blog/BlogPostForm',
  component: BlogPostForm,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    onSubmit: { action: 'form-submitted' },
    onSaveDraft: { action: 'draft-saved' },
    onCancel: { action: 'form-cancelled' },
  },
}

export default meta
type Story = StoryObj<typeof BlogPostForm>

export const CreateNew: Story = {
  parameters: {
    msw: {
      handlers: [
        http.post('/posts', async ({ request }) => {
          const body = await request.json() as any
          return HttpResponse.json({
            status: 'success',
            data: {
              post: {
                id: `post-${Date.now()}`,
                ...body,
                author: 'Current User',
                publishedAt: new Date().toISOString(),
              }
            }
          }, { status: 201 })
        }),
      ],
    },
  },
}

export const EditExisting: Story = {
  parameters: {
    msw: {
      handlers: [
        http.get('/posts/:id', () => {
          return HttpResponse.json({
            status: 'success',
            data: {
              post: {
                id: 'post-123',
                title: 'Getting Started with Next.js',
                content: 'Next.js is a powerful React framework that enables you to build full-stack web applications...',
                excerpt: 'Learn the basics of Next.js in this comprehensive guide.',
                author: 'John Doe',
                publishedAt: '2024-01-15T10:30:00Z',
                status: 'draft'
              }
            }
          })
        }),
        http.put('/posts/:id', async ({ request }) => {
          const body = await request.json() as any
          return HttpResponse.json({
            status: 'success',
            data: {
              post: {
                id: 'post-123',
                ...body,
                author: 'John Doe',
                publishedAt: '2024-01-15T10:30:00Z',
              }
            }
          })
        }),
      ],
    },
  },
}

export const SaveError: Story = {
  parameters: {
    msw: {
      handlers: [
        http.post('/posts', () => {
          return HttpResponse.json({
            status: 'error',
            error: {
              code: 'VALIDATION_ERROR',
              message: 'Title is required',
            },
          }, { status: 400 })
        }),
      ],
    },
  },
}

export const ServerError: Story = {
  parameters: {
    msw: {
      handlers: [
        http.post('/posts', () => {
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