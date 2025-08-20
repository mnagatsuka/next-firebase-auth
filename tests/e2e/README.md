# End-to-End Testing Guide

This directory contains comprehensive end-to-end tests using **Playwright** following the **Testing Trophy** approach. E2E tests verify critical user journeys across the entire application stack (frontend + backend).

## Test Structure

```
tests/e2e/
├── blog-navigation.spec.ts    # Core navigation and browsing flows
├── blog-post-creation.spec.ts # Post creation and editing workflows
└── README.md                  # This documentation
```

**Note**: E2E tests are located at project root level since they test the complete application stack, while unit/integration tests are in their respective `tests/frontend/` and `tests/backend/` directories.

## Quick Start

### 1. Install Dependencies

E2E tests use Playwright which is installed at the project root:

```bash
# From project root directory
pnpm install

# Install Playwright browsers (first time only)
npx playwright install
```

### 2. Start Application Stack

E2E tests require both frontend and backend to be running. Use Docker Compose for the easiest setup:

```bash
# From project root directory
docker-compose up

# Or run in background
docker-compose up -d

# Application will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
```

**Alternative: Manual startup** (if Docker is not available):

```bash
# Terminal 1: Start backend
cd backend/
uv run fastapi dev src/app/main.py

# Terminal 2: Start frontend  
cd frontend/
pnpm dev
```

### 3. Run E2E Tests

```bash
# From project root directory
npx playwright test

# Run specific test file
npx playwright test tests/e2e/blog-navigation.spec.ts

# Run with UI (visual test runner)
npx playwright test --ui
```

## Test Categories

### Critical User Journeys

E2E tests focus on **essential user flows** that must work correctly:

```bash
# Blog navigation and browsing
npx playwright test tests/e2e/blog-navigation.spec.ts

# Post creation and editing workflows
npx playwright test tests/e2e/blog-post-creation.spec.ts
```

### Cross-Browser Testing

```bash
# Run on all configured browsers (Chrome, Firefox, Safari)
npx playwright test

# Run on specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Mobile Testing

```bash
# Run mobile viewport tests
npx playwright test --project="Mobile Chrome"
npx playwright test --project="Mobile Safari"
```

## Test Execution Options

### Headless vs Headed Mode

```bash
# Headless (default, faster)
npx playwright test

# Headed mode (see browser window)
npx playwright test --headed

# Debug mode (opens browser dev tools)
npx playwright test --debug
```

### Test Reports

```bash
# Generate HTML report
npx playwright test --reporter=html

# View last test report
npx playwright show-report

# Generate JUnit XML for CI
npx playwright test --reporter=junit
```

### Parallel Execution

```bash
# Run tests in parallel (default)
npx playwright test

# Control worker count
npx playwright test --workers=4

# Run tests sequentially
npx playwright test --workers=1
```

### Specific Test Selection

```bash
# Run tests matching pattern
npx playwright test --grep "navigation"

# Run specific test method
npx playwright test tests/e2e/blog-navigation.spec.ts -g "should navigate to individual blog post"

