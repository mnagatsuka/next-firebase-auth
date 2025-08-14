import type { BlogPostListResponse, BlogPostSummary, PaginationData } from "@/types/blog";

// This is a mock data fetching function. In a real application, this would
// fetch data from a live API endpoint.
export async function getBlogPosts(page: number = 1, limit: number = 10): Promise<{ posts: BlogPostSummary[], pagination: PaginationData }> {
  // Mock data based on docs/specifications/api/components/examples/blog-post-list-response.yml
  const mockResponse: BlogPostListResponse = {
    status: "success",
    data: {
      posts: [
        {
          id: "post-123",
          title: "Getting Started with Next.js",
          excerpt: "Learn the basics of Next.js in this comprehensive guide covering SSR, SSG, and CSR.",
          author: "John Doe",
          publishedAt: "2024-01-15T10:30:00Z",
          tags: ["Next.js", "React", "TypeScript"],
        },
        {
          id: "post-124",
          title: "Advanced React Patterns",
          excerpt: "Explore advanced React patterns including hooks, context, and state management techniques.",
          author: "Jane Smith",
          publishedAt: "2024-01-14T09:15:00Z",
          tags: ["React", "Patterns", "Hooks"],
        },
        {
          id: "post-125",
          title: "TypeScript Best Practices",
          excerpt: "Learn TypeScript best practices for building scalable and maintainable applications.",
          author: "Bob Johnson",
          publishedAt: "2024-01-13T14:45:00Z",
          tags: ["TypeScript", "Best Practices"],
        },
        {
          id: "post-126",
          title: "Styling in Next.js with Tailwind CSS",
          excerpt: "A deep dive into using Tailwind CSS for utility-first styling in Next.js projects.",
          author: "Alice Wilson",
          publishedAt: "2024-01-12T16:20:00Z",
          tags: ["Styling", "Tailwind CSS"],
        },
        {
          id: "post-127",
          title: "State Management with Zustand",
          excerpt: "A guide to lightweight state management in React applications using Zustand.",
          author: "Charlie Brown",
          publishedAt: "2024-01-11T08:30:00Z",
          tags: ["State Management", "Zustand"],
        },
        {
          id: "post-128",
          title: "API Mocking with MSW",
          excerpt: "Learn how to mock API requests in your tests and Storybook using Mock Service Worker.",
          author: "Diana Prince",
          publishedAt: "2024-01-10T11:00:00Z",
          tags: ["Testing", "MSW"],
        },
      ],
      pagination: {
        page: page,
        limit: limit,
        total: 45,
        hasNext: page * limit < 45,
      },
    },
  };

  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));

  return mockResponse.data;
}
