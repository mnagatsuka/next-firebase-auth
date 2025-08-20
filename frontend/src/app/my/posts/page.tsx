"use client";

import { useSearchParams } from "next/navigation";
import { PostList } from "@/components/blog/PostList";
import { BlogPagination } from "@/components/blog/BlogPagination";
import { useAuth } from "@/hooks/useAuth";
import { useGetUserPosts } from "@/lib/api/generated/client";

export default function MyPostsPage() {
  const { user, isLoading: authLoading } = useAuth();
  const params = useSearchParams();

  const page = Math.max(1, Number(params.get("page") ?? "1") || 1);

  const { data, isLoading, error } = useGetUserPosts(user?.uid ?? "", {
    page,
    limit: 10,
  });

  const posts = data?.data?.posts ?? [];
  const pagination = data?.data?.pagination ?? { page, limit: 10, total: 0, hasNext: false };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">My Posts</h1>
      </div>

      {/* Loading or auth initializing state */}
      {authLoading ? (
        <PostList posts={[]} isLoading emptyMessage="Loading your posts..." showStatus={false} />
      ) : error ? (
        <PostList posts={[]} emptyMessage="Failed to load your posts. Please try again." />
      ) : (
        <>
          <PostList
            posts={posts as any[]}
            isLoading={isLoading}
            emptyMessage="No posts yet."
            showStatus
            actions="view-and-edit"
          />

          <BlogPagination
            currentPage={pagination.page ?? page}
            totalPages={Math.max(1, Math.ceil((pagination.total ?? 0) / (pagination.limit || 10)))}
            hasNext={!!pagination.hasNext}
            hasPrevious={(pagination.page ?? page) > 1}
            basePath="/my/posts"
          />
        </>
      )}
    </div>
  );
}
