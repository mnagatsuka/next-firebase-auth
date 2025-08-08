# 1. Introduction & Scope

This document outlines the **purpose**, **scope**, and **applicable context** for our frontend coding guidelines for **Next.js + TypeScript** projects built with the **App Router** and **React Server Components (RSC)**.

It is intended to be read before diving into the individual sections, as it explains the audience, versions, and libraries that these rules cover.


## Purpose of the Guidelines

The primary goals of these guidelines are to:

- **Ensure consistency** across the codebase, regardless of who writes the code (human developers or AI-assisted tools).
- **Improve maintainability** by standardizing patterns for structure, naming, and architecture.
- **Promote best practices** in performance, accessibility, and scalability.
- **Facilitate collaboration** between team members by reducing friction in code reviews and onboarding.
- **Enable AI-assisted development** by providing clear, machine-readable rules.

These rules are not static — they should evolve as our tech stack, project requirements, and the Next.js ecosystem grow.


## Target Audience

These guidelines apply to:

- **Human developers** — frontend engineers working on our Next.js projects.
- **AI coding assistants** — tools like GitHub Copilot, ChatGPT, and similar, to help produce compliant code automatically.
- **Automated code quality tools** — linters, formatters, type checkers, and CI/CD pipelines.


## Applicable Versions

These guidelines are written for:

- **Next.js**: `15.x` and later  
- **React**: `18.x` (including support for React Server Components)  
- **TypeScript**: `5.x` with strict compiler settings enabled  

The recommendations may not apply to older versions.


## Libraries & Tools in Scope

While the primary focus is **Next.js + TypeScript**, the following libraries and tools are part of our standard setup:

### 1. State Management
- **Zustand** — minimal and flexible client state management  
- **TanStack Query** — server state fetching and caching

### 2. Data Fetching & API
- **TanStack Query** — async data fetching, caching, and sync

### 3. Forms & Validation
- **Zod** — TypeScript-first schema validation

### 4. Styling & UI Components
- **Tailwind CSS** — utility-first CSS framework  
- **shadcn/ui** — headless UI components built with Tailwind

### 5. Authentication & Security
- **Firebase Auth** — authentication with identity providers

### 6. Testing
- **Vitest** — Vite-native unit/integration testing  
- **Testing Library** (React Testing Library) — DOM testing utilities  
- **Playwright** — modern E2E testing framework  
- **MSW** (Mock Service Worker) — API mocking for tests

### 7. Storybook & Design Systems
- **Storybook** — isolated UI development and documentation

### 8. Performance & Monitoring
- **Lighthouse** — performance monitoring and analysis in Chrome

### 9. Deployment & CI/CD
- **Vercel** — official Next.js hosting

### 10. Developer Experience
- **Biome** — code linter and formatter  
- **pnpm** — fast, disk space-efficient package manager

### 11. Local Development & Testing Environment
- **Docker** — containerized development environment  
- **Docker Compose** — multi-container orchestration for local setup and testing


## Out of Scope

These guidelines do **not** cover:

- Backend service development (covered in separate backend guidelines)  
- Non-Next.js frontend frameworks  
- Project management and workflow conventions (e.g., Git branching)  


By following these guidelines, we aim to keep our frontend codebase **clean, predictable, and scalable**, making it easier for both humans and AI tools to contribute effectively.
