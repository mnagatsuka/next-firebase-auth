# 18. Deployment on Vercel

This section outlines the rules and best practices for deploying our **Next.js + TypeScript** applications to **Vercel**, including environment management, build settings, and troubleshooting.

Our goals are:
- Keep deployments **predictable and reproducible**
- Maintain clear separation between environments (preview, staging, production)
- Ensure environment variables are correctly managed and secured
- Optimize build and runtime performance on Vercel


## 1. Connecting the Repository

1. Sign in to [Vercel](https://vercel.com) using your GitHub, GitLab, or Bitbucket account.
2. Import the repository containing your Next.js project.
3. Choose the correct root directory. For this project, the root directory for the frontend is `frontend`.
4. Select the **framework preset** for Next.js — Vercel will auto-detect most settings.


## 2. Environment Variables Management

Environment variables for deployments are managed directly in the **Vercel Project Settings > Environment Variables**.

For local development that mirrors a Vercel environment, you can pull variables from Vercel into local `.env` files using the Vercel CLI. This project's convention is:
- `.env.development`: For local development, matching the `Development` environment on Vercel.
- `.env.staging`: For simulating the `Preview` environment locally.
- `.env.production`: For simulating the `Production` environment locally.

**Rules:**
- Never commit `.env.*` files to the repository, except for `frontend/.env.example`.
- Use Vercel’s **Environment** field to scope variables to `Production`, `Preview`, and `Development`.
- Server-side secrets (like `FIREBASE_PRIVATE_KEY`) must **only** be set in Vercel and never exposed in client-side code.

See the **Manual Deployments** section for instructions on pulling these variables with `vercel env pull`.

### Required Variables

The following variables from `frontend/.env.example` must be configured in Vercel for deployment:

#### Firebase Client SDK (Client-side)
These variables are prefixed with `NEXT_PUBLIC_` and are safe for the browser.

| Name                                  | Environment | Description                               |
| ------------------------------------- | ----------- | ----------------------------------------- |
| `NEXT_PUBLIC_FIREBASE_API_KEY`        | All         | Firebase project API key.                 |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`    | All         | Firebase project auth domain.             |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID`     | All         | Firebase project ID.                      |
| `NEXT_PUBLIC_FIREBASE_APP_ID`         | All         | Firebase app ID.                          |
| (Optional) `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | All | Firebase storage bucket. Use only if needed. |
| (Optional) `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | All | Firebase messaging sender ID. Use only if needed. |

#### API & WebSocket Endpoints (Client-side)

| Name                        | Environment | Example Value (Production)                               |
| --------------------------- | ----------- | -------------------------------------------------------- |
| `NEXT_PUBLIC_API_BASE_URL`  | All         | `https://your-backend-api.com`                           |
| `NEXT_PUBLIC_WEBSOCKET_URL` | All         | `wss://your-websocket-api.com`                           |

#### Firebase Admin SDK (Server-side)
These are used for server-side rendering (SSR) and API routes. **They must not be prefixed with `NEXT_PUBLIC_`**.

| Name                    | Environment      | Description                                       |
| ----------------------- | ---------------- | ------------------------------------------------- |
| `FIREBASE_PROJECT_ID`   | Production, Preview | Your Firebase project ID.                         |
| `FIREBASE_CLIENT_EMAIL` | Production, Preview | Service account email from Firebase.              |
| `FIREBASE_PRIVATE_KEY`  | Production, Preview | Service account private key from Firebase.        |
| `API_BASE_URL`          | Production, Preview | Internal URL for server-to-server API calls.      |
| `FIREBASE_API_KEY`      | Production, Preview | Firebase project API key (for server-side auth).  |


## 3. Build Settings and Output Configuration

Vercel automatically detects Next.js and `pnpm`, applying the following default settings. Ensure they match your project settings in Vercel.

- **Framework Preset**: Next.js
- **Build Command**:
  ```bash
  pnpm build
  ```
- **Output Directory**: `.next` (within the `frontend` root directory)
- **Install Command**:
  ```bash
  pnpm install --frozen-lockfile
  ```

> Our project uses `pnpm` as the standard package manager. Vercel will use it automatically because of the `pnpm-lock.yaml` file.


## 4. Preview, Staging, and Production Environments

* **Preview Deployments**:

  * Triggered by pull requests or commits to non-production branches.
  * Use environment variables scoped to **Preview** in Vercel.
  * For QA, design reviews, and stakeholder demos.

* **Production Deployments**:

  * Triggered by merges to the main branch.
  * Uses environment variables scoped to **Production** in Vercel.
  * Only deploy when the main branch is stable and tested.

* **Staging (optional)**:

  * Can be simulated by creating a dedicated branch and mapping it to a custom domain.
  * Useful for pre-production testing.


## 5. Vercel Analytics and Monitoring

* Enable **Vercel Analytics** in the project settings for real-user performance metrics.
* Monitor:

  * Core Web Vitals
  * Page load times
  * Rendering performance

> For more detailed frontend performance tracking, combine with **Lighthouse** audits in CI.


## 6. Common Pitfalls and Troubleshooting

**Problem:** Environment variables not updating
**Solution:** Redeploy after updating environment variables in Vercel; ensure the correct environment scope.

**Problem:** Build fails due to missing dependencies
**Solution:** Check `pnpm-lock.yaml` is committed; run `pnpm install --frozen-lockfile` locally before pushing.

**Problem:** Functions not running as expected
**Solution:** Check the **Runtime Logs** in Vercel dashboard; ensure server actions and API routes are compatible with the target runtime (Edge or Node).

**Problem:** `.env.development` is being used in production
**Solution:** Verify environment variable setup in Vercel; local `.env` files are not used in Vercel's build environment.


## 7. Security Best Practices

* **Secrets Management**: Do not expose secret keys in `NEXT_PUBLIC_*` variables. Server-side keys like `FIREBASE_PRIVATE_KEY` must only be set in Vercel's environment variables for Production and Preview environments.
* **Credential Rotation**: Rotate service account keys periodically and update them in Vercel settings.
* **Security Headers**: The application includes important security headers via `frontend/next.config.ts`. These include `Strict-Transport-Security` (in production), `X-Content-Type-Options`, and `X-Frame-Options`.
* **Content Security Policy (CSP)**: A strict CSP is enforced in production and staging via `frontend/middleware.ts`. It is configured using the `NEXT_PUBLIC_API_BASE_URL` and `API_BASE_URL` environment variables to allow connections to our backend services.
> Tip: On Vercel Preview, set `NODE_ENV=staging` to enable CSP for preview builds.


By following these deployment guidelines, we ensure our Next.js applications run **securely, efficiently, and predictably** across all environments on Vercel.

## 8. Manual Deployments with Vercel CLI

While the primary deployment method is through Git integration, the [Vercel CLI](https://vercel.com/docs/cli) is useful for manual deployments and managing environment variables locally.

### Step 1: Install Vercel CLI

It is recommended to install the Vercel CLI as a local development dependency to ensure version consistency across the team.

```bash
# From the frontend directory
pnpm add -D vercel
```

After installation, you will run commands with `pnpm vercel ...`.

(Alternatively, for global access across all projects, you can install it with `pnpm add -g vercel` and run commands directly with `vercel ...`.)

### Step 2: Link Project to Vercel

Before deploying from the CLI, you must link your local `frontend` directory to the corresponding Vercel project.

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Run the link command:
    ```bash
    pnpm vercel link
    ```
3.  Follow the interactive prompts to connect to your Vercel account and select the correct project.

### Step 3: Pull Environment Variables

To sync environment variables from Vercel to your local machine for testing or development, use the `env pull` command. This project uses the following convention:

- **For local development:**
  ```bash
  # Pulls from the "Development" environment in Vercel
  pnpm vercel env pull .env.development
  ```
- **To test the Preview/Staging environment locally:**
  ```bash
  # Pulls from the "Preview" environment in Vercel
  pnpm vercel env pull .env.staging --environment=preview
  ```
- **To test the Production environment locally:**
  ```bash
  # Pulls from the "Production" environment in Vercel
  pnpm vercel env pull .env.production --environment=production
  ```

### Step 4: Deploy Manually

Once the project is linked, you can deploy from the `frontend` directory.

*   **To create a Preview Deployment:**
    ```bash
    pnpm vercel
    ```
    This will create a new preview deployment with a unique URL.

*   **To create a Production Deployment:**
    > **Warning:** This command deploys directly to your production domain. Use it with caution.
    ```bash
    pnpm vercel --prod
    ```
