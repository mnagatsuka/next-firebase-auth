# syntax=docker/dockerfile:1

FROM node:20-alpine

WORKDIR /app

# Install pnpm globally and dependencies
RUN corepack enable && apk add --no-cache libc6-compat

# Copy package files and tsconfig.base.json  
COPY frontend/package.json frontend/pnpm-lock.yaml ./
COPY tsconfig.base.json ../

# Install dependencies with correct architecture
RUN pnpm install --frozen-lockfile --prod=false

# Copy source code only (avoid copying node_modules)
COPY frontend/src ./src
COPY frontend/public ./public  
COPY frontend/*.json frontend/*.js frontend/*.mjs frontend/*.ts frontend/*.md ./

# Expose ports for development and Storybook
EXPOSE 3000 6006

# Start development server
CMD ["pnpm", "dev"]