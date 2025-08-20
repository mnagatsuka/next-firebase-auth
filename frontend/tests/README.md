# Frontend Testing Guide

This directory contains comprehensive tests for the frontend application following the **Testing Trophy** approach with modern React testing best practices.

## Test Structure

```
frontend/tests/
├── unit/                    # Fast, isolated unit tests (60%)
│   ├── stores/             # Zustand store tests
│   └── lib/                # Utility function tests
├── integration/            # Component and hook integration tests (30%)
│   ├── components/         # Component tests with real API calls
│   └── hooks/              # Custom hook tests
├── setup.ts               # Test environment setup
├── test-utils.tsx         # React Testing Library helpers
└── tsconfig.json
```

**Note**: E2E tests are located at project root `tests/e2e/` since they test the full application stack.

## Quick Start

### 1. Install Dependencies

Frontend tests use the dependencies from the main frontend project:

```bash
# From frontend directory
cd frontend/
pnpm install

# Dependencies are automatically available for tests
```

### 2. Run All Tests

```bash
# From repository root
pnpm test:frontend          # run once
pnpm test:frontend:watch    # watch mode
pnpm test:frontend:coverage # with coverage
```

## Test Categories

### Unit Tests (Fast, Isolated)

Test pure functions and isolated logic without external dependencies:

```bash
# Run all unit tests
pnpm vitest run tests/frontend/unit

# Utility function tests
pnpm vitest run tests/frontend/unit/lib/date.test.ts
```

### Integration Tests

Test component interactions with real API calls (mocked with MSW):

```bash
# Run all integration tests
pnpm vitest run tests/frontend/integration

# Component integration tests
pnpm vitest run tests/frontend/integration/components/BlogPostsClient.test.tsx
pnpm vitest run tests/frontend/integration/components/BlogPostForm.test.tsx

# Hook integration tests
pnpm vitest run tests/frontend/integration/hooks/use-blog-posts.test.tsx
```

## Test Execution Options

### Coverage Reports

```bash
# Run with coverage
pnpm test:frontend:coverage

# View coverage report
open coverage/index.html
```

### Watch Mode for Development

```bash
# Watch mode with UI
pnpm test:frontend:ui

# Watch specific files
pnpm vitest watch tests/frontend/unit/stores
```

### Specific Test Selection

```bash
# Run tests by pattern
pnpm vitest run --grep "BlogPostForm"

# Run specific test file
pnpm vitest run tests/frontend/unit/stores/app-store.test.ts

# Run tests in specific directory
pnpm vitest run tests/frontend/integration
```

### Debug Mode

```bash
# Run with debug output
npx vitest run --reporter=verbose

# Run in debug mode
npx vitest run --inspect-brk
```

## Test Configuration

### Vitest Configuration (`vitest.config.ts`)

The test suite is configured with:
- **JSDOM environment** for DOM testing
- **Path aliases** (`@/` pointing to frontend/src)
- **MSW integration** for API mocking
- **React Testing Library** setup

### TypeScript Test Config (`tests/frontend/tsconfig.json` + `tsconfig.base.json`)

- Shared options live in `tsconfig.base.json` at the repo root.
- Frontend (`frontend/tsconfig.json`) and tests (`tests/frontend/tsconfig.json`) both extend the base.
- Tests scope TypeScript to this folder (`tests/frontend/**`) only (unit/integration).
- Playwright e2e is separate; not included in this tsconfig.
- Adds `vitest/globals` and `@testing-library/jest-dom` to `types`.

### Test Setup (`setup.ts`)

Provides:
- **MSW server** setup for API mocking
- **Testing Library** DOM matchers
- **Automatic cleanup** between tests

### Test Utilities (`test-utils.tsx`)

Helper functions for rendering components:
- `createTestQueryClient()`: TanStack Query client for tests
- `renderWithProviders()`: Render with all necessary providers
- `renderWithQuery()`: Render with QueryClient only

## API Mocking Strategy

### MSW Integration

Frontend tests use the existing MSW setup from `frontend/src/mocks/`:

```typescript
// Tests automatically use generated API mocks
import { server } from '../../setup'
import { http, HttpResponse } from 'msw'

// Override specific endpoints for error testing
server.use(
  http.get('/posts', () => {
    return HttpResponse.json(
      { status: 'error', error: { code: 'INTERNAL_SERVER_ERROR' } },
      { status: 500 }
    )
  })
)
```

