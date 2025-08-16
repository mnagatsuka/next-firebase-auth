"use client"

import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"

export interface PostCardProps {
  /** Unique post identifier */
  id: string
  /** Post title */
  title: string
  /** Post excerpt/summary */
  excerpt: string
  /** Post author name */
  author: string
  /** Publication date */
  publishedAt: string
  /** Optional post tags */
  tags?: string[]
  /** Callback for read more action */
  onReadMore?: (id: string) => void
}

export function PostCard({ 
  id, 
  title, 
  excerpt, 
  author, 
  publishedAt, 
  tags = [],
  onReadMore 
}: PostCardProps) {
  const [formattedDate, setFormattedDate] = useState<string | null>(null)

  useEffect(() => {
    setFormattedDate(
      new Date(publishedAt).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    )
  }, [publishedAt])

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex flex-wrap gap-1 mb-2">
          {tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
        <CardTitle className="line-clamp-2">
          <Link 
            href={`/posts/${id}`} 
            className="hover:underline"
          >
            {title}
          </Link>
        </CardTitle>
        <CardDescription>
          By {author} {formattedDate && `• ${formattedDate}`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
          {excerpt}
        </p>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => onReadMore?.(id)}
          asChild
        >
          <Link href={`/posts/${id}`}>
            Read more
          </Link>
        </Button>
      </CardContent>
    </Card>
  )
}