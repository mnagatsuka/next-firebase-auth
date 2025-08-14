FROM node:20-alpine

WORKDIR /app

COPY pnpm-lock.yml package.json ./
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install

COPY . .

EXPOSE 3000
CMD ["pnpm", "dev"]