# 18. Deployment on Vercel

This section outlines the rules and best practices for deploying our **Next.js + TypeScript** applications to **Vercel**, including environment management, build settings, and troubleshooting.

Our goals are:
- Keep deployments **predictable and reproducible**
- Maintain clear separation between environments (preview, staging, production)
- Ensure environment variables are correctly managed and secured
- Optimize build and runtime performance on Vercel


## 1. Connecting the Repository

1. Sign in to [Vercel](https://vercel.com) using your GitHub, GitLab, or Bitbucket account.
2. Import the repository containing your Next.js project.
3. Choose the correct root directory (if not the repository root).
4. Select the **framework preset** for Next.js — Vercel will auto-detect most settings.


## 2. Environment Variables Management

We use three main `.env` files in local development:

- `.env.local` — for local development only (never committed to Git)
- `.env.development` — for development/preview deployments
- `.env.production` — for production deployments

**Rules:**
- Never commit `.env.local` to the repository.
- Set environment variables in **Vercel Project Settings > Environment Variables**.
- Use Vercel’s **Environment** field to scope variables:
  - `Production` → `.env.production`
  - `Preview` → `.env.development` values
  - `Development` → `.env.local` values (local `vercel dev` runs)

**Example variables:**

| Name             | Value                  | Environment |
| ---------------- | ---------------------- | ----------- |
| NEXT_PUBLIC_API  | https://api.example.com| Production  |
| NEXT_PUBLIC_API  | https://staging-api.example.com | Preview  |
| NEXT_PUBLIC_API  | http://localhost:3000  | Development |


## 3. Build Settings and Output Configuration

Default build settings for Next.js projects on Vercel:

- **Framework Preset**: Next.js
- **Build Command**:  
```bash
  pnpm install --frozen-lockfile && pnpm build
````

* **Output Directory**: `.next`
* **Install Command**:

```bash
  pnpm install --frozen-lockfile
```

> Always use `pnpm` (our standard package manager) to ensure consistent installs.


## 4. Preview, Staging, and Production Environments

* **Preview Deployments**:

  * Triggered by pull requests or commits to non-production branches.
  * Use `.env.development` or environment variables scoped to Preview.
  * For QA, design reviews, and stakeholder demos.

* **Production Deployments**:

  * Triggered by merges to the main branch.
  * Uses `.env.production` or Production-scoped environment variables.
  * Only deploy when the main branch is stable and tested.

* **Staging (optional)**:

  * Can be simulated by creating a dedicated branch and mapping it to a custom domain.
  * Useful for pre-production testing.


## 5. Vercel Analytics and Monitoring

* Enable **Vercel Analytics** in the project settings for real-user performance metrics.
* Monitor:

  * Core Web Vitals
  * Page load times
  * Rendering performance

> For more detailed frontend performance tracking, combine with **Lighthouse** audits in CI.


## 6. Common Pitfalls and Troubleshooting

**Problem:** Environment variables not updating
**Solution:** Redeploy after updating environment variables in Vercel; ensure the correct environment scope.

**Problem:** Build fails due to missing dependencies
**Solution:** Check `pnpm-lock.yaml` is committed; run `pnpm install --frozen-lockfile` locally before pushing.

**Problem:** Functions not running as expected
**Solution:** Check the **Runtime Logs** in Vercel dashboard; ensure server actions and API routes are compatible with the target runtime (Edge or Node).

**Problem:** `.env.local` is being used in production
**Solution:** Verify environment variable setup in Vercel; `.env.local` should never be present on production builds.


## 7. Security Best Practices

* Do not expose secret keys in `NEXT_PUBLIC_*` variables unless they are safe for the client.
* Rotate credentials periodically and update them in Vercel settings.
* Use Vercel’s built-in secret storage for sensitive values.


By following these deployment guidelines, we ensure our Next.js applications run **securely, efficiently, and predictably** across all environments on Vercel.