### Factories & Scenarios

- Factories produce deterministic, typed data aligned with Orval schemas (seeded RNG + fixed time):

```ts
import { makePost, makePostSummary } from './factories/post'
import { makeComment } from './factories/comment'

const post = makePost({}, 42)           // stable across runs
const summary = makePostSummary({}, 42)  // matches types, deterministic
const comment = makeComment({}, 42, post.id)
```

- Scenarios compose generated MSW handlers to ensure cross-endpoint consistency and pagination continuity. Use `server.use(...scenario)` to override per test.

```ts
import { server } from '../setup'
import { scenarioPostsConsistent, scenarioPaginatedList, scenarioCreateThenGet } from './scenarios/posts'

// Ensure list ⇄ detail ⇄ comments use the same ID
server.use(...scenarioPostsConsistent({ seed: 7, selectedId: 'post-777' }))

// Drive pagination based on query params
server.use(...scenarioPaginatedList(25 /* total */, 11 /* seed */))

// Capture POST /posts and then GET the same entity
server.use(...scenarioCreateThenGet(5))
```

### Generated Query Hooks

Tests use the **actual generated TanStack Query hooks**:

```typescript
// ✅ Good: Use real generated hooks
import { useGetBlogPosts, useCreateBlogPost } from '@/lib/api/generated/client'

// Test the real implementation
const { result } = renderHook(() => useGetBlogPosts({ page: 1 }))
```

## Writing New Tests

### Test Naming Convention

```typescript
describe('ComponentName', () => {
  it('should <expected behavior> when <condition>', () => {
    // Arrange
    // Act
    // Assert
  })
})
```

### Unit Tests for Stores

```typescript
import { useAppStore } from '@/stores/app-store'

describe('App Store', () => {
  beforeEach(() => {
    // Reset store state
    useAppStore.setState({
      user: null,
      isAuthenticated: false
    })
  })

  it('should set user and mark as authenticated', () => {
    const { setUser } = useAppStore.getState()
    
    setUser({ id: '1', name: 'Test User' })
    
    const state = useAppStore.getState()
    expect(state.user).toBeDefined()
    expect(state.isAuthenticated).toBe(true)
  })
})
```

### Component Integration Tests

```typescript
import { renderWithProviders } from '../../test-utils'
import { BlogPostForm } from '@/components/blog/BlogPostForm'

describe('BlogPostForm Integration', () => {
  it('should submit form with correct data', async () => {
    const mockOnSubmit = vi.fn()
    
    renderWithProviders(
      <BlogPostForm onSubmit={mockOnSubmit} />
    )
    
    await user.type(screen.getByLabelText(/title/i), 'Test Title')
    await user.click(screen.getByRole('button', { name: /publish/i }))
    
    expect(mockOnSubmit).toHaveBeenCalledWith({
      title: 'Test Title',
      status: 'published'
    })
  })
})
```

### Custom Hook Tests

```typescript
import { renderHook, waitFor } from '@testing-library/react'
import { useBlogPosts } from '@/hooks/use-blog-posts'

describe('useBlogPosts Hook', () => {
  it('should fetch and sync data to store', async () => {
    const wrapper = createWrapper()
    
    const { result } = renderHook(
      () => useBlogPosts({ page: 1, limit: 10 }),
      { wrapper }
    )
    
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
    
    expect(result.current.data).toBeDefined()
  })
})
```

## Testing Patterns

### Component Props Testing

```typescript
// Test different prop combinations
const scenarios = [
  { props: { isLoading: true }, expected: 'Loading...' },
  { props: { error: 'Failed' }, expected: 'Error: Failed' },
  { props: { data: mockData }, expected: 'Data loaded' }
]

scenarios.forEach(({ props, expected }) => {
  it(`should render ${expected} when ${Object.keys(props)[0]}`, () => {
    renderWithProviders(<Component {...props} />)
    expect(screen.getByText(expected)).toBeInTheDocument()
  })
})
```

### User Interaction Testing

```typescript
import userEvent from '@testing-library/user-event'

it('should handle user interactions', async () => {
  const user = userEvent.setup()
  
  renderWithProviders(<BlogPostForm />)
  
  // Type in form
  await user.type(screen.getByLabelText(/title/i), 'New Title')
  
  // Click button
  await user.click(screen.getByRole('button', { name: /save/i }))
  
  // Verify result
  expect(screen.getByText(/saved/i)).toBeInTheDocument()
})
```

