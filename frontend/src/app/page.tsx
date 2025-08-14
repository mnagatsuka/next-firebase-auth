import { getBlogPosts } from "@/lib/api/posts";
import { PostList } from "@/components/blog/PostList";
import { Pagination } from "@/components/blog/Pagination";

export default async function Home() {
  const { posts, pagination } = await getBlogPosts();

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold">Blog</h1>
      <PostList posts={posts} />
      <Pagination 
        currentPage={pagination.page}
        totalPages={Math.ceil(pagination.total / pagination.limit)}
        hasNext={pagination.hasNext}
        hasPrevious={pagination.page > 1}
      />
    </div>
  );
}