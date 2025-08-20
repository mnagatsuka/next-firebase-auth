# Implementation Verfication Check List

I have summarized the test perspectives for the Firebase Auth implementation as follows.
At each milestone in the implementation, please review these test perspectives to ensure that the implementation approach is aligned.
The condition for implementation completion is that all test perspectives are ultimately passed.

## 1. Authentication / Cookie Related

1. When accessing as an anonymous user, `signInAnonymously` is executed and a session cookie is successfully issued.
2. During anonymous login, `verifySessionCookie()` correctly authenticates the user in Middleware.
3. The UID obtained during anonymous login is preserved even after page navigation (session cookie validity is maintained).
4. After a normal login, the UID remains the same as the anonymous login, and `isAnonymous` is changed to `false`.
5. When accessing with an expired session cookie, anonymous users are automatically re-logged in.
6. When accessing with an expired session cookie as a normal user, the user is redirected to the login page.
7. Immediately after normal login, a new session cookie is issued (with a 14-day expiration).
8. During logout, the session cookie is deleted and the token stored in Zustand is reset.
9. The contents of the session cookie cannot be viewed or modified from the client side.

## 2. Middleware / Routing Related

1. Middleware verifies the validity of the cookie and controls routing accordingly.
2. If the cookie is invalid or does not exist, the user is properly redirected to either anonymous login or the login page.
3. The anonymous login flow via `/api/login/anonymous` is directed by Middleware.
4. When accessing an SSR page that requires authentication without a cookie, the user is prompted to log in or perform an anonymous login.

## 3. CSR / SSR & API Request Related

1. CSR pages are rendered as CSR and can correctly fetch and display the necessary data (CSR/SSR rendering switch).
2. SSR pages are rendered as SSR and can correctly fetch and display the necessary data (CSR/SSR rendering switch).
3. In CSR, the ID token stored in Zustand is included in the Authorization header.
4. When the token expires in CSR, the API returns 401/403, triggering re-login flow (anonymous or normal).
5. In SSR, the session cookie is properly read and the token is verified using the Firebase Admin SDK.
6. When token verification fails in SSR, an error page or anonymous login process is executed.
7. During SSR API requests, the ID token obtained from the session cookie is added to the Authorization header.

## 4. Upgrade (Anonymous → Normal Login)

1. Users can upgrade from an anonymous login state to a normal login (e.g., Google).
2. When upgrading, `linkWithCredential()` is used, and the UID remains unchanged.
3. After upgrading, data from the anonymous user period is inherited as-is.

## 5. Data Persistence Related

1. Data is stored and displayed based on the anonymous user’s UID.
2. After upgrading, past data is preserved as-is.
3. Data for normal logged-in users is stored and displayed based on their UID.
4. Data is preserved across CSR page navigations (either via Zustand persistence or API re-fetch).
