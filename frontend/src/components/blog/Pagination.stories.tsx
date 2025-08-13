import type { Meta, StoryObj } from '@storybook/nextjs-vite'
import { Pagination } from './Pagination'

const meta: Meta<typeof Pagination> = {
  title: 'Blog/Pagination',
  component: Pagination,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    onPageChange: { action: 'page-changed' },
  },
}

export default meta
type Story = StoryObj<typeof Pagination>

export const FirstPage: Story = {
  args: {
    currentPage: 1,
    totalPages: 10,
    hasNext: true,
    hasPrevious: false,
  },
}

export const MiddlePage: Story = {
  args: {
    currentPage: 5,
    totalPages: 10,
    hasNext: true,
    hasPrevious: true,
  },
}

export const LastPage: Story = {
  args: {
    currentPage: 10,
    totalPages: 10,
    hasNext: false,
    hasPrevious: true,
  },
}

export const FewPages: Story = {
  args: {
    currentPage: 2,
    totalPages: 3,
    hasNext: true,
    hasPrevious: true,
  },
}

export const SinglePage: Story = {
  args: {
    currentPage: 1,
    totalPages: 1,
    hasNext: false,
    hasPrevious: false,
  },
}

export const ManyPages: Story = {
  args: {
    currentPage: 15,
    totalPages: 50,
    hasNext: true,
    hasPrevious: true,
  },
}