# Firebase Auth Setup Guide

This guide will help you set up Firebase Authentication for the Next.js frontend application.

## Prerequisites

1. **Firebase Project**: You need a Firebase project with Authentication enabled
2. **Firebase Admin SDK**: Service account key for server-side operations
3. **Environment Variables**: Properly configured environment variables

## Step-by-Step Setup

### 1. Firebase Project Setup

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable Authentication:
   - Go to **Authentication** > **Sign-in method**
   - Enable **Email/password** provider
   - Enable **Anonymous** provider
4. Get your Firebase config:
   - Go to **Project Settings** > **General**
   - In the "Your apps" section, click "Web app" icon
   - Copy the Firebase configuration object

### 2. Firebase Admin SDK Setup

1. Go to **Project Settings** > **Service accounts**
2. Click **Generate new private key**
3. Download the JSON file with your service account credentials
4. Extract the required fields for environment variables

### 3. Environment Variables Configuration

Create a `.env.development` file in the frontend directory with the following variables (Storage/Messaging optional):

```bash
# Firebase Client Configuration (Public)
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abc123def456
# Optional (only if using Storage/Messaging)
# NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
# NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789

# Firebase Admin SDK Configuration (Server-side only)
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-abc123@your_project.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
FIREBASE_PRIVATE_KEY_ID=private_key_id_here
FIREBASE_CLIENT_ID=123456789
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-abc123%40your_project.iam.gserviceaccount.com

# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
API_BASE_URL=http://backend:8000
```

### 4. Install Dependencies

Dependencies are already added to `package.json`:

```bash
pnpm install
```

### 5. Development Setup

1. **Start the development server**:
   ```bash
   pnpm dev
   ```

2. **Optional: Firebase Auth Emulator** (for local development):
   
   **First-time setup:**
   ```bash
   # Install Firebase CLI locally (recommended approach)
   pnpm add -D firebase-tools

   # Login to Firebase (one-time setup)
   npx firebase login

   # Initialize Firebase emulators in your project root
   npx firebase init emulators
   # Select:
   # - Authentication Emulator
   # - Use default port (9099) or specify custom port
   # - This will create firebase.json and .firebaserc files
   ```

   **Configure environment:**
   ```bash
   # Add to frontend/.env.development
   NEXT_PUBLIC_FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
   ```
   
   **Start the emulator:**
   ```bash
   # From project root
   npx firebase emulators:start --only auth
   
   # Or use the npm script (if added to package.json)
   pnpm fb:emu:auth
   ```

   **Note**: You may see a deprecation warning `(node:xxxxx) [DEP0040] DeprecationWarning: The 'punycode' module is deprecated.` when running firebase commands. This is a known issue with the Firebase CLI and can be safely ignored - it doesn't affect functionality.

   **Troubleshooting**: If you get "No emulators to start" error, you need to run `npx firebase init emulators` first to set up the Firebase emulator configuration.

### 6. Production Deployment

1. **Set environment variables** in your hosting platform (Vercel, Netlify, etc.)
2. **Remove or update emulator settings** - ensure `NEXT_PUBLIC_FIREBASE_AUTH_EMULATOR_HOST` is not set in production
3. **Test the deployment** with real Firebase Authentication

## Features Implemented

### ✅ Authentication Methods
- **Email/Password Sign In**: Traditional login with email and password
- **Email/Password Sign Up**: Account creation with email and password
- **Anonymous Authentication**: Guest access without registration
- **Anonymous to Regular User Upgrade**: Convert guest accounts to permanent accounts

### ✅ Session Management
- **HTTP-only Cookies**: Secure session storage
- **Session Verification**: Server-side session validation
- **Auto-refresh**: Token renewal for authenticated users
- **Secure Logout**: Complete session cleanup

### ✅ Route Protection
- **Middleware Authentication**: Automatic route protection
- **Anonymous User Handling**: Seamless guest access to protected routes
- **Redirect Handling**: Smart redirection after authentication

