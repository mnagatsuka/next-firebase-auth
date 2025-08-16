/**
 * Safe date formatting utilities that work consistently on server and client
 */

/**
 * Format date for server-side rendering (consistent format)
 */
export function formatDateSSR(dateString: string): string {
  const date = new Date(dateString)
  return date.toISOString().split('T')[0] || '' // YYYY-MM-DD format
}

/**
 * Format date for blog post display (server-safe)
 */
export function formatBlogPostDate(dateString: string): string {
  const date = new Date(dateString)
  
  // Use a consistent format that works on both server and client
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]
  
  return `${months[date.getUTCMonth()]} ${date.getUTCDate()}, ${date.getUTCFullYear()}`
}