export interface BlogPostSummary {
  id: string;
  title: string;
  excerpt: string;
  author: string;
  publishedAt: string;
  tags?: string[];
}

export interface PaginationData {
  page: number;
  limit: number;
  total: number;
  hasNext: boolean;
}

export interface BlogPostListResponse {
  status: "success" | "error";
  data: {
    posts: BlogPostSummary[];
    pagination: PaginationData;
  };
}
