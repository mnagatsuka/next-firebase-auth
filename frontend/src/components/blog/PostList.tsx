import { PostCard, PostCardProps } from "./PostCard"

export interface PostListProps {
  /** Array of blog posts to display */
  posts: PostCardProps[]
  /** Loading state */
  isLoading?: boolean
  /** Empty state message */
  emptyMessage?: string
}

export function PostList({ 
  posts, 
  isLoading = false, 
  emptyMessage = "No posts found." 
}: PostListProps) {
  if (isLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-64 bg-gray-200 rounded-lg"></div>
          </div>
        ))}
      </div>
    )
  }

  if (posts.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground text-lg">{emptyMessage}</p>
      </div>
    )
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {posts.map((post) => (
        <PostCard key={post.id} {...post} />
      ))}
    </div>
  )
}