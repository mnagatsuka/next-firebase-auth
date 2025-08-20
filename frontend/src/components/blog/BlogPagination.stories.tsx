import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { BlogPagination } from "./BlogPagination";

const meta: Meta<typeof BlogPagination> = {
	title: "Blog/BlogPagination",
	component: BlogPagination,
	parameters: {
		layout: "centered",
		nextjs: {
			appDirectory: true,
		},
	},
	tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof BlogPagination>;

export const FirstPage: Story = {
	args: {
		currentPage: 1,
		totalPages: 10,
		hasNext: true,
		hasPrevious: false,
	},
};

export const MiddlePage: Story = {
	args: {
		currentPage: 5,
		totalPages: 10,
		hasNext: true,
		hasPrevious: true,
	},
};

export const LastPage: Story = {
	args: {
		currentPage: 10,
		totalPages: 10,
		hasNext: false,
		hasPrevious: true,
	},
};

export const SinglePage: Story = {
	args: {
		currentPage: 1,
		totalPages: 1,
		hasNext: false,
		hasPrevious: false,
	},
};

export const FewPages: Story = {
	args: {
		currentPage: 2,
		totalPages: 3,
		hasNext: true,
		hasPrevious: true,
	},
};
