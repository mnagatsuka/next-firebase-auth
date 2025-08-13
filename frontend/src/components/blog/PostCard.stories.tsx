import type { Meta, StoryObj } from '@storybook/nextjs-vite'
import { PostCard } from './PostCard'

const meta: Meta<typeof PostCard> = {
  title: 'Blog/PostCard',
  component: PostCard,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    onReadMore: { action: 'read-more-clicked' },
  },
}

export default meta
type Story = StoryObj<typeof PostCard>

export const Default: Story = {
  args: {
    id: '1',
    title: 'Getting Started with Next.js',
    excerpt: 'Learn the basics of Next.js in this comprehensive guide covering SSR, SSG, and CSR.',
    author: 'John Doe',
    publishedAt: '2024-01-15T10:30:00Z',
    tags: ['Next.js', 'React', 'TypeScript'],
  },
}

export const LongTitle: Story = {
  args: {
    id: '2',
    title: 'A Very Long Blog Post Title That Might Wrap to Multiple Lines and Should Be Handled Gracefully',
    excerpt: 'This post has a very long title to test how the card handles text overflow and wrapping.',
    author: 'Jane Smith',
    publishedAt: '2024-01-14T09:15:00Z',
    tags: ['UI', 'Design'],
  },
}

export const LongExcerpt: Story = {
  args: {
    id: '3',
    title: 'Short Title',
    excerpt: 'This is a very long excerpt that should be truncated with line-clamp. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.',
    author: 'Bob Johnson',
    publishedAt: '2024-01-13T14:45:00Z',
    tags: ['Content', 'Writing'],
  },
}

export const ManyTags: Story = {
  args: {
    id: '4',
    title: 'Post with Many Tags',
    excerpt: 'This post demonstrates how the card handles multiple tags.',
    author: 'Alice Wilson',
    publishedAt: '2024-01-12T16:20:00Z',
    tags: ['React', 'Next.js', 'TypeScript', 'Tailwind', 'Storybook', 'Testing', 'Development'],
  },
}

export const NoTags: Story = {
  args: {
    id: '5',
    title: 'Post Without Tags',
    excerpt: 'This post has no tags to show how the card looks without any tags.',
    author: 'Charlie Brown',
    publishedAt: '2024-01-11T08:30:00Z',
    tags: [],
  },
}