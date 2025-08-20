import type { Comment } from "@/lib/api/generated/schemas";
import { addMinutesIso, fixedIso } from "../utils/fixed-time";
import { createRng, makeId, sentence } from "../utils/seeded-rng";

export function makeComment(overrides: Partial<Comment> = {}, seed = 1, postId?: string): Comment {
	const rng = createRng(seed);
	const id = overrides.id ?? makeId(rng, "comment");
	const content = overrides.content ?? sentence(rng, 14);
	const author = overrides.author ?? "Jane Smith";
	const createdAt = overrides.createdAt ?? addMinutesIso(fixedIso(), 230);
	const finalPostId = overrides.postId ?? postId ?? "post-123";

	return {
		id,
		content,
		author,
		createdAt,
		postId: finalPostId,
		...overrides,
	};
}