# Run tests by tag (if using test tags)
npx playwright test --grep "@smoke"
```

## Test Configuration

### Playwright Configuration (`playwright.config.ts`)

Located at project root with configuration for:
- **Multiple browsers** (Chrome, Firefox, Safari)
- **Mobile viewports** (iPhone, Android)
- **Base URL** configuration
- **Automatic web server** startup
- **Screenshots and videos** on failure
- **Trace collection** for debugging

### Web Server Auto-Start

The configuration can automatically start the frontend dev server:

```typescript
webServer: {
  command: 'cd frontend && pnpm dev',
  url: 'http://localhost:3000',
  reuseExistingServer: !process.env.CI,
  timeout: 120 * 1000,
}
```

**Note**: When using Docker Compose, make sure to start the services first with `docker-compose up` before running Playwright tests, as the auto-start only handles the frontend server.

### Test Environment

E2E tests run against:
- **Frontend**: Next.js dev server (http://localhost:3000)
- **Backend**: FastAPI server (http://localhost:8000)
- **Real Browser**: Chromium/Firefox/WebKit
- **Database**: Test database (isolated from development)
- **Network**: Docker bridge network (app-network) when using Docker Compose

## Writing New E2E Tests

### Test Structure

```typescript
import { test, expect } from '@playwright/test'

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup that runs before each test
    await page.goto('/')
  })

  test('should perform user action and verify result', async ({ page }) => {
    // Test implementation
  })
})
```

### Page Navigation Tests

```typescript
test('should navigate through application', async ({ page }) => {
  // Navigate to page
  await page.goto('/')
  
  // Verify page loaded
  await expect(page).toHaveTitle(/expected title/i)
  
  // Click navigation element
  await page.getByRole('link', { name: /blog/i }).click()
  
  // Verify navigation worked
  await expect(page).toHaveURL(/\/blog/)
  await expect(page.getByRole('heading', { name: /blog/i })).toBeVisible()
})
```

### Form Interaction Tests

```typescript
test('should create new blog post', async ({ page }) => {
  await page.goto('/create-post')
  
  // Fill form fields
  await page.getByLabel(/title/i).fill('My New Post')
  await page.getByLabel(/content/i).fill('Post content here')
  
  // Submit form
  await page.getByRole('button', { name: /publish/i }).click()
  
  // Verify success
  await expect(page).toHaveURL('/')
  await expect(page.getByText(/post created successfully/i)).toBeVisible()
  await expect(page.getByText('My New Post')).toBeVisible()
})
```

### API State Verification

```typescript
test('should reflect API changes in UI', async ({ page }) => {
  // Navigate to blog list
  await page.goto('/')
  
  // Count initial posts
  const initialPosts = await page.getByTestId('post-card').count()
  
  // Create new post
  await page.goto('/create-post')
  await page.getByLabel(/title/i).fill('API Test Post')
  await page.getByRole('button', { name: /publish/i }).click()
  
  // Verify post appears in list
  await page.goto('/')
  const newPostCount = await page.getByTestId('post-card').count()
  expect(newPostCount).toBe(initialPosts + 1)
  await expect(page.getByText('API Test Post')).toBeVisible()
})
```

### Error Handling Tests

```typescript
test('should handle API errors gracefully', async ({ page }) => {
  // Navigate to form
  await page.goto('/create-post')
  
  // Try to submit invalid data or simulate network error
  await page.getByLabel(/title/i).fill('') // Invalid empty title
  await page.getByRole('button', { name: /publish/i }).click()
  
  // Verify error handling
  await expect(page.getByText(/title is required/i)).toBeVisible()
  await expect(page).toHaveURL('/create-post') // Should stay on form
})
```

## Browser-Specific Testing

### Responsive Design

```typescript
test('should work on mobile viewport', async ({ page }) => {
  // Set mobile viewport
  await page.setViewportSize({ width: 375, height: 667 })
  
  await page.goto('/')
  
  // Test mobile-specific behavior
  await expect(page.getByRole('button', { name: /menu/i })).toBeVisible()
  
  // Test mobile navigation
  await page.getByRole('button', { name: /menu/i }).click()
  await expect(page.getByRole('navigation')).toBeVisible()
})
```

### Cross-Browser Features

```typescript
test('should work in all browsers', async ({ page, browserName }) => {
  await page.goto('/interactive-feature')
  
  // Test might behave differently in different browsers
  if (browserName === 'webkit') {
    // Safari-specific test adjustments
  }
  
  await expect(page.getByRole('button')).toBeVisible()
})
```

## Test Data Management

### Test Isolation

```typescript
test.describe('Blog Post Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Each test gets fresh data
    await page.goto('/reset-test-data') // If you have a test data reset endpoint
  })
  
  test.afterEach(async ({ page }) => {
    // Cleanup after each test if needed
  })
})
```

### Mock External Services

```typescript
test('should handle external API failures', async ({ page }) => {
  // Mock external API to return error
  await page.route('**/external-api/**', route => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'External service unavailable' })
    })
  })
  
  await page.goto('/feature-using-external-api')
  
  // Verify graceful error handling
  await expect(page.getByText(/service temporarily unavailable/i)).toBeVisible()
})
```

## Debugging E2E Tests

### Visual Debugging

```bash
# Run in headed mode to see browser
npx playwright test --headed

