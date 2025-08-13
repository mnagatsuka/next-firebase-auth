import { Badge } from "@/components/ui/badge"

export interface BlogPostContentProps {
  /** Post title */
  title: string
  /** Post content (markdown or plain text) */
  content: string
  /** Post author */
  author: string
  /** Publication date */
  publishedAt: string
  /** Post tags */
  tags?: string[]
  /** Reading time estimate */
  readingTime?: string
}

export function BlogPostContent({
  title,
  content,
  author,
  publishedAt,
  tags = [],
  readingTime
}: BlogPostContentProps) {
  const formattedDate = new Date(publishedAt).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })

  return (
    <article className="max-w-4xl mx-auto">
      <header className="mb-8 pb-8 border-b">
        <div className="flex flex-wrap gap-2 mb-4">
          {tags.map((tag) => (
            <Badge key={tag} variant="secondary">
              {tag}
            </Badge>
          ))}
        </div>
        
        <h1 className="text-4xl font-bold mb-4 leading-tight">
          {title}
        </h1>
        
        <div className="flex items-center text-muted-foreground space-x-4">
          <span>By {author}</span>
          <span>•</span>
          <span>{formattedDate}</span>
          {readingTime && (
            <>
              <span>•</span>
              <span>{readingTime}</span>
            </>
          )}
        </div>
      </header>
      
      <div className="prose prose-lg max-w-none">
        {/* For now, rendering content as plain text. In production, you'd use a markdown parser */}
        {content.split('\\n').map((paragraph, index) => (
          <p key={index} className="mb-4 leading-relaxed">
            {paragraph}
          </p>
        ))}
      </div>
    </article>
  )
}