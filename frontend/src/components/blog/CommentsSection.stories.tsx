import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { HttpResponse, http } from "msw";
import { CommentsSection } from "./CommentsSection";

const meta: Meta<typeof CommentsSection> = {
	title: "Blog/CommentsSection",
	component: CommentsSection,
	parameters: {
		layout: "padded",
	},
	tags: ["autodocs"],
	argTypes: {
		postId: { control: "text" },
	},
};

export default meta;
type Story = StoryObj<typeof CommentsSection>;

export const WithComments: Story = {
	args: {
		postId: "post-with-comments",
	},
	parameters: {
		msw: {
			handlers: [
				http.get("*/posts/:id/comments", ({ params }) => {
					if (params.id === "post-with-comments") {
						return HttpResponse.json({
							status: "success",
							data: [
								{
									id: "comment-1",
                            postId: params.id,
                            userId: "uid_alice",
									content:
										"Great article! Very helpful for beginners. I learned a lot from the examples you provided.",
									createdAt: "2024-01-16T08:30:00Z",
								},
                        {
                            id: "comment-2",
                            postId: params.id,
                            userId: "uid_bob",
                            content:
                                "Thanks for sharing this. Looking forward to more content like this. The explanations were very clear.",
                            createdAt: "2024-01-16T10:15:00Z",
                        },
                        {
                            id: "comment-3",
                            postId: params.id,
                            userId: "uid_carol",
                            content: "Excellent post! Could you write a follow-up about advanced topics?",
                            createdAt: "2024-01-16T14:22:00Z",
                        },
							],
						});
					}
					// Fallback for other IDs
					return HttpResponse.json({ status: "success", data: [] });
				}),
				http.post("*/posts/:id/comments", async ({ request, params }) => {
                    const body = (await request.json()) as { content: string };
					return HttpResponse.json(
						{
                        id: `comment-${Date.now()}`,
                        postId: params.id,
                        userId: "uid_mock",
                        content: body.content,
                        createdAt: new Date().toISOString(),
						},
						{ status: 201 },
					);
				}),
			],
		},
	},
};

export const NoComments: Story = {
	args: {
		postId: "post-no-comments",
	},
	parameters: {
		msw: {
			handlers: [
				http.get("*/posts/post-no-comments/comments", () => {
					return HttpResponse.json({
						status: "success",
						data: [],
					});
				}),
			],
		},
	},
};

export const Loading: Story = {
	args: {
		postId: "post-loading",
	},
	parameters: {
		msw: {
			handlers: [
				http.get("*/posts/post-loading/comments", () => {
					// Delay response to show loading state
					return new Promise((resolve) => {
						setTimeout(() => {
							resolve(
								HttpResponse.json({
									status: "success",
									data: [],
								}),
							);
						}, 3000); // 3 second delay
					});
				}),
			],
		},
	},
};

export const ErrorState: Story = {
	args: {
		postId: "post-error",
	},
	parameters: {
		msw: {
			handlers: [
				http.get("*/posts/post-error/comments", () => {
					return HttpResponse.json(
						{
							status: "error",
							error: {
								code: "INTERNAL_SERVER_ERROR",
								message: "Failed to load comments. Please try again later.",
							},
						},
						{ status: 500 },
					);
				}),
			],
		},
	},
};

// Add a story with many comments to show scrolling behavior
export const ManyComments: Story = {
	args: {
		postId: "post-many-comments",
	},
	parameters: {
		msw: {
			handlers: [
				http.get("*/posts/post-many-comments/comments", ({ params }) => {
                    const manyComments = Array.from({ length: 8 }, (_, i) => ({
                        id: `comment-${i + 1}`,
                        postId: params.id,
                        userId: `uid_user_${i + 1}`,
                        content: `This is comment number ${i + 1}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.`,
                        createdAt: new Date(Date.now() - i * 60 * 60 * 1000).toISOString(), // Each comment 1 hour apart
                    }));

					return HttpResponse.json({
						status: "success",
						data: manyComments,
					});
				}),
			],
		},
	},
};
