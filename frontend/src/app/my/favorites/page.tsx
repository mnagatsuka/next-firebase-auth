"use client";

import { useEffect, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { PostList } from "@/components/blog/PostList";
import { BlogPagination } from "@/components/blog/BlogPagination";
import { useAuth } from "@/hooks/useAuth";
import { useGetUserFavorites } from "@/lib/api/generated/client";

export default function FavoritePostsPage() {
  const { user, isLoading: authLoading, signInAnonymously } = useAuth();
  const params = useSearchParams();

  const page = Math.max(1, Number(params.get("page") ?? "1") || 1);
  const limit = 10;

  const uid = user?.uid;

  useEffect(() => {
    if (!uid && !authLoading) {
      // Ensure we have an anonymous session so we can fetch favorites
      signInAnonymously().catch(() => {});
    }
  }, [uid, authLoading, signInAnonymously]);

  // Memoize params to keep React Query key stable across renders
  const favParams = useMemo(() => ({ page, limit }), [page, limit]);
  const favQuery = useGetUserFavorites(uid ?? "", favParams);
  const posts = (favQuery.data as any)?.data?.posts ?? [];
  const pagination = (favQuery.data as any)?.data?.pagination ?? { page, limit, total: 0, hasNext: false };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Favorite Posts</h1>
      </div>

      {favQuery.error ? (
        <PostList posts={[]} emptyMessage="Failed to load favorites. Please try again." />
      ) : (
        <PostList
          posts={posts}
          isLoading={favQuery.isLoading}
          emptyMessage="No favorites yet. Browse posts and add some!"
          actions="view-only"
        />
      )}

      <BlogPagination
        currentPage={pagination.page}
        totalPages={Math.max(1, Math.ceil((pagination.total ?? 0) / (pagination.limit || 10)))}
        hasNext={!!pagination.hasNext}
        hasPrevious={pagination.page > 1}
        basePath="/my/favorites"
      />
    </div>
  );
}
