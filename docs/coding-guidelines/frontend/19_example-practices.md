# 19. Example Practices

This section provides a **practical reference** for recommended coding practices (Do’s) and common pitfalls to avoid (Don’ts) when working on our **Next.js + TypeScript** frontend projects.

Our goals are:
- Reinforce consistent, high-quality coding patterns
- Prevent common mistakes that degrade performance, maintainability, or security
- Serve as a quick review before code reviews and deployments


## ✅ Do’s — Recommended Practices

### 1. General Project Practices
- **Follow the coding guidelines** defined in `01_introduction.md` to `18_vercel-deployment.md`.
- Use **pnpm** for all package installations to ensure consistency.
- Keep `.env.development` out of version control.
- Regularly update dependencies to patch security vulnerabilities.

### 2. Components & Architecture
- **Default to Server Components** unless client interactivity is required.
- Co-locate related UI, data fetching, and tests.
- Keep components small, focused, and reusable.
- Name files and folders consistently using **kebab-case**.

### 3. Data Fetching & State Management
- Use **TanStack Query** for server state fetching, caching, and mutations.
- Use **Zustand** for minimal client-side state.
- Apply caching strategies instead of defaulting to `no-store`.
- Invalidate queries appropriately after mutations.

### 4. Styling
- Use **Tailwind CSS** utility classes for styling.
- Use **shadcn/ui** components to maintain design consistency.
- Prefer design tokens (colors, spacing, typography) from Tailwind config over hardcoded values.

### 5. Forms & Validation
- Use **Zod** for schema-based validation.
- Validate both client-side and server-side.

### 6. Testing
- Follow the **Testing Trophy** principle:
  - Write more integration and unit tests than E2E tests.
  - Use **Vitest** + **Testing Library** for component and logic tests.
  - Use **Playwright** for essential E2E scenarios.
  - Use **MSW** for API mocking in tests.
- Keep test files next to the code they test when possible.

### 7. Performance
- Use **next/image** for image optimization.
- Use **next/font** for self-hosted fonts to avoid layout shift.
- Avoid unnecessary client-side JavaScript and large dependencies.

### 8. Deployment
- Keep environment variables scoped to the correct environment (Preview/Production).
- Monitor performance via Vercel Analytics and Lighthouse.
- Ensure production builds are tested locally before deploying.


## ❌ Don’ts — Common Pitfalls to Avoid

### 1. General Project Mistakes
- ❌ Commit `.env.development` or other sensitive files.
- ❌ Install packages without `pnpm` — it may break dependency consistency.
- ❌ Disable TypeScript strict mode.

### 2. Components & Architecture
- ❌ Overuse Client Components — they increase bundle size and hydration cost.
- ❌ Mix unrelated concerns in the same component or file.
- ❌ Use magic strings for route paths — centralize them.

### 3. Data Fetching & State Management
- ❌ Fetch data in Client Components when it can be fetched on the server.
- ❌ Store server state in Zustand — use TanStack Query instead.
- ❌ Forget to invalidate queries after mutations.

### 4. Styling
- ❌ Write large amounts of custom CSS without using Tailwind utilities.
- ❌ Inline styles for theme-dependent values — use Tailwind tokens.

### 5. Forms & Validation
- ❌ Skip server-side validation — client validation can be bypassed.
- ❌ Write ad-hoc validation logic without using Zod.

### 6. Testing
- ❌ Rely solely on E2E tests — they are slow and brittle.
- ❌ Write snapshot tests for dynamic UI without meaningful assertions.
- ❌ Mock everything in integration tests — test real flows where possible.

### 7. Performance
- ❌ Use unoptimized `<img>` instead of `next/image`.
- ❌ Load large libraries globally when they can be dynamically imported.
- ❌ Ignore Lighthouse performance or accessibility warnings.

### 8. Deployment
- ❌ Use `.env.development` in production builds.
- ❌ Push directly to the main branch without PR review.
- ❌ Deploy untested code to production.


By following the **Do’s** and avoiding the **Don’ts**, we ensure our Next.js applications remain **performant, secure, maintainable, and consistent**.
