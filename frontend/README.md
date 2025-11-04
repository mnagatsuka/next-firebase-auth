This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Directory Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js App Router pages
│   │   ├── api/             # API routes
│   │   │   └── auth/        # Authentication endpoints
│   │   ├── auth/            # Auth-related pages
│   │   ├── create-post/     # Post creation page
│   │   ├── my/              # User dashboard pages
│   │   │   ├── favorites/   # User favorites page
│   │   │   └── posts/       # User posts page
│   │   └── posts/           # Blog post pages
│   │       └── [id]/        # Dynamic post pages
│   ├── components/          # React components
│   │   ├── auth/            # Authentication components
│   │   ├── blog/            # Blog-related components
│   │   ├── common/          # Shared utility components
│   │   ├── layout/          # Layout components (Header, Footer)
│   │   └── ui/              # shadcn/ui components
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utility libraries
│   │   ├── api/             # API client and generated types
│   │   ├── auth/            # Authentication utilities
│   │   ├── config/          # Configuration
│   │   ├── firebase/        # Firebase client setup
│   │   ├── providers/       # React context providers
│   │   └── utils/           # General utilities
│   ├── mocks/               # MSW mock handlers
│   ├── stores/              # Zustand stores
│   └── types/               # TypeScript type definitions
├── tests/                   # Test files
│   ├── factories/           # Test data factories
│   ├── integration/         # Integration tests
│   ├── scenarios/           # Test scenarios
│   ├── unit/                # Unit tests
│   └── utils/               # Test utilities
└── public/                  # Static assets
```

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

## Building with Docker Compose

To build the Docker images for both the application and Storybook, run the following command from the `frontend` directory:

```bash
docker compose build
```

This command builds the necessary images without starting the containers.

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

## Environment Variables (Staging / Vercel)

Set server vs client variables appropriately:

- Server (Vercel Project Settings → Environment Variables):
  - `API_BASE_URL` — HTTPS API URL (SAM output `ApiUrl`) (Required: all env).
  - `FIREBASE_PROJECT_ID` — Firebase project ID (Required: all env).
  - `FIREBASE_CLIENT_EMAIL` — Service account email. (Required: staging, production)
  - `FIREBASE_PRIVATE_KEY` — Service account private key (paste multiline or use `\n`) (Required: staging, production).
  - `FIREBASE_API_KEY` — Web API key used by server (Identity Toolkit custom-token exchange) (Required: staging, production).
  - Do NOT set `FIREBASE_AUTH_EMULATOR_HOST` on Vercel (Required: developemt).

- Client (in repo `.env.staging`/`.env.production`):
  - `NEXT_PUBLIC_FIREBASE_API_KEY` - Web API key used by server. Same value as Server (Required: all env)
  - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` - (Required: all env)
  - `NEXT_PUBLIC_FIREBASE_PROJECT_ID` - (Required: all env)
  - `NEXT_PUBLIC_FIREBASE_APP_ID` - (Required: all env)
  - `NEXT_PUBLIC_API_BASE_URL` — Same base URL as `API_BASE_URL` for browser (Required: all env).
  - Optional: `NEXT_PUBLIC_WEBSOCKET_URL` — WebSocket URL (SAM output `WebSocketURL`) (Required: all env).
  - Optional (if using Storage/Messaging): `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`, `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`

Notes
- The app validates server env via `src/lib/config/env.ts` and uses it in server-only modules.
- For manual staging, either:
  - `cp .env.staging .env.production` before build, or
  - `set -a; source .env.staging; set +a` in the same shell for both build and start.

## Firebase Env Values — How To Obtain

Use a dedicated Firebase project for staging. You’ll need values for both the client SDK (`NEXT_PUBLIC_*`) and the server (Admin SDK + Identity Toolkit).

Client (NEXT_PUBLIC_*)
- Where to find (Firebase Console):
  - Project settings → General → Your apps → Web app → “Config” snippet
- Map config → env:
  - `apiKey` → `NEXT_PUBLIC_FIREBASE_API_KEY`
  - `authDomain` → `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
  - `projectId` → `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
  - `appId` → `NEXT_PUBLIC_FIREBASE_APP_ID`
  - Optional: `storageBucket` → `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
  - Optional: `messagingSenderId` → `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
  - Optional: `measurementId` → `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID`

Server (non-prefixed)
- Service account (Admin SDK credentials):
  - Firebase Console → Project settings → Service accounts → Firebase Admin SDK → “Generate new private key” (downloads JSON)
  - Map JSON → env:
    - `project_id` → `FIREBASE_PROJECT_ID`
    - `client_email` → `FIREBASE_CLIENT_EMAIL`
    - `private_key` → `FIREBASE_PRIVATE_KEY` (keep newlines; if needed, replace with `\n`)
  - Optional (not required by our Next server): `private_key_id`, `client_id`, etc.
- Identity Toolkit Web API Key (server-side custom-token exchange):
  - Use the same `apiKey` as the client web app → set `FIREBASE_API_KEY` (note: not a secret by itself).
- Auth emulator (local dev only):
  - `FIREBASE_AUTH_EMULATOR_HOST=127.0.0.1:9099` — do not set on Vercel.

Tips
- Ensure your staging domain is in Authentication → Settings → Authorized domains.
- Storage bucket: shown in Project settings → General or Build → Storage; also embedded in the web app config.
- Quick extraction from service account JSON:
  ```bash
  jq -r '.project_id, .client_email, .private_key' service-account.json
  ```

Where to set
- Vercel (Server): `API_BASE_URL`, `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`, `FIREBASE_API_KEY`.
- Repo env files (Client): set `NEXT_PUBLIC_*` in `.env.staging`/`.env.production`.
 
### Variables and Examples
 
- Client (`NEXT_PUBLIC_*`):
  - `NEXT_PUBLIC_FIREBASE_API_KEY`: Firebase Web API key. Example: `AIzaSyD3mo-ExampleKey1234`
  - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`: Firebase Auth domain. Example: `your-project.firebaseapp.com`
  - `NEXT_PUBLIC_FIREBASE_PROJECT_ID`: Firebase project ID. Example: `your-project`
  - `NEXT_PUBLIC_FIREBASE_APP_ID`: Firebase web app ID. Example: `1:1234567890:web:abc123def456`
  - `NEXT_PUBLIC_API_BASE_URL`: Browser base URL for API. Example: `https://abc123.execute-api.ap-northeast-1.amazonaws.com`
  - Optional `NEXT_PUBLIC_WEBSOCKET_URL`: WebSocket URL. Example: `wss://xyz987.execute-api.ap-northeast-1.amazonaws.com/staging`
  - Optional (if using other features): `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`, `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
 
- Server (non-prefixed):
  - `API_BASE_URL`: Server base URL for API fetches. Example: `https://abc123.execute-api.ap-northeast-1.amazonaws.com`
  - `FIREBASE_PROJECT_ID`: Service account project ID. Example: `your-project`
  - `FIREBASE_CLIENT_EMAIL`: Service account client email. Example: `firebase-adminsdk-xyz@your-project.iam.gserviceaccount.com`
  - `FIREBASE_PRIVATE_KEY`: Service account private key (keep newlines). Example: `-----BEGIN PRIVATE KEY-----\nMIIEv...\n-----END PRIVATE KEY-----\n`
  - `FIREBASE_API_KEY`: Same Web API key (server-side Identity Toolkit). Example: `AIzaSyD3mo-ExampleKey1234`
  - Local only `FIREBASE_AUTH_EMULATOR_HOST`: Auth emulator host. Example: `127.0.0.1:9099`
