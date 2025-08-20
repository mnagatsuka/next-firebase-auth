import { test, expect } from '@playwright/test'

const API_BASE = process.env.E2E_API_BASE ?? 'http://localhost:8000'

async function createPost(request: any, overrides?: Partial<{ title: string; excerpt: string; content: string; status: 'draft'|'published' }>) {
  const title = overrides?.title ?? `E2E Post ${Date.now()}`
  const excerpt = overrides?.excerpt ?? 'E2E excerpt for navigation tests.'
  const content = overrides?.content ?? '# E2E Content\n\nThis is an E2E-created blog post.'
  const status = overrides?.status ?? 'published'

  const res = await request.post(`${API_BASE}/posts`, {
    data: { title, excerpt, content, status },
  })
  expect(res.ok()).toBeTruthy()
  const json = await res.json()
  const id = json?.data?.id as string
  expect(id).toBeTruthy()
  return { id, title, excerpt, content }
}

test.describe('Blog Navigation E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page before each test
    await page.goto('/')
  })

  test('should navigate through blog homepage and view posts', async ({ page, request }) => {
    const post = await createPost(request)
    // Should load the blog homepage
    await expect(page).toHaveTitle(/create next app/i)
    await expect(page.getByRole('heading', { name: /blog/i })).toBeVisible()

    // Should show blog post we just created
    await expect(page.getByText(post.title)).toBeVisible()

    // Should have pagination if there are multiple pages
    const nextButton = page.getByRole('button', { name: /next/i })
    if (await nextButton.isVisible()) {
      await expect(nextButton).toBeVisible()
    }
  })

  test('should navigate to individual blog post', async ({ page, request }) => {
    const post = await createPost(request, { content: '# Title\n\nBody content for e2e detail.' })

    // Click on a blog post title to navigate to detail page
    await page.getByText(post.title).click()

    // Should navigate to the post detail page
    await expect(page).toHaveURL(new RegExp(`/posts/${post.id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`))

    // Should show the full blog post content
    await expect(page.getByRole('heading', { name: new RegExp(post.title, 'i') })).toBeVisible()
    await expect(page.getByText(/body content for e2e detail/i)).toBeVisible()

    // Should show comments section header if rendered
    await expect(page.getByText(/comments/i)).toBeVisible()
  })

  test('should handle pagination correctly', async ({ page }) => {
    // Check if pagination exists (assuming we have multiple pages)
    const nextButton = page.getByRole('button', { name: /next/i })
    
    if (await nextButton.isVisible()) {
      // Click next page
      await nextButton.click()

      // URL should update with page parameter
      await expect(page).toHaveURL(/\?page=2/)

      // Should still show blog posts
      await expect(page.getByRole('heading', { name: /blog/i })).toBeVisible()

      // Previous button should now be visible
      await expect(page.getByRole('button', { name: /previous/i })).toBeVisible()

      // Go back to first page
      await page.getByRole('button', { name: '1' }).click()
      await expect(page).toHaveURL('/')
    }
  })

  test('should maintain responsive design on mobile', async ({ page, request }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })

    // Should still show main content
    await expect(page.getByRole('heading', { name: /blog/i })).toBeVisible()
    const post = await createPost(request)
    await expect(page.getByText(post.title)).toBeVisible()

    // Navigation should be mobile-friendly
    await page.getByText(post.title).click()
    await expect(page.getByRole('heading', { name: new RegExp(post.title, 'i') })).toBeVisible()
  })

  test('should handle loading states gracefully', async ({ page }) => {
    // Navigate to a page that might show loading
    await page.goto('/?page=2')

    // Should not show any error states
    await expect(page.getByText(/error/i)).not.toBeVisible()
    await expect(page.getByText(/failed/i)).not.toBeVisible()

    // Should eventually show content
    await expect(page.getByRole('heading', { name: /blog/i })).toBeVisible()
  })

  test('should navigate back to home from post detail', async ({ page, request }) => {
    const post = await createPost(request)
    await page.getByText(post.title).click()
    await expect(page).toHaveURL(new RegExp(`/posts/${post.id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`))

    // Navigate back using browser back button
    await page.goBack()
    await expect(page).toHaveURL('/')
    await expect(page.getByRole('heading', { name: /blog/i })).toBeVisible()
  })

  test('should handle direct URL access to post', async ({ page, request }) => {
    const post = await createPost(request, { content: 'Direct URL content check.' })
    // Navigate directly to a post URL
    await page.goto(`/posts/${post.id}`)

    // Should load the post directly
    await expect(page.getByRole('heading', { name: new RegExp(post.title, 'i') })).toBeVisible()
    await expect(page.getByText(/direct url content check/i)).toBeVisible()
  })

  test('should handle 404 for non-existent posts', async ({ page }) => {
    // Navigate to a non-existent post
    await page.goto('/posts/non-existent-post')

    // Should show 404 or error state
    await expect(page.getByText(/not found|404/i)).toBeVisible()
  })
})