# Run with slow motion
npx playwright test --headed --slowMo=1000

# Debug specific test
npx playwright test tests/e2e/blog-navigation.spec.ts --debug
```

### Screenshots and Videos

```typescript
test('debug test with screenshots', async ({ page }) => {
  await page.goto('/')
  
  // Take screenshot at specific point
  await page.screenshot({ path: 'debug-homepage.png' })
  
  // Continue with test...
  await page.getByRole('link').click()
  
  // Take another screenshot
  await page.screenshot({ path: 'debug-after-click.png' })
})
```

### Trace Viewer

```bash
# Run with trace on (automatic on failure)
npx playwright test --trace=on

# View trace for failed test
npx playwright show-trace test-results/*/trace.zip
```

### Console and Network Logs

```typescript
test('debug with logs', async ({ page }) => {
  // Listen to console logs
  page.on('console', msg => console.log('PAGE LOG:', msg.text()))
  
  // Listen to network requests
  page.on('request', request => 
    console.log('REQUEST:', request.method(), request.url())
  )
  
  // Listen to responses
  page.on('response', response =>
    console.log('RESPONSE:', response.status(), response.url())
  )
  
  await page.goto('/')
  // Logs will appear in terminal
})
```

## Performance Testing

### Page Load Performance

```typescript
test('should load pages quickly', async ({ page }) => {
  const startTime = Date.now()
  
  await page.goto('/')
  await page.waitForLoadState('networkidle')
  
  const loadTime = Date.now() - startTime
  expect(loadTime).toBeLessThan(3000) // Should load in under 3 seconds
})
```

### Core Web Vitals

```typescript
test('should have good core web vitals', async ({ page }) => {
  await page.goto('/')
  
  // Measure Largest Contentful Paint
  const lcp = await page.evaluate(() => {
    return new Promise((resolve) => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const lastEntry = entries[entries.length - 1]
        resolve(lastEntry.startTime)
      }).observe({ entryTypes: ['largest-contentful-paint'] })
    })
  })
  
  expect(lcp).toBeLessThan(2500) // Good LCP is under 2.5s
})
```

## Accessibility Testing

### Basic Accessibility

```typescript
test('should be accessible', async ({ page }) => {
  await page.goto('/')
  
  // Check for proper heading structure
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  
  // Check for alt text on images
  const images = await page.getByRole('img').all()
  for (const img of images) {
    expect(await img.getAttribute('alt')).toBeTruthy()
  }
  
  // Test keyboard navigation
  await page.keyboard.press('Tab')
  await expect(page.locator(':focus')).toBeVisible()
})
```

### Screen Reader Testing

```typescript
test('should work with screen readers', async ({ page }) => {
  await page.goto('/')
  
  // Check for proper ARIA labels
  await expect(page.getByRole('navigation')).toHaveAttribute('aria-label')
  
  // Check for form labels
  await page.goto('/create-post')
  await expect(page.getByLabelText(/title/i)).toBeVisible()
  
  // Check for error announcements
  await page.getByRole('button', { name: /submit/i }).click()
  await expect(page.getByRole('alert')).toBeVisible()
})
```

## CI/CD Integration

### GitHub Actions

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      
      - name: Start application stack
        run: |
          docker-compose up -d
          # Wait for services to be ready
          sleep 30
        
      - name: Run E2E tests
        run: npx playwright test
        
      - name: Stop application stack
        run: docker-compose down
        
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

### Docker Integration

For running E2E tests in a containerized environment:

```dockerfile
# Dockerfile for E2E tests
FROM mcr.microsoft.com/playwright:v1.40.0-focal

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
CMD ["npx", "playwright", "test"]
```

**Using with Docker Compose**:

```yaml
# docker-compose.e2e.yml
version: '3.8'
services:
  e2e-tests:
    build:
      context: .
      dockerfile: Dockerfile.e2e
    depends_on:
      - backend
      - frontend
    environment:
      - BASE_URL=http://frontend:3000
    networks:
      - app-network

  # Include backend and frontend services from main docker-compose.yml
```

Run with: `docker-compose -f docker-compose.yml -f docker-compose.e2e.yml up e2e-tests`

## Best Practices

### Test Organization

- **Focus on critical user journeys** only
- **Keep E2E tests minimal** (highest cost, slowest)
- **Group related flows** in same test file
- **Use descriptive test names** that explain user value

### Page Object Pattern

```typescript
// pages/blog-page.ts
export class BlogPage {
  constructor(private page: Page) {}
  
  async goto() {
    await this.page.goto('/')
  }
  
  async createPost(title: string, content: string) {
    await this.page.goto('/create-post')
    await this.page.getByLabel(/title/i).fill(title)
    await this.page.getByLabel(/content/i).fill(content)
    await this.page.getByRole('button', { name: /publish/i }).click()
  }
  
  async expectPostVisible(title: string) {
    await expect(this.page.getByText(title)).toBeVisible()
  }
}

// Use in tests
test('should create and display post', async ({ page }) => {
  const blogPage = new BlogPage(page)
  
  await blogPage.createPost('Test Title', 'Test Content')
  await blogPage.expectPostVisible('Test Title')
})
```

### Reliable Selectors

```typescript
// ✅ Good: Semantic selectors
await page.getByRole('button', { name: /submit/i })
await page.getByLabel(/email address/i)
await page.getByText(/welcome back/i)

// ✅ Good: Test IDs for unique elements
await page.getByTestId('user-profile-menu')

// ❌ Avoid: CSS selectors that can break
await page.locator('.btn-primary')
await page.locator('#submit-form')
```

### Wait Strategies

```typescript
// ✅ Good: Wait for specific content
await expect(page.getByText(/loading complete/i)).toBeVisible()

// ✅ Good: Wait for network requests
await page.waitForResponse('**/api/posts')

