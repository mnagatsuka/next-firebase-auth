/**
 * Shared authentication types
 */

export interface User {
	uid: string;
	email: string | null;
	displayName: string | null;
	isAnonymous: boolean;
	emailVerified: boolean;
}

export interface AuthError {
	type: 'auth' | 'network' | 'validation' | 'unknown';
	message: string;
	code?: string;
}

export type AuthStatus = 'authenticated' | 'unauthenticated' | 'loading' | 'error';

export interface AuthState {
	user: User | null;
	status: AuthStatus;
	error: AuthError | null;
}