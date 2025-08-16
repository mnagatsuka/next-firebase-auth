# 2. Project Setup

This section describes how to initialize and configure a **Next.js + TypeScript** project using the **App Router** and **React Server Components (RSC)** with our standard tooling and libraries.

It covers **project initialization**, **TypeScript configuration**, **code quality tools**, **Next.js settings**, **Docker setup**, and **environment variable management** to ensure consistency across all development environments.


## 1. Project Initialization

We use **pnpm** as the package manager for its speed, disk efficiency, and workspace capabilities.

```bash
# Create a new Next.js project
pnpm create next-app@latest my-app \
  --typescript \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"

cd my-app
````

**Rules:**

* Always use `pnpm` (`pnpm install`, `pnpm add`, `pnpm remove`) — do **not** use `npm` or `yarn`.
* Use `--save-exact` (`-E`) when installing runtime dependencies unless a version range is intentional.


## 2. TypeScript Configuration

We enforce **strict typing** for safety and maintainability.

Example `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

**Rules:**

* `strict` mode must remain enabled.
* Explicitly type **props, function parameters, and return values**.
* Avoid `any` unless strictly necessary and documented.


## 3. Code Linter & Formatter (Biome)

We use **[Biome](https://biomejs.dev/)** as a unified linter and formatter.

Install Biome:

```bash
pnpm add -D @biomejs/biome
```

Example `biome.json`:

```json
{
  "$schema": "https://biomejs.dev/schemas/1.0.0/schema.json",
  "formatter": {
    "enabled": true,
    "lineWidth": 100
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true
    }
  }
}
```

**Rules:**

* Run `pnpm biome check .` before committing.
* Use `pre-commit` hooks to automatically format and lint staged files.


## 4. Next.js Configuration

We use a **typed** `next.config.ts`:

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    serverActions: true
  }
}

export default nextConfig
```

**Rules:**

* Keep `reactStrictMode: true` for development.
* Document non-default config values with comments.


## 5. Docker & Docker Compose for Local Development

We use **Docker** and **Docker Compose** to standardize local development and testing environments.

Example `Dockerfile`:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY pnpm-lock.yaml package.json ./
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install

COPY . .

EXPOSE 3000
CMD ["pnpm", "dev"]
```

Example `docker-compose.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - '3000:3000'
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      NODE_ENV: development
```

**Rules:**

* Use Docker volumes for live reload in development.
* Install dependencies inside the container to ensure consistency.


## 6. Environment Variables

Follow the Next.js convention:

* `.env.local` — Local development (not committed)
* `.env.test` — Testing environment
* `.env.production` — Production environment

**Rules:**

* Do **not** commit `.env.local` or secrets.
* Document all required variables in `docs/env.md`.
* Use `process.env.MY_VAR` with explicit typing.


By following this setup, all developers and CI/CD pipelines share the **same baseline configuration**, ensuring consistent and predictable behavior across environments.