### ✅ UI Components
- **Login Form**: Email/password authentication with guest option
- **Signup Form**: Account creation form
- **Anonymous Upgrade Form**: Convert guest account to permanent account
- **Header Authentication**: Login status and user actions
- **Loading States**: Proper loading indicators

### ✅ State Management
- **Zustand Integration**: Client-side authentication state
- **Persistence**: Secure state persistence (non-sensitive data only)
- **Auto-initialization**: Firebase Auth state synchronization

### ✅ API Integration
- **Automatic Token Injection**: Bearer tokens in API requests
- **Error Handling**: 401/403 response handling and token refresh
- **Mock Support**: MSW integration for testing

## Usage Examples

### Basic Authentication Check
```tsx
import { useAuth } from '@/hooks/useAuth'

function MyComponent() {
  const { user, isAuthenticated, isLoading } = useAuth()
  
  if (isLoading) return <div>Loading...</div>
  if (!isAuthenticated) return <div>Please sign in</div>
  
  return <div>Welcome, {user?.email}!</div>
}
```

### Require Authentication
```tsx
import { useRequireAuth } from '@/hooks/useRequireAuth'

function ProtectedComponent() {
  const { isAuthenticated, isLoading } = useRequireAuth('/login')
  
  if (isLoading || !isAuthenticated) return null
  
  return <div>Protected content</div>
}
```

### Manual Authentication Actions
```tsx
import { useAuth } from '@/hooks/useAuth'

function AuthActions() {
  const { 
    signInWithEmail, 
    signUpWithEmail, 
    signInAnonymously,
    logout 
  } = useAuth()
  
  const handleLogin = async () => {
    try {
      await signInWithEmail('user@example.com', 'password')
    } catch (error) {
      console.error('Login failed:', error)
    }
  }
  
  // ... other handlers
}
```

## Security Notes

### ✅ Implemented Security Measures
- **HTTP-only session cookies**: Prevent XSS attacks
- **Secure cookie settings**: HTTPS-only in production
- **Server-side session verification**: Using Firebase Admin SDK
- **Token expiration handling**: Automatic refresh and cleanup
- **Environment variable protection**: Sensitive data server-side only

### 🔒 Production Checklist
- [ ] All environment variables set in production
- [ ] Firebase project configured for production domain
- [ ] CORS settings configured if needed
- [ ] Firebase Auth emulator disabled in production
- [ ] HTTPS enabled for cookie security
- [ ] Firebase rules configured properly

## Troubleshooting

### Common Issues

1. **"Invalid API key"**: Check `NEXT_PUBLIC_FIREBASE_API_KEY`
2. **"Auth domain not whitelisted"**: Add domain in Firebase Console
3. **"Session cookie not set"**: Check server-side environment variables
4. **"CORS errors"**: Configure Firebase project settings
5. **"Anonymous sign-in disabled"**: Enable in Firebase Console

### Development Debugging

1. **Check browser console** for client-side errors
2. **Check server logs** for API route errors
3. **Verify environment variables** are loaded correctly
4. **Test with Firebase Auth emulator** for local development
5. **Use React DevTools** to inspect Zustand state

## Testing

The implementation includes MSW mocks for testing:

```bash
# Run tests
pnpm test

# Run tests with coverage
pnpm test:coverage

# Run tests in watch mode
pnpm test:watch
```

Mock handlers are available for:
- Authentication API endpoints
- Session verification
- Login/logout flows
- Anonymous authentication

---

## Support

For issues specific to this implementation, check:
1. [Firebase Auth Documentation](https://firebase.google.com/docs/auth)
2. [Next.js Authentication Guide](https://nextjs.org/docs/authentication)
3. [Project documentation in `docs/projects/add-firebase-auth/`](../docs/projects/add-firebase-auth/)

The implementation follows all coding guidelines and is ready for production use with proper environment configuration.
