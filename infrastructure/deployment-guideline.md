# Frontend Deployment on Vercel (Next.js App)

This guide explains how to deploy the frontend (Next.js, App Router) to Vercel for Development, Preview, and Production, tailored to this repository.

- Frontend root: `frontend`
- Package manager: `pnpm`
- Backend REST endpoint: Lambda Function URL (CORS Pattern A: `*` origins, no credentials)
- WebSocket endpoint: API Gateway WebSocket URL

## Prerequisites
- Vercel account with access to your Git repository
- Backend deployed via SAM (so you can copy outputs):
  - `FunctionUrlEndpoint` (REST)
  - `WebSocketURL` (WebSocket)

Get outputs (example for `blogapp-development`):
```bash
aws cloudformation describe-stacks --stack-name blogapp-development \
  --query 'Stacks[0].Outputs' --output table
```

## Project Import (Vercel)
1. Import the repository in Vercel.
2. Set Project Root to `frontend`.
3. Framework Preset: Next.js (auto-detected).
4. Build settings (auto):
   - Install Command: `pnpm install --frozen-lockfile`
   - Build Command: `pnpm build`
   - Output Directory: `.next`

## Environment Variables (Vercel)
Configure these in Vercel Project Settings → Environment Variables. Scope each to Development / Preview / Production as appropriate.

### Client-side (NEXT_PUBLIC_*)
These are exposed to the browser.
- `NEXT_PUBLIC_FIREBASE_API_KEY` — Firebase Web API key
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` — Firebase auth domain
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID` — Firebase project ID
- `NEXT_PUBLIC_FIREBASE_APP_ID` — Firebase web app ID
- `NEXT_PUBLIC_API_BASE_URL` — Browser base URL for REST API
  - Set to `FunctionUrlEndpoint` from SAM outputs
- `NEXT_PUBLIC_WEBSOCKET_URL` — WebSocket URL
  - Set to `WebSocketURL` from SAM outputs (e.g., `wss://.../development`)

Optional:
- `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
- `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID`

### Server-side (not exposed to browser)
Used by SSR/server actions and middleware.
- `API_BASE_URL` — Server base URL for REST API
  - Set to `FunctionUrlEndpoint` (same as browser)  
    Note: Our middleware/CSP uses this to build `connect-src`.
- `FIREBASE_PROJECT_ID` — Service account project ID
- `FIREBASE_CLIENT_EMAIL` — Service account client email
- `FIREBASE_PRIVATE_KEY` — Service account private key (keep newlines; use `\n` if needed)
- `FIREBASE_API_KEY` — Same Web API key (used by server-side Firebase auth flows)

Development-only (do NOT set on Vercel production/preview):
- `FIREBASE_AUTH_EMULATOR_HOST`

### Why no origin allowlists?
The backend REST uses a Lambda Function URL configured with CORS Pattern A (`AllowOrigins: "*"`, `AllowCredentials: false`), so you do not need to add every Vercel preview URL after each deployment.

## Deployments
- Production: triggered by merges to your production branch (according to your Vercel settings).
- Preview: created automatically for pull requests and non-prod branches.
- Development: you can manually deploy or use the Vercel CLI locally.

### Manual Deployments (CLI)
From the `frontend` directory:
```bash
# Optional: install CLI locally to pin versions
pnpm add -D vercel

# Link local folder to Vercel project
pnpm vercel link

# Pull env vars to local files
pnpm vercel env pull .env.development
pnpm vercel env pull .env.staging --environment=preview
pnpm vercel env pull .env.production --environment=production

# Create a preview deployment
pnpm vercel

# Create a production deployment (use with caution)
pnpm vercel --prod
```

## Post-Deployment Checks
- Open your Vercel URL and verify pages load.
- Confirm API calls use `NEXT_PUBLIC_API_BASE_URL` and succeed (Function URL).
- Confirm WebSocket connects to `NEXT_PUBLIC_WEBSOCKET_URL`.
- In production and staging, our middleware applies CSP. Ensure `NEXT_PUBLIC_API_BASE_URL` and `API_BASE_URL` are set so `connect-src` allows your endpoints.

Tip: For Vercel Preview deployments, set `NODE_ENV=staging` in Project Settings → Environment Variables so CSP is applied in preview builds.

## Troubleshooting
- Missing env vars: ensure they’re set in the correct Vercel environment scope (Development/Preview/Production) and redeploy.
- 401/403 from API: verify Firebase client keys and server `FIREBASE_*` are correct; the backend expects `Authorization: Bearer <token>`.
- CORS errors: the Function URL provides permissive CORS (Pattern A). If errors persist, ensure you’re calling the Function URL (not an old API Gateway URL), and that requests include required headers.

## References
- docs/coding-guidelines/frontend/18_vercel-deployment.md (general guidance)
- DEPLOYMENT.md (backend SAM deployment & outputs)
- frontend/.env.example (variable list and examples)
