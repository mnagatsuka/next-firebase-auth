import { getBlogPosts } from "@/lib/api/generated/client";
import { BlogHomePage } from "@/components/blog/BlogHomePage";
import type { BlogPostListData } from "@/lib/api/generated/schemas";

interface HomeProps {
  searchParams: Promise<{ page?: string }>
}

export default async function Home({ searchParams }: HomeProps) {
  const { page: pageParam } = await searchParams;
  const currentPage = Number(pageParam) || 1;
  
  try {
    const response = await getBlogPosts({ page: currentPage, limit: 10 }) as BlogPostListData;
    
    const posts = response?.posts || [];
    const pagination = response?.pagination || {
      page: currentPage,
      limit: 10,
      total: 0,
      hasNext: false
    };

    return (
      <BlogHomePage 
        initialPosts={posts} 
        initialPagination={pagination} 
      />
    );
  } catch (error) {
    console.error("❌ API Error:", error);
    
    // Return empty state on error
    return (
      <BlogHomePage 
        initialPosts={[]} 
        initialPagination={{
          page: currentPage,
          limit: 10,
          total: 0,
          hasNext: false
        }} 
      />
    );
  }
}