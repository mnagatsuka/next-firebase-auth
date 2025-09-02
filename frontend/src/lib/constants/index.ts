// (Removed) ROUTES: page route helpers are no longer exported; use literal paths where needed.

// API endpoints
export const API_ENDPOINTS = {
	AUTH: {
		LOGIN: "/api/auth/login",
		LOGOUT: "/api/auth/logout",
		SESSION: "/api/auth/session",
		ANONYMOUS: "/api/auth/anonymous",
	},
	POSTS: {
		LIST: "/posts",
		DETAIL: (id: string) => `/posts/${id}`,
		CREATE: "/posts",
		COMMENTS: (id: string) => `/posts/${id}/comments`,
	},
} as const;

// Auth related constants
export const AUTH_CONSTANTS = {
	ANONYMOUS_AUTO_SIGNIN_EXCLUDED_PATHS: [],
} as const;

// (Removed) UI_CONSTANTS and VALIDATION: unused; keep styles inline with Tailwind and validate close to forms.