### Accessibility Testing

```typescript
it('should be accessible', () => {
  renderWithProviders(<BlogPostForm />)
  
  // Check for proper labels
  expect(screen.getByLabelText(/title/i)).toBeInTheDocument()
  
  // Check for ARIA roles
  expect(screen.getByRole('form')).toBeInTheDocument()
  
  // Check keyboard navigation
  const firstInput = screen.getByLabelText(/title/i)
  firstInput.focus()
  expect(firstInput).toHaveFocus()
})
```

## Mock Management

### Next.js Router Mocking

```typescript
const mockPush = vi.fn()

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
  useSearchParams: () => new URLSearchParams()
}))
```

### API Error Testing

```typescript
import { server } from '../../setup'
import { http, HttpResponse } from 'msw'

it('should handle API errors', async () => {
  // Override default success handler
  server.use(
    http.get('/posts', () => {
      return HttpResponse.json(
        { status: 'error', error: { message: 'Server error' } },
        { status: 500 }
      )
    })
  )
  
  renderWithProviders(<BlogPostsList />)
  
  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument()
  })
})
```

## Debugging Tests

### Test Output

```bash
# Show test output
npx vitest run --reporter=verbose

# Show detailed errors
npx vitest run --reporter=verbose --no-truncate
```

### Browser Debugging

```typescript
import { screen } from '@testing-library/react'

it('debug test', () => {
  renderWithProviders(<Component />)
  
  // Print current DOM
  screen.debug()
  
  // Print specific element
  screen.debug(screen.getByRole('button'))
})
```

### IDE Integration

For VS Code, add to `.vscode/settings.json`:

```json
{
  "vitest.enable": true,
  "vitest.commandLine": "npx vitest",
  "typescript.preferences.includePackageJsonAutoImports": "on"
}
```

## Best Practices

### Test Organization

- **Co-locate tests** with tested code when possible
- **Group related tests** in describe blocks
- **Use descriptive test names** that explain the behavior
- **Keep tests focused** on single behaviors

### Component Testing

- **Test user-visible behavior**, not implementation details
- **Use semantic queries** (`getByRole`, `getByLabelText`)
- **Test accessibility** and keyboard navigation
- **Mock external dependencies** but not the component under test

### State Testing

- **Test state transitions** and side effects
- **Verify store synchronization** with API calls
- **Test error states** and edge cases
- **Use realistic test data** that matches production

### API Testing

- **Use generated mock handlers** for consistency
- **Test loading states** and error conditions
- **Verify cache invalidation** and optimistic updates
- **Test request retry logic** and error recovery

## Performance Considerations

### Test Speed

- **Keep unit tests under 10ms** per test
- **Limit integration test complexity**
- **Use shallow rendering** when possible
- **Mock expensive operations**

### Memory Management

```typescript
beforeEach(() => {
  // Reset stores
  useAppStore.getState().reset()
  useBlogStore.getState().reset()
})

afterEach(() => {
  // Cleanup is automatic with Testing Library
  cleanup()
})
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Frontend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install
      - run: pnpm test:ci
      - run: pnpm test:coverage
```

## Test Metrics

### Coverage Goals

- **Components**: 90%+ (user-facing critical)
- **Custom Hooks**: 95%+ (reusable logic)
- **Stores**: 95%+ (state management critical)
- **Utilities**: 90%+

### Performance Targets

- **Unit tests**: < 10ms per test
- **Integration tests**: < 100ms per test
- **Full test suite**: < 60 seconds

Run `npx vitest run --reporter=verbose` to see test performance details.

## Troubleshooting

### Common Issues

1. **Import Errors**: Check path aliases in `vitest.config.ts`
2. **MSW Issues**: Verify server setup and handler configuration
3. **React Errors**: Ensure proper provider wrapping
4. **TypeScript Errors**: Check tsconfig.json includes test files

### Getting Help

- Review existing test examples in this directory
- Check Vitest documentation: https://vitest.dev/
- Review React Testing Library guides: https://testing-library.com/docs/react-testing-library/intro/
- Review TanStack Query testing: https://tanstack.com/query/latest/docs/react/guides/testing

## Related Documentation

- **Backend Tests**: See `tests/backend/README.md` for API testing
- **E2E Tests**: See `tests/e2e/` for end-to-end testing
- **Frontend Guidelines**: See `docs/coding-guidelines/frontend/14_testing.md`
