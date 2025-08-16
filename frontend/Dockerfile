# syntax=docker/dockerfile:1

# Base stage with dependencies
FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Enable corepack and install pnpm
RUN corepack enable

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies only
RUN pnpm install --frozen-lockfile --prod=false

# Development stage
FROM node:20-alpine AS dev
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Enable corepack
RUN corepack enable

# Copy installed dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/pnpm-lock.yaml ./pnpm-lock.yaml

# Copy source code
COPY . .

# Expose ports
EXPOSE 3000 6006

# Default command for development
CMD ["pnpm", "dev"]
