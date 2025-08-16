"use client"

import { useGetBlogPosts } from "@/lib/api/generated/client"
import type { BlogPostListData } from "@/lib/api/generated/schemas"

export default function ApiTestPage() {
  const { data, isLoading, error } = useGetBlogPosts({ page: 1, limit: 10 })

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">API Test Page (Client-side)</h1>
      
      {isLoading && (
        <div className="text-blue-600">Loading posts...</div>
      )}

      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <strong>Error:</strong> {error instanceof Error ? error.message : String(error)}
        </div>
      )}

      {data && (
        <div className="mt-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          <strong>Success!</strong> Found {(data as BlogPostListData).posts?.length || 0} posts
          <pre className="mt-2 text-sm overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}