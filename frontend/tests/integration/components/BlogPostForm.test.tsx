import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { BlogPostForm } from "@/components/blog/BlogPostForm";
import { renderWithProviders } from "../../test-utils";

describe("BlogPostForm Integration", () => {
	const user = userEvent.setup();
	const mockOnSubmit = vi.fn();
	const mockOnSaveDraft = vi.fn();
	const mockOnCancel = vi.fn();

	beforeEach(() => {
		mockOnSubmit.mockClear();
		mockOnSaveDraft.mockClear();
		mockOnCancel.mockClear();
	});

	const defaultProps = {
		onSubmit: mockOnSubmit,
		onSaveDraft: mockOnSaveDraft,
		onCancel: mockOnCancel,
		isLoading: false,
	};

	describe("Form Rendering", () => {
		it("should render create form with all fields", () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			expect(screen.getByText(/create new blog post/i)).toBeInTheDocument();
			expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
			expect(screen.getByLabelText(/excerpt/i)).toBeInTheDocument();
			expect(screen.getByLabelText(/content/i)).toBeInTheDocument();
			expect(screen.getByLabelText(/tags/i)).toBeInTheDocument();
			expect(screen.getByRole("button", { name: /save draft/i })).toBeInTheDocument();
			expect(screen.getByRole("button", { name: /publish/i })).toBeInTheDocument();
			expect(screen.getByRole("button", { name: /cancel/i })).toBeInTheDocument();
		});

		it("should render edit form with initial data", () => {
			const initialData = {
				title: "Existing Post Title",
				content: "Existing post content",
				excerpt: "Existing excerpt",
				tags: ["react", "typescript"],
				status: "draft" as const,
			};

			renderWithProviders(<BlogPostForm {...defaultProps} initialData={initialData} />);

			expect(screen.getByText(/edit blog post/i)).toBeInTheDocument();
			expect(screen.getByDisplayValue("Existing Post Title")).toBeInTheDocument();
			expect(screen.getByDisplayValue("Existing post content")).toBeInTheDocument();
			expect(screen.getByDisplayValue("Existing excerpt")).toBeInTheDocument();
			expect(screen.getByText("react")).toBeInTheDocument();
			expect(screen.getByText("typescript")).toBeInTheDocument();
		});
	});

	describe("Form Validation", () => {
		it("should disable publish button when title is empty", () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const publishButton = screen.getByRole("button", { name: /publish/i });
			expect(publishButton).toBeDisabled();
		});

		it("should disable publish button when content is empty", async () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const titleInput = screen.getByLabelText(/title/i);
			await user.type(titleInput, "Test Title");

			const publishButton = screen.getByRole("button", { name: /publish/i });
			expect(publishButton).toBeDisabled();
		});

		it("should enable publish button when title and content are provided", async () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const titleInput = screen.getByLabelText(/title/i);
			const contentInput = screen.getByLabelText(/content/i);

			await user.type(titleInput, "Test Title");
			await user.type(contentInput, "Test content");

			const publishButton = screen.getByRole("button", { name: /publish/i });
			expect(publishButton).toBeEnabled();
		});

		it("should enable save draft button when only title is provided", async () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const titleInput = screen.getByLabelText(/title/i);
			await user.type(titleInput, "Test Title");

			const saveDraftButton = screen.getByRole("button", { name: /save draft/i });
			expect(saveDraftButton).toBeEnabled();
		});
	});

	describe("Form Submission", () => {
		it("should call onSubmit with correct data when publishing", async () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const titleInput = screen.getByLabelText(/title/i);
			const contentInput = screen.getByLabelText(/content/i);
			const excerptInput = screen.getByLabelText(/excerpt/i);

			await user.type(titleInput, "Test Title");
			await user.type(contentInput, "Test content");
			await user.type(excerptInput, "Test excerpt");

			const publishButton = screen.getByRole("button", { name: /publish/i });
			await user.click(publishButton);

			expect(mockOnSubmit).toHaveBeenCalledWith({
				title: "Test Title",
				content: "Test content",
				excerpt: "Test excerpt",
				tags: [],
				status: "published",
			});
		});

		it("should call onSaveDraft with correct data when saving draft", async () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const titleInput = screen.getByLabelText(/title/i);
			const contentInput = screen.getByLabelText(/content/i);

			await user.type(titleInput, "Draft Title");
			await user.type(contentInput, "Draft content");

			const saveDraftButton = screen.getByRole("button", { name: /save draft/i });
			await user.click(saveDraftButton);

			expect(mockOnSaveDraft).toHaveBeenCalledWith({
				title: "Draft Title",
				content: "Draft content",
				excerpt: "",
				tags: [],
				status: "draft",
			});
		});

		it("should call onCancel when cancel button is clicked", async () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const cancelButton = screen.getByRole("button", { name: /cancel/i });
			await user.click(cancelButton);

			expect(mockOnCancel).toHaveBeenCalled();
		});
	});

	describe("Tags Management", () => {
		it("should add tags when typing and pressing Enter", async () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const tagInput = screen.getByLabelText(/tags/i);
			await user.type(tagInput, "react");
			await user.keyboard("[Enter]");

			expect(screen.getByText("react")).toBeInTheDocument();
			expect(tagInput).toHaveValue("");
		});

		it("should add tags when clicking Add button", async () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const tagInput = screen.getByLabelText(/tags/i);
			const addButton = screen.getByRole("button", { name: /add/i });

			await user.type(tagInput, "typescript");
			await user.click(addButton);

			expect(screen.getByText("typescript")).toBeInTheDocument();
			expect(tagInput).toHaveValue("");
		});

		it("should remove tags when clicking X button", async () => {
			const initialData = {
				tags: ["react", "typescript"],
			};

			renderWithProviders(<BlogPostForm {...defaultProps} initialData={initialData} />);

			const reactTag = screen.getByText("react");
			expect(reactTag).toBeInTheDocument();

			// Find the remove button for the react tag
			const removeButton = reactTag.parentElement?.querySelector("button");
			if (removeButton) {
				await user.click(removeButton);
			}

			expect(screen.queryByText("react")).not.toBeInTheDocument();
			expect(screen.getByText("typescript")).toBeInTheDocument();
		});

		it("should not add duplicate tags", async () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const tagInput = screen.getByLabelText(/tags/i);

			await user.type(tagInput, "react");
			await user.keyboard("[Enter]");
			await user.type(tagInput, "react");
			await user.keyboard("[Enter]");

			const reactTags = screen.getAllByText("react");
			expect(reactTags).toHaveLength(1);
		});
	});

	describe("Loading States", () => {
		it("should disable all inputs and buttons when loading", () => {
			renderWithProviders(<BlogPostForm {...defaultProps} isLoading={true} />);

			expect(screen.getByLabelText(/title/i)).toBeDisabled();
			expect(screen.getByLabelText(/content/i)).toBeDisabled();
			expect(screen.getByLabelText(/excerpt/i)).toBeDisabled();
			expect(screen.getByLabelText(/tags/i)).toBeDisabled();
			expect(screen.getByRole("button", { name: /add/i })).toBeDisabled();
			expect(screen.getByRole("button", { name: /cancel/i })).toBeDisabled();
		});

		it("should show loading text on buttons when loading", () => {
			renderWithProviders(<BlogPostForm {...defaultProps} isLoading={true} />);

			expect(screen.getByText(/saving/i)).toBeInTheDocument();
			expect(screen.getByText(/publishing/i)).toBeInTheDocument();
		});
	});

	describe("Accessibility", () => {
		it("should have proper labels and ARIA attributes", () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			expect(screen.getByLabelText(/title/i)).toHaveAttribute("required");
			expect(screen.getByLabelText(/content/i)).toHaveAttribute("required");

			const publishButton = screen.getByRole("button", { name: /publish/i });
			expect(publishButton).toHaveAttribute("disabled");
		});

		it("should be keyboard navigable", async () => {
			renderWithProviders(<BlogPostForm {...defaultProps} />);

			const titleInput = screen.getByLabelText(/title/i);
			const excerptInput = screen.getByLabelText(/excerpt/i);
			const contentInput = screen.getByLabelText(/content/i);

			// Should be able to tab through form fields
			titleInput.focus();
			expect(titleInput).toHaveFocus();

			await user.keyboard("[Tab]");
			expect(excerptInput).toHaveFocus();

			await user.keyboard("[Tab]");
			expect(contentInput).toHaveFocus();
		});
	});
});
