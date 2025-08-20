import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { Header } from "./Header";

const meta: Meta<typeof Header> = {
	title: "Layout/Header",
	component: Header,
	parameters: {
		layout: "fullscreen",
	},
	tags: ["autodocs"],
	argTypes: {},
};

export default meta;
type Story = StoryObj<typeof Header>;

export const Default: Story = {
	args: {
		isAuthenticated: false,
	},
};

export const Authenticated: Story = {
	args: {
		isAuthenticated: true,
		userName: "John Doe",
	},
};

export const AuthenticatedLongName: Story = {
	args: {
		isAuthenticated: true,
		userName: "John Doe with a Very Long Name",
	},
};
