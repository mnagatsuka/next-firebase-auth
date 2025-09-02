## Auth Specifications

- [Firebase Auth Setup](./firebase-auth-setup.md)
- [Firebase Auth Frontend](./firebase-auth-frontend.md)
- [Firebase Auth Backend](./firebase-auth-backend.md)
- [Next + Firebase Auth Flow](./next-firebase-auth-flow.md)
- [Session Guard Pattern](./session-guard-pattern.md) — Final recommendation: guard SSR-only pages with `getServerUser()` and silently reissue `__session` on 401 via client ID token + `/api/auth/login`; avoid global ensure-session.
- [Verification Check List](./verification-check-list.md)
