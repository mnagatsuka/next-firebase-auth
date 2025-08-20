import type { FullConfig } from '@playwright/test'

async function waitForHealth(url: string, timeoutMs = 120_000): Promise<void> {
  const start = Date.now()
  let lastErr: unknown
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url)
      if (res.ok) {
        return
      }
      lastErr = new Error(`Health check non-OK: ${res.status}`)
    } catch (e) {
      lastErr = e
    }
    await new Promise((r) => setTimeout(r, 1000))
  }
  throw new Error(`Backend health check failed: ${String(lastErr)}`)
}

export default async function globalSetup(_config: FullConfig) {
  // Wait for backend to be up (docker-compose started by webServer)
  await waitForHealth('http://localhost:8000/health')

  // NOTE: Seeding of deterministic data (e.g., a post with id 'post-123')
  // requires backend support for fixed IDs or a dedicated seeding route.
  // Pending approval, we will add a test-only seeding endpoint and call it here.
}