// ✅ Good: Wait for element state
await page.waitForLoadState('networkidle')

// ❌ Avoid: Fixed timeouts
await page.waitForTimeout(3000)
```

## Performance Targets

### Test Execution Speed

- **Individual test**: < 30 seconds
- **Full E2E suite**: < 10 minutes
- **CI pipeline**: < 15 minutes (including setup)

### Browser Coverage

- **Chrome/Chromium**: Primary browser (latest)
- **Firefox**: Cross-browser validation
- **Safari/WebKit**: macOS/iOS compatibility
- **Mobile**: iPhone and Android viewports

## Troubleshooting

### Common Issues

1. **Flaky Tests**: Use proper waits, avoid timeouts
2. **Element Not Found**: Check selectors, wait for content
3. **Browser Crashes**: Update Playwright, check system resources
4. **Slow Tests**: Optimize waits, reduce test scope

### Debug Commands

```bash
# Run with debug output
npx playwright test --debug

# Generate trace file
npx playwright test --trace=on

# Run single test with headed browser
npx playwright test tests/e2e/blog-navigation.spec.ts --headed --workers=1

# Record new test interactively
npx playwright codegen http://localhost:3000
```

### Getting Help

- Review existing test examples in this directory
- Check Playwright documentation: https://playwright.dev/
- Review test reports in `playwright-report/`
- See related documentation:
  - Frontend tests: `tests/frontend/README.md`
  - Backend tests: `tests/backend/README.md`

## Test Maintenance

### Updating Tests

- **Review tests** when UI changes
- **Update selectors** when elements change
- **Add tests** for new critical features
- **Remove tests** for deprecated features

### Monitoring Test Health

```bash
# Check test flakiness
npx playwright test --repeat-each=5

# Performance profiling
npx playwright test --trace=on --reporter=html

# Cross-browser compatibility check
npx playwright test --project=chromium --project=firefox --project=webkit
```

## Related Documentation

- **Frontend Tests**: See `tests/frontend/README.md` for component/integration tests
- **Backend Tests**: See `tests/backend/README.md` for API testing
- **Testing Guidelines**: See `docs/coding-guidelines/frontend/14_testing.md`
- **Playwright Config**: See root `playwright.config.ts` for configuration details