import {
	getCreateBlogPostMockHandler,
	getGetBlogPostByIdMockHandler,
	getGetBlogPostsMockHandler,
	getGetPostCommentsMockHandler,
} from "@/lib/api/generated/client.msw";
import type {
	BlogPostListResponse,
	BlogPostResponse,
	CommentsResponse,
	CreatePostRequest,
} from "@/lib/api/generated/schemas";
import { makeComment } from "../factories/comment";
import { makePost, makePostSummary } from "../factories/post";

/**
 * Scenario: Ensure list ⇄ detail ⇄ comments consistency by ID.
 * - Returns handlers for GET /posts, GET /posts/:id, GET /posts/:id/comments
 * - Uses examples as defaults and overrides only minimal fields
 */
export function scenarioPostsConsistent(params?: {
	seed?: number;
	total?: number;
	page?: number;
	limit?: number;
	selectedId?: string;
}) {
	const seed = params?.seed ?? 1;
	const total = params?.total ?? 3;
	const page = params?.page ?? 1;
	const limit = params?.limit ?? 10;

	const selected = params?.selectedId ?? makePostSummary({}, seed).id;

	const listHandler = getGetBlogPostsMockHandler(async (info) => {
		// Read query if present for pagination
		const url = new URL(info.request.url);
		const qPage = Number(url.searchParams.get("page") ?? page);
		const qLimit = Number(url.searchParams.get("limit") ?? limit);

		// Create a small deterministic list ensuring selectedId is present
		const posts = Array.from({ length: Math.min(total, qLimit) }, (_, i) =>
			makePostSummary({ id: i === 0 ? selected : makePostSummary({}, seed + i + 1).id }, seed + i),
		);

		const hasNext = qPage * qLimit < total;

		const response: BlogPostListResponse = {
			status: "success",
			data: {
				posts,
				pagination: { page: qPage, limit: qLimit, total, hasNext },
			},
		};
		return response;
	});

	const detailHandler = getGetBlogPostByIdMockHandler(async (info) => {
		const id = (info.params as any)?.id || selected;
		const response: BlogPostResponse = {
			status: "success",
			data: makePost({ id }, seed + 100),
		};
		return response;
	});

	const commentsHandler = getGetPostCommentsMockHandler(async (info) => {
		const id = (info.params as any)?.id || selected;
		const response: CommentsResponse = {
			status: "success",
			data: [makeComment({}, seed + 200, id), makeComment({}, seed + 201, id)],
		};
		return response;
	});

	return [listHandler, detailHandler, commentsHandler];
}

/**
 * Scenario: Create → Get flow using closure state.
 * - POST /posts captures created entity
 * - GET /posts/:id returns that entity when ID matches
 */
export function scenarioCreateThenGet(seed = 1) {
	let created: BlogPostResponse["data"] | null = null;

	const createHandler = getCreateBlogPostMockHandler(async (info) => {
		const body = (await info.request.json()) as Partial<CreatePostRequest>;
		const id = makePost({}, seed).id;
		created = makePost({ id, ...body }, seed);
		return { status: "success", data: created };
	});

	const getByIdHandler = getGetBlogPostByIdMockHandler(async (info) => {
		const id = (info.params as any)?.id;
		if (created && created.id === id) {
			return { status: "success", data: created };
		}
		// fall back to example-based generated response when not matching
		return { status: "success", data: makePost({ id }, seed + 1000) };
	});

	return [createHandler, getByIdHandler];
}

/**
 * Scenario: Paginated list continuity based on query params.
 */
export function scenarioPaginatedList(total = 25, seed = 1) {
	return [
		getGetBlogPostsMockHandler(async (info) => {
			const url = new URL(info.request.url);
			const page = Number(url.searchParams.get("page") ?? 1);
			const limit = Number(url.searchParams.get("limit") ?? 10);
			const start = (page - 1) * limit;
			const end = Math.min(start + limit, total);
			const count = Math.max(0, end - start);
			const posts = Array.from({ length: count }, (_, i) => makePostSummary({}, seed + start + i));
			const hasNext = page * limit < total;
			const response: BlogPostListResponse = {
				status: "success",
				data: {
					posts,
					pagination: { page, limit, total, hasNext },
				},
			};
			return response;
		}),
	];
}
