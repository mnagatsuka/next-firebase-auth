"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { X, Loader2 } from "lucide-react"

export interface BlogPostFormData {
  title: string
  content: string
  excerpt: string
  tags: string[]
  status: "draft" | "published"
}

export interface BlogPostFormProps {
  /** Initial form data */
  initialData?: Partial<BlogPostFormData>
  /** Whether form is in loading/submitting state */
  isLoading?: boolean
  /** Callback for form submission */
  onSubmit?: (data: BlogPostFormData) => void
  /** Callback for saving draft */
  onSaveDraft?: (data: BlogPostFormData) => void
  /** Callback for cancel action */
  onCancel?: () => void
}

export function BlogPostForm({
  initialData = {},
  isLoading = false,
  onSubmit,
  onSaveDraft,
  onCancel
}: BlogPostFormProps) {
  const [formData, setFormData] = useState<BlogPostFormData>({
    title: initialData.title || "",
    content: initialData.content || "",
    excerpt: initialData.excerpt || "",
    tags: initialData.tags || [],
    status: initialData.status || "draft"
  })
  
  const [newTag, setNewTag] = useState("")

  const handleInputChange = (field: keyof BlogPostFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }))
      setNewTag("")
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleAddTag()
    }
  }

  const handleSubmit = (status: "draft" | "published") => {
    const dataToSubmit = { ...formData, status }
    
    if (status === "published") {
      onSubmit?.(dataToSubmit)
    } else {
      onSaveDraft?.(dataToSubmit)
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>
          {initialData.title ? "Edit Blog Post" : "Create New Blog Post"}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <label htmlFor="title" className="text-sm font-medium">
            Title *
          </label>
          <Input
            id="title"
            placeholder="Enter your blog post title..."
            value={formData.title}
            onChange={(e) => handleInputChange("title", e.target.value)}
            disabled={isLoading}
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="excerpt" className="text-sm font-medium">
            Excerpt
          </label>
          <Textarea
            id="excerpt"
            placeholder="Brief summary of your post..."
            value={formData.excerpt}
            onChange={(e) => handleInputChange("excerpt", e.target.value)}
            disabled={isLoading}
            rows={3}
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="content" className="text-sm font-medium">
            Content *
          </label>
          <Textarea
            id="content"
            placeholder="Write your blog post content here..."
            value={formData.content}
            onChange={(e) => handleInputChange("content", e.target.value)}
            disabled={isLoading}
            rows={15}
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="tags" className="text-sm font-medium">
            Tags
          </label>
          <div className="flex gap-2">
            <Input
              id="tags"
              placeholder="Add a tag..."
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <Button
              type="button"
              variant="outline"
              onClick={handleAddTag}
              disabled={isLoading || !newTag.trim()}
            >
              Add
            </Button>
          </div>
          <div className="flex flex-wrap gap-2 mt-2">
            {formData.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  disabled={isLoading}
                  className="hover:text-destructive"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        </div>

        <div className="flex justify-between pt-6">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <div className="flex gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => handleSubmit("draft")}
              disabled={isLoading || !formData.title.trim()}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Saving...
                </>
              ) : (
                "Save Draft"
              )}
            </Button>
            <Button
              type="button"
              onClick={() => handleSubmit("published")}
              disabled={isLoading || !formData.title.trim() || !formData.content.trim()}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Publishing...
                </>
              ) : (
                "Publish"
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}