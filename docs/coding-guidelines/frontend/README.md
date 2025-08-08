# Next.js + TypeScript Coding Guidelines (App Router + RSC)

This document serves as the **table of contents** for the frontend coding guidelines of our Next.js + TypeScript projects using the App Router and React Server Components (RSC).  
Each section links to a dedicated file with detailed rules, best practices, and examples.  
It is intended for both **human developers** and **AI-based tools** to ensure code quality, maintainability, and consistency across the codebase.

## 1. Introduction & Scope
- [01_introduction.md](./01_introduction.md)
- Purpose of the guidelines  
- Target audience (developers, AI assistants, linters)  
- Applicable Next.js, React, and TypeScript versions  
- Library

## 2. Project Setup
- [02_project-setup.md](./02_project-setup.md)
- Project initialization  
- TypeScript configuration  
- Code linter and formatter (Biome) setup 
- next.config typing & structure  

## 3. Directory Structure & Routing
- [03_routing.md](./routing.md)
- Directory structure best practice
- App Router usage (`/app` directory)  
- File conventions (`layout.tsx`, `page.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx`)  
- Route Handlers (`route.ts`)  
- Co-location of UI, data fetching, and tests  

## 4. Server vs Client Components
- [04_components.md](./04_components.md)
- Default to Server Components  
- When to use Client Components  
- `'use client'` boundary rules  
- Component streaming with `<Suspense>`  

## 5. Data Fetching & Caching
- [05_fetching-caching.md](./05_fetching-caching.md)
- Server-side data fetching with extended `fetch()`  
- Caching strategies (time-based, tag-based, path-based)  
- Avoiding unnecessary `no-store`  
- Co-location of fetch logic  

## 6. State Management
- [06_state-management.md](./06_state-management.md)
- When to use global state vs. server state  
- **Zustand** for lightweight client-side state  
- **TanStack Query** for server state management and caching  
- Combining RSC with client-side state libraries  
- Guidelines for query key naming and cache invalidation  

## 7. Mutations & Server Actions
- [07_server-actions.md](./07_server-actions.md)
- `"use server"` directive usage  
- Triggering Server Actions (form, button)  
- Serialization rules for inputs/outputs  
- Cache invalidation after mutations  

## 8. Navigation & Linking
- [08_navigation.md](./08_navigation.md)
- `next/link` best practices  
- Prefetching behavior  
- Typed routes (experimental)  

## 9. Metadata & SEO
- [09_metadata.md](./09_metadata.md)
- Metadata API usage (`metadata`, `generateMetadata`)  
- OG/Twitter image generation  
- robots.txt, sitemap.xml placement  

## 10. Styling & Assets
- [10_styling.md](./10_styling.md)
- styling with Tailwind CSS
- `next/font` for self-hosted fonts  
- `next/image` for image optimization  

## 11. Middleware & Edge Functions
- [11_middleware.md](./11_middleware.md)
- Use cases for `middleware.ts`  
- Performance considerations  

## 12. Error & State Handling
- [12_error-handling.md](./12_error-handling.md)
- `error.tsx` and `not-found.tsx`  
- `loading.tsx` and Suspense fallbacks  
- Redirects and `notFound()` helper  

## 13. TypeScript Rules
- [13_typescript.md](./13_typescript.md)
- Compiler strictness  
- Explicit types for props and exports  
- Avoiding `any`  
- Advanced compiler options (`noUncheckedIndexedAccess`, etc.)  

## 14. Testing Strategy
- [14_testing.md](./14_testing.md)
- Unit/integration testing (Vitest)  
- Mock server worker
- E2E testing tools (Playwright)  
- Testing Server Actions and Route Handlers  

## 15. Performance Best Practices
- [15_performance-optimization.md](./15_performance-optimization.md)
- Minimizing client JS  
- Streaming strategies  
- Image/font optimization  
- Avoiding unnecessary dynamic rendering  

## 16. Storybook & UI Development
- [16_storybook.md](./16_storybook.md)
- Setting up Storybook in a Next.js project  
- Writing stories for components and pages  
- Using Storybook for visual regression testing  
- Integrating with design systems and Figma  
- Best practices for organizing stories and decorators  

## 17. Deployment on Vercel
- [17_vercel-deployment.md](./17_vercel-deployment.md)
- Connecting Git repository to Vercel  
- Environment variables management (`.env.local`, `.env.production`)  
- Build settings and output configuration  
- Preview, staging, and production environments  
- Using Vercel analytics and monitoring  
- Common pitfalls and troubleshooting tips  

## 18. Do’s and Don’ts Checklist
- [18_example-practices.md](./18_example-practices.md)
- Recommended practices  
- Common pitfalls to avoid  

accessibility
