# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

This is a **documentation-first repository** for a Next.js + Firebase Auth project that has not yet been initialized. The repository contains comprehensive coding guidelines but no actual implementation yet.

## Project Architecture (Planned)

Based on the extensive documentation, this will be a modern Next.js application with:

- **Next.js 15.x** with App Router and React Server Components (RSC)
- **TypeScript 5.x** with strict typing enabled
- **Firebase Auth** for authentication
- **Tailwind CSS** + **shadcn/ui** for styling
- **Zustand** for client-side state management
- **TanStack Query** for server state and caching
- **Zod** for schema validation

## Development Commands (When Project is Initialized)

The project will use **pnpm** as the package manager. Expected commands:

```bash
# Install dependencies
pnpm install

# Development server
pnpm dev

# Build for production
pnpm build

# Code quality
pnpm biome check .    # Lint and format with Biome
pnpm typecheck        # TypeScript checking

# Testing
pnpm test            # Unit tests with Vitest
pnpm test:e2e        # E2E tests with Playwright

# Docker development
docker-compose up    # Local containerized development
```

## Project Initialization

To initialize the actual project following the guidelines:

1. Run the Next.js creation command from `docs/coding-guidelines/frontend/02_project-setup.md`:
   ```bash
   pnpm create next-app@latest . \
     --typescript \
     --eslint \
     --app \
     --src-dir \
     --import-alias "@/*"
   ```

2. Set up the required configuration files:
   - `tsconfig.json` with strict TypeScript settings
   - `biome.json` for linting/formatting
   - `next.config.ts` (typed configuration)
   - `docker-compose.yml` for local development

## Key Guidelines to Follow

When implementing this project, follow the comprehensive guidelines in `docs/coding-guidelines/frontend/`:

- Use **Server Components by default**, only add `'use client'` when necessary
- Implement **strict TypeScript** typing for all props and functions
- Use **pnpm** exclusively (never npm or yarn)
- Follow the **App Router** patterns with proper file conventions
- Use **Biome** for code formatting and linting
- Container development with **Docker Compose**
- Deploy to **Vercel** following the deployment guidelines

## Documentation Structure

- `docs/coding-guidelines/frontend/` - Complete frontend development guidelines (18 detailed files)
- `docs/specifications/` - Project specifications (currently empty)
- Main `README.md` - Basic project description

## Authentication Architecture (Planned)

The project will integrate **Firebase Auth** with the Next.js App Router, likely using:
- Server-side session management
- Protected routes with middleware
- Client-side auth state with Zustand
- Server Actions for auth operations