import { getBlogPostAPIMock } from '@/lib/api/generated/client.msw'
import { http, HttpResponse } from 'msw'

// Use generated mock handlers directly - they already have the correct paths (/posts)
const apiHandlers = getBlogPostAPIMock()

// Additional custom error handlers for testing
const errorHandlers = [
  http.get('/posts/error-500', () => {
    return HttpResponse.json({
      status: 'error',
      error: {
        code: 'INTERNAL_SERVER_ERROR',
        message: 'Something went wrong'
      }
    }, { status: 500 })
  }),

  http.post('/posts/unauthorized', () => {
    return HttpResponse.json({
      status: 'error',
      error: {
        code: 'UNAUTHORIZED',
        message: 'Authentication required'
      }
    }, { status: 401 })
  })
]

export const handlers = [
  ...apiHandlers,
  ...errorHandlers
]