This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Running Storybook

To run Storybook using Docker Compose, follow these steps:

1.  **Ensure Docker is running:**
    Make sure Docker Desktop or your Docker daemon is running on your system.

2.  **Start the Storybook service:**
    Navigate to the `frontend` directory and run the following command:
    ```bash
    docker compose up storybook -d
    ```
    This will build the Storybook image (if not already built) and start the Storybook container.

    Storybook will be accessible at [http://localhost:6006](http://localhost:6006).

3.  **Stop the Storybook service:**
    To stop the Storybook container, press `Ctrl+C` in the terminal where `docker compose up` is running.
    Alternatively, you can run:
    ```bash
    docker compose down storybook
    ```

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
