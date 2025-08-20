import { BlogPagination } from "@/components/blog/BlogPagination";
import { PostList } from "@/components/blog/PostList";
import { getBlogPosts } from "@/lib/api/generated/client";
import type { BlogPostListResponse } from "@/lib/api/generated/schemas";

interface HomeProps {
	searchParams: Promise<{ page?: string }>;
}

export default async function Home({ searchParams }: HomeProps) {
	const { page: pageParam } = await searchParams;
	const currentPage = Number(pageParam) || 1;

	try {
		// Get published posts only for Home
		const response = (await getBlogPosts({ page: currentPage, limit: 10, status: "published" })) as BlogPostListResponse;

		const posts = response?.data?.posts || [];
		const pagination = response?.data?.pagination || {
			page: currentPage,
			limit: 10,
			total: 0,
			hasNext: false,
		};

		return (
			<div className="space-y-12">
				<div className="flex items-center justify-between">
					<h1 className="text-4xl font-bold">Blog</h1>
				</div>

				{/* Published Posts */}
				<section className="space-y-4">
					<h2 className="text-2xl font-semibold">Latest Posts</h2>
					<PostList posts={posts} />
					<BlogPagination
						currentPage={currentPage}
						totalPages={Math.ceil(pagination.total / (pagination.limit || 10))}
						hasNext={pagination.hasNext}
						hasPrevious={currentPage > 1}
					/>
				</section>
			</div>
		);
	} catch (error) {
		console.error("Failed to load blog posts:", error);

		// Return empty state on error
		return (
			<div className="space-y-8">
				<div className="flex items-center justify-between">
					<h1 className="text-4xl font-bold">Blog</h1>
				</div>
				<PostList posts={[]} emptyMessage="Failed to load blog posts. Please try again later." />
			</div>
		);
	}
}
