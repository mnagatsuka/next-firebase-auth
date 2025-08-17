"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { BlogPostForm, BlogPostFormData } from "@/components/blog/BlogPostForm"
import { getBlogPostById, createBlogPost } from "@/lib/api/generated/client"
import { toast } from "sonner"

export default function CreatePostPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const postId = searchParams.get("id")
  
  const [initialData, setInitialData] = useState<Partial<BlogPostFormData>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingPost, setIsLoadingPost] = useState(!!postId)

  // Load existing post data if editing
  useEffect(() => {
    if (!postId) return

    const loadPost = async () => {
      try {
        setIsLoadingPost(true)
        const response = await getBlogPostById(postId)
        const post = response.data
        
        setInitialData({
          title: post.title,
          content: post.content,
          excerpt: post.excerpt,
          status: post.status,
          tags: [] // TODO: Add tags to API schema if needed
        })
      } catch (error: any) {
        console.error("Failed to load post:", error)
        toast.error("Failed to load post for editing")
        router.push("/")
      } finally {
        setIsLoadingPost(false)
      }
    }

    loadPost()
  }, [postId, router])

  const handleSubmit = async (formData: BlogPostFormData) => {
    try {
      setIsLoading(true)
      
      if (postId) {
        // TODO: Implement update functionality when PUT endpoint is ready
        console.log("Would update post:", postId, formData)
        toast.success("Post updated successfully!")
      } else {
        // Create new post
        const response = await createBlogPost({
          title: formData.title,
          content: formData.content,
          excerpt: formData.excerpt || "",
          status: formData.status as "draft" | "published"
        })
        console.log("Created post:", response)
        toast.success("Post published successfully!")
      }
      
      // Navigate to home page or post detail
      router.push("/")
    } catch (error: any) {
      console.error("Failed to save post:", error)
      toast.error("Failed to save post")
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveDraft = async (formData: BlogPostFormData) => {
    try {
      setIsLoading(true)
      
      if (postId) {
        // TODO: Implement update functionality when PUT endpoint is ready
        console.log("Would update draft:", postId, formData)
        toast.success("Draft updated successfully!")
      } else {
        // Save as draft
        const response = await createBlogPost({
          title: formData.title,
          content: formData.content,
          excerpt: formData.excerpt || "",
          status: "draft"
        })
        console.log("Saved draft:", response)
        toast.success("Draft saved successfully!")
      }
    } catch (error: any) {
      console.error("Failed to save draft:", error)
      toast.error("Failed to save draft")
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    // TODO: Add confirmation dialog if there are unsaved changes
    router.back()
  }

  if (isLoadingPost) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="text-lg">Loading post...</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <BlogPostForm
        initialData={initialData}
        isLoading={isLoading}
        onSubmit={handleSubmit}
        onSaveDraft={handleSaveDraft}
        onCancel={handleCancel}
      />
    </div>
  )
}