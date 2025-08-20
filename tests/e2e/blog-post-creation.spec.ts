import { test, expect } from '@playwright/test'

test.describe('Blog Post Creation E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to create post page before each test
    await page.goto('/create-post')
  })

  test('should create a new blog post successfully', async ({ page }) => {
    // Should show the create post form
    await expect(page.getByRole('heading', { name: /create new blog post/i })).toBeVisible()

    // Fill in the form
    await page.getByLabel(/title/i).fill('My New Test Post')
    await page.getByLabel(/excerpt/i).fill('This is a test excerpt for my new post')
    await page.getByLabel(/content/i).fill('# My New Post\n\nThis is the content of my new blog post. It contains markdown formatting and detailed information.')

    // Add some tags
    await page.getByLabel(/tags/i).fill('testing')
    await page.getByRole('button', { name: /add/i }).click()
    await page.getByLabel(/tags/i).fill('playwright')
    await page.keyboard.press('Enter')

    // Verify tags were added
    await expect(page.getByText('testing')).toBeVisible()
    await expect(page.getByText('playwright')).toBeVisible()

    // Publish the post
    await page.getByRole('button', { name: /publish/i }).click()

    // Should navigate back to home page and show success message
    await expect(page).toHaveURL('/')
    await expect(page.getByText(/post created successfully/i)).toBeVisible()

    // The new post should appear in the blog list
    await expect(page.getByText('My New Test Post')).toBeVisible()
  })

  test('should save post as draft', async ({ page }) => {
    // Fill in minimum required fields
    await page.getByLabel(/title/i).fill('Draft Post Title')
    await page.getByLabel(/content/i).fill('This is a draft post content.')

    // Save as draft
    await page.getByRole('button', { name: /save draft/i }).click()

    // Should show success message
    await expect(page.getByText(/draft saved successfully/i)).toBeVisible()
    await expect(page).toHaveURL('/')
  })

  test('should validate required fields', async ({ page }) => {
    // Try to publish without filling required fields
    const publishButton = page.getByRole('button', { name: /publish/i })
    await expect(publishButton).toBeDisabled()

    // Fill only title
    await page.getByLabel(/title/i).fill('Test Title')
    await expect(publishButton).toBeDisabled() // Still disabled without content

    // Fill content
    await page.getByLabel(/content/i).fill('Test content')
    await expect(publishButton).toBeEnabled() // Now should be enabled
  })

  test('should handle tag management correctly', async ({ page }) => {
    // Add tags using different methods
    await page.getByLabel(/tags/i).fill('react')
    await page.keyboard.press('Enter')
    await expect(page.getByText('react')).toBeVisible()

    await page.getByLabel(/tags/i).fill('nextjs')
    await page.getByRole('button', { name: /add/i }).click()
    await expect(page.getByText('nextjs')).toBeVisible()

    // Try to add duplicate tag
    await page.getByLabel(/tags/i).fill('react')
    await page.keyboard.press('Enter')
    
    // Should still have only one 'react' tag
    const reactTags = page.getByText('react')
    await expect(reactTags).toHaveCount(1)

    // Remove a tag
    await page.getByText('react').locator('..').getByRole('button').click()
    await expect(page.getByText('react')).not.toBeVisible()
    await expect(page.getByText('nextjs')).toBeVisible()
  })

  test('should handle form cancellation', async ({ page }) => {
    // Fill some data
    await page.getByLabel(/title/i).fill('Title to be cancelled')
    await page.getByLabel(/content/i).fill('Content to be cancelled')

    // Cancel the form
    await page.getByRole('button', { name: /cancel/i }).click()

    // Should navigate away (back to previous page or home)
    await expect(page).not.toHaveURL('/create-post')
  })

  test('should be accessible via keyboard navigation', async ({ page }) => {
    // Navigate through form using keyboard
    await page.keyboard.press('Tab') // Should focus on title
    await expect(page.getByLabel(/title/i)).toBeFocused()

    await page.keyboard.press('Tab') // Should focus on excerpt
    await expect(page.getByLabel(/excerpt/i)).toBeFocused()

    await page.keyboard.press('Tab') // Should focus on content
    await expect(page.getByLabel(/content/i)).toBeFocused()

    // Fill form using keyboard
    await page.keyboard.press('Tab') // Move to tags
    await page.keyboard.press('Tab') // Move to add button
    await page.keyboard.press('Tab') // Move to cancel button
    await expect(page.getByRole('button', { name: /cancel/i })).toBeFocused()

    await page.keyboard.press('Tab') // Move to save draft
    await expect(page.getByRole('button', { name: /save draft/i })).toBeFocused()

    await page.keyboard.press('Tab') // Move to publish
    await expect(page.getByRole('button', { name: /publish/i })).toBeFocused()
  })
})
