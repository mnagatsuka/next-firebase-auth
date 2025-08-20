"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { BlogPostForm, type BlogPostFormData } from "@/components/blog/BlogPostForm";
import { QueryErrorBoundary } from "@/components/common/QueryErrorBoundary";
import { useCreateBlogPost, useGetBlogPostById, useUpdateBlogPost } from "@/lib/api/generated/client";

export default function CreatePostPage() {
	const router = useRouter();
	const searchParams = useSearchParams();
	const postId = searchParams.get("id");
	const isEditing = !!postId;

	// Load existing post data if editing
	const { data: existingPost, isLoading: isLoadingPost } = useGetBlogPostById(postId || "", {
		query: { enabled: isEditing },
	});

    // Mutations (no global handlers to avoid duplicate toasts)
    const createMutation = useCreateBlogPost();
    const updateMutation = useUpdateBlogPost();

	const initialData =
		existingPost?.status === "success"
			? {
					title: existingPost.data.title,
					content: existingPost.data.content,
					excerpt: existingPost.data.excerpt,
					status: existingPost.data.status,
					tags: [], // TODO: Add tags to API schema if needed
				}
			: {};

	const handleSubmit = (formData: BlogPostFormData) => {
		const payload = {
			title: formData.title,
			content: formData.content,
			excerpt: formData.excerpt || "",
			status: formData.status as "draft" | "published",
		};

        if (isEditing && postId) {
            updateMutation.mutate(
                { id: postId, data: payload },
                {
                    onSuccess: () => {
                        toast.success("Post updated successfully!");
                        router.push("/");
                    },
                    onError: (error) => {
                        console.error("Failed to update post:", error);
                        toast.error("Failed to update post");
                    },
                },
            );
        } else {
            createMutation.mutate(
                { data: payload },
                {
                    onSuccess: () => {
                        toast.success("Post created successfully!");
                        router.push("/");
                    },
                    onError: (error) => {
                        console.error("Failed to create post:", error);
                        toast.error("Failed to create post");
                    },
                },
            );
        }
	};

	const handleSaveDraft = (formData: BlogPostFormData) => {
		const payload = {
			title: formData.title,
			content: formData.content,
			excerpt: formData.excerpt || "",
			status: "draft" as const,
		};

        if (isEditing && postId) {
            updateMutation.mutate(
                { id: postId, data: payload },
                {
                    onSuccess: () => {
                        toast.success("Draft saved successfully!");
                        router.push("/");
                    },
                    onError: (error) => {
                        console.error("Update error:", error);
                        toast.error("Failed to save draft");
                    },
                },
            );
        } else {
            createMutation.mutate(
                { data: payload },
                {
                    onSuccess: () => {
                        toast.success("Draft saved successfully!");
                        router.push("/");
                    },
                    onError: (error) => {
                        console.error("Create error:", error);
                        toast.error("Failed to save draft");
                    },
                },
            );
        }
	};

	const handleCancel = () => {
		// TODO: Add confirmation dialog if there are unsaved changes
		router.back();
	};

	if (isLoadingPost) {
		return (
			<div className="flex justify-center items-center min-h-[50vh]">
				<div className="text-lg">Loading post...</div>
			</div>
		);
	}

	const isLoading = createMutation.isPending || updateMutation.isPending;

	return (
		<QueryErrorBoundary>
			<div className="container mx-auto py-8">
				<BlogPostForm
					initialData={initialData}
					isLoading={isLoading}
					onSubmit={handleSubmit}
					onSaveDraft={handleSaveDraft}
					onCancel={handleCancel}
				/>
			</div>
		</QueryErrorBoundary>
	);
}
