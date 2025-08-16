import { notFound } from "next/navigation"
import { BlogPostContent } from "@/components/blog/BlogPostContent"
import { CommentsSection } from "@/components/blog/CommentsSection"
import { getBlogPostById } from "@/lib/api/generated/client"
import type { BlogPost } from "@/lib/api/generated/schemas"

interface BlogPostPageProps {
  params: Promise<{ id: string }>
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const { id: postId } = await params

  try {
    // customFetch.ts extracts the data property from BlogPostResponse, 
    // so we get BlogPost directly (same pattern as home page)
    const post = await getBlogPostById(postId) as unknown as BlogPost

    return (
      <div className="space-y-12">
        <BlogPostContent
          title={post.title}
          content={post.content}
          author={post.author}
          publishedAt={post.publishedAt}
          tags={[]} // TODO: Add tags to BlogPost schema if needed
        />
        <CommentsSection postId={postId} />
      </div>
    )
  } catch (error: any) {
    if (error.status === 404) {
      notFound()
    }
    throw error
  }
}
