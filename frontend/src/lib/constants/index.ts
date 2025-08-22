// Route constants
export const ROUTES = {
	HOME: "/",
	LOGIN: "/login",
	SIGNUP: "/signup",
	CREATE_POST: "/create-post",
	POST_DETAIL: (id: string) => `/posts/${id}`,
	PROFILE: "/profile",
	AUTH_ANONYMOUS: "/auth/anonymous",
} as const;

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
	COOKIE_NAME: "session",
	TOKEN_REFRESH_THRESHOLD: 5 * 60 * 1000, // 5 minutes in milliseconds
	ANONYMOUS_AUTO_SIGNIN_EXCLUDED_PATHS: ["/login", "/signup"],
} as const;

// UI constants
export const UI_CONSTANTS = {
	PAGINATION: {
		DEFAULT_PAGE_SIZE: 10,
		MAX_PAGE_SIZE: 50,
	},
	TIMEOUTS: {
		API_REQUEST: 10000,
		TOAST_DURATION: 4000,
	},
	ANIMATION: {
		PAGE_TRANSITION_DURATION: 300,
	},
} as const;

// Validation constants
export const VALIDATION = {
	PASSWORD: {
		MIN_LENGTH: 8,
		MAX_LENGTH: 128,
	},
	EMAIL: {
		MAX_LENGTH: 254,
	},
	POST: {
		TITLE_MAX_LENGTH: 200,
		CONTENT_MAX_LENGTH: 10000,
		EXCERPT_MAX_LENGTH: 500,
	},
	COMMENT: {
		MAX_LENGTH: 1000,
	},
} as const;
