import type {
	BlogPost,
	BlogPostStatus,
	BlogPostSummary,
	CreatePostRequest,
} from "@/lib/api/generated/schemas";
import { addMinutesIso, fixedIso } from "../utils/fixed-time";
import { createRng, makeId, sentence } from "../utils/seeded-rng";

export function makePostSummary(
	overrides: Partial<BlogPostSummary> = {},
	seed = 1,
): BlogPostSummary {
	const rng = createRng(seed);
	const id = overrides.id ?? makeId(rng, "post");
	const title = overrides.title ?? sentence(rng, 5).replace(".", "");
	const excerpt = overrides.excerpt ?? sentence(rng, 14);
	const author = overrides.author ?? "Test Author";
	const publishedAt = overrides.publishedAt ?? fixedIso();

	return {
		id,
		title,
		excerpt,
		author,
		publishedAt,
		...overrides,
	};
}

export function makePost(overrides: Partial<BlogPost> = {}, seed = 1): BlogPost {
	const rng = createRng(seed);
	const summary = makePostSummary(overrides as Partial<BlogPostSummary>, seed);
	const content =
		overrides.content ?? `# ${summary.title}\n\n${sentence(rng, 20)}\n\n${sentence(rng, 18)}`;
	const status: BlogPostStatus = (overrides.status as BlogPostStatus) ?? "published";
	const publishedAt = overrides.publishedAt ?? addMinutesIso(summary.publishedAt, 0);

	return {
		...summary,
		content,
		status,
		publishedAt,
		...overrides,
	};
}

export function makeCreatePostRequest(
	overrides: Partial<CreatePostRequest> = {},
	seed = 1,
): CreatePostRequest {
	const rng = createRng(seed);
	const title = overrides.title ?? sentence(rng, 5).replace(".", "");
	const content = overrides.content ?? `${sentence(rng, 16)}\n\n${sentence(rng, 16)}`;
	const excerpt = overrides.excerpt ?? sentence(rng, 12);
	const status = overrides.status ?? "draft";
	return { title, content, excerpt, status };
}
