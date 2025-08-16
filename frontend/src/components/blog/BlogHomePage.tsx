"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { PostList } from "./PostList"
import { Pagination } from "./Pagination"
import { getBlogPosts } from "@/lib/api/generated/client"
import type { BlogPostSummary } from "@/lib/api/generated/schemas"

interface BlogHomePageProps {
  initialPosts: BlogPostSummary[]
  initialPagination: {
    page: number
    limit: number
    total: number
    hasNext: boolean
  }
}

export function BlogHomePage({ initialPosts, initialPagination }: BlogHomePageProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [posts, setPosts] = useState(initialPosts)
  const [pagination, setPagination] = useState(initialPagination)
  const [isLoading, setIsLoading] = useState(false)

  const currentPage = Number(searchParams.get("page")) || 1

  // Update posts when page changes
  useEffect(() => {
    if (currentPage === initialPagination.page) {
      // Use initial data for the first page
      setPosts(initialPosts)
      setPagination(initialPagination)
      return
    }

    const loadPosts = async () => {
      try {
        setIsLoading(true)
        const response = await getBlogPosts({ 
          page: currentPage, 
          limit: initialPagination.limit 
        })
        
        setPosts(response?.data?.posts || [])
        setPagination(response?.data?.pagination || {
          page: currentPage,
          limit: initialPagination.limit,
          total: 0,
          hasNext: false
        })
      } catch (error) {
        console.error("Failed to load posts:", error)
        // Keep current state on error
      } finally {
        setIsLoading(false)
      }
    }

    loadPosts()
  }, [currentPage, initialPosts, initialPagination])

  const handlePageChange = (page: number) => {
    // Update URL with new page number
    const params = new URLSearchParams(searchParams)
    if (page === 1) {
      params.delete("page")
    } else {
      params.set("page", page.toString())
    }
    
    const newUrl = params.toString() ? `/?${params.toString()}` : "/"
    router.push(newUrl)
  }

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold">Blog</h1>
      
      {isLoading ? (
        <div className="space-y-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-1"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          ))}
        </div>
      ) : (
        <PostList posts={posts} />
      )}
      
      <Pagination 
        currentPage={pagination.page}
        totalPages={Math.ceil(pagination.total / pagination.limit)}
        hasNext={pagination.hasNext}
        hasPrevious={pagination.page > 1}
        onPageChange={handlePageChange}
      />
    </div>
  )
}