import { http, HttpResponse } from 'msw'

// Blog Posts API Handlers
export const handlers = [
  // GET /api/posts - Get paginated blog posts
  http.get('/api/posts', ({ request }) => {
    const url = new URL(request.url)
    const page = Number(url.searchParams.get('page')) || 1
    const limit = Number(url.searchParams.get('limit')) || 10

    return HttpResponse.json({
      status: 'success',
      data: {
        posts: [
          {
            id: 'post-123',
            title: 'Getting Started with Next.js',
            excerpt: 'Learn the basics of Next.js in this comprehensive guide covering SSR, SSG, and CSR.',
            author: 'John Doe',
            publishedAt: '2024-01-15T10:30:00Z'
          },
          {
            id: 'post-124',
            title: 'Advanced React Patterns',
            excerpt: 'Explore advanced React patterns including hooks, context, and state management techniques.',
            author: 'Jane Smith',
            publishedAt: '2024-01-14T09:15:00Z'
          },
          {
            id: 'post-125',
            title: 'TypeScript Best Practices',
            excerpt: 'Learn TypeScript best practices for building scalable and maintainable applications.',
            author: 'Bob Johnson',
            publishedAt: '2024-01-13T14:45:00Z'
          }
        ],
        pagination: {
          page,
          limit,
          total: 45,
          hasNext: page * limit < 45
        }
      }
    })
  }),

  // POST /api/posts - Create a new blog post
  http.post('/api/posts', async ({ request }) => {
    const body = await request.json() as {
      title: string
      content: string
      excerpt?: string
      status: 'draft' | 'published'
    }

    const newPost = {
      id: `post-${Date.now()}`,
      title: body.title,
      content: body.content,
      excerpt: body.excerpt || body.content.substring(0, 100) + '...',
      author: 'Current User',
      publishedAt: new Date().toISOString(),
      status: body.status
    }

    return HttpResponse.json({
      status: 'success',
      data: {
        post: newPost
      }
    }, { status: 201 })
  }),

  // GET /api/posts/:id - Get single blog post
  http.get('/api/posts/:id', ({ params }) => {
    const { id } = params

    if (id === 'post-404') {
      return HttpResponse.json({
        status: 'error',
        error: {
          code: 'NOT_FOUND',
          message: 'Blog post not found'
        }
      }, { status: 404 })
    }

    return HttpResponse.json({
      status: 'success',
      data: {
        post: {
          id: id as string,
          title: 'Getting Started with Next.js',
          content: '# Introduction\n\nNext.js is a powerful React framework that enables you to build full-stack web applications...',
          excerpt: 'Learn the basics of Next.js in this comprehensive guide covering SSR, SSG, and CSR.',
          author: 'John Doe',
          publishedAt: '2024-01-15T10:30:00Z',
          status: 'published'
        }
      }
    })
  }),

  // PUT /api/posts/:id - Update blog post
  http.put('/api/posts/:id', async ({ params, request }) => {
    const { id } = params
    const body = await request.json() as {
      title: string
      content: string
      excerpt?: string
      status: 'draft' | 'published'
    }

    if (id === 'post-404') {
      return HttpResponse.json({
        status: 'error',
        error: {
          code: 'NOT_FOUND',
          message: 'Blog post not found'
        }
      }, { status: 404 })
    }

    const updatedPost = {
      id: id as string,
      title: body.title,
      content: body.content,
      excerpt: body.excerpt || body.content.substring(0, 100) + '...',
      author: 'John Doe',
      publishedAt: '2024-01-15T10:30:00Z',
      status: body.status
    }

    return HttpResponse.json({
      status: 'success',
      data: {
        post: updatedPost
      }
    })
  }),

  // GET /api/posts/:id/comments - Get comments for a blog post
  http.get('/api/posts/:id/comments', ({ params, request }) => {
    const { id } = params
    const url = new URL(request.url)
    const page = Number(url.searchParams.get('page')) || 1
    const limit = Number(url.searchParams.get('limit')) || 10

    return HttpResponse.json({
      status: 'success',
      data: {
        comments: [
          {
            id: 'comment-1',
            postId: id as string,
            author: 'Alice Johnson',
            content: 'Great article! Very helpful for beginners.',
            createdAt: '2024-01-16T08:30:00Z'
          },
          {
            id: 'comment-2',
            postId: id as string,
            author: 'Bob Wilson',
            content: 'Thanks for sharing this. Looking forward to more content like this.',
            createdAt: '2024-01-16T10:15:00Z'
          }
        ],
        pagination: {
          page,
          limit,
          total: 15,
          hasNext: page * limit < 15
        }
      }
    })
  }),

  // POST /api/posts/:id/comments - Create a new comment
  http.post('/api/posts/:id/comments', async ({ params, request }) => {
    const { id } = params
    const body = await request.json() as {
      author: string
      content: string
    }

    const newComment = {
      id: `comment-${Date.now()}`,
      postId: id as string,
      author: body.author,
      content: body.content,
      createdAt: new Date().toISOString()
    }

    return HttpResponse.json({
      status: 'success',
      data: {
        comment: newComment
      }
    }, { status: 201 })
  }),

  // Error handlers for testing error scenarios
  http.get('/api/posts/error-500', () => {
    return HttpResponse.json({
      status: 'error',
      error: {
        code: 'INTERNAL_SERVER_ERROR',
        message: 'Something went wrong'
      }
    }, { status: 500 })
  }),

  http.post('/api/posts/unauthorized', () => {
    return HttpResponse.json({
      status: 'error',
      error: {
        code: 'UNAUTHORIZED',
        message: 'Authentication required'
      }
    }, { status: 401 })
  })
]