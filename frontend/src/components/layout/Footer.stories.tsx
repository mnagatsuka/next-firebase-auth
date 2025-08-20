import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { Footer } from "./Footer";

const meta: Meta<typeof Footer> = {
	title: "Layout/Footer",
	component: Footer,
	parameters: {
		layout: "fullscreen",
	},
	tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof Footer>;

export const Default: Story = {
	args: {},
};

export const CustomSiteName: Story = {
	args: {
		siteName: "My Awesome Blog",
		year: 2024,
	},
};

export const DifferentYear: Story = {
	args: {
		siteName: "Tech Blog",
		year: 2023,
	},
};
