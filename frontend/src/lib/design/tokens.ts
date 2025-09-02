/**
 * Design tokens for consistent spacing, colors, and typography
 */

// Spacing tokens
export const spacing = {
  xs: '0.25rem',      // 4px
  sm: '0.5rem',       // 8px
  md: '1rem',         // 16px
  lg: '1.5rem',       // 24px
  xl: '2rem',         // 32px
  '2xl': '3rem',      // 48px
  '3xl': '4rem',      // 64px
} as const;

// Layout constants
export const layout = {
  containerMaxWidth: '1200px',
  headerHeight: '4rem',
  sidebarWidth: '16rem',
  contentPadding: spacing.lg,
  borderRadius: {
    sm: '0.25rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
  }
} as const;

// Animation durations
export const animation = {
  fast: '150ms',
  normal: '300ms',
  slow: '500ms',
} as const;

// Z-index scale
export const zIndex = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modal: 1040,
  popover: 1050,
  tooltip: 1060,
  toast: 1070,
} as const;

// Breakpoints (matching Tailwind defaults)
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// Common class combinations
export const classNames = {
  // Layout
  container: 'container mx-auto px-4',
  flexCenter: 'flex items-center justify-center',
  flexBetween: 'flex items-center justify-between',
  
  // Text
  textMuted: 'text-muted-foreground',
  textError: 'text-destructive',
  textSuccess: 'text-green-600',
  
  // Spacing
  section: 'space-y-12',
  sectionSmall: 'space-y-8',
  stack: 'space-y-4',
  stackSmall: 'space-y-2',
  
  // Cards and surfaces
  card: 'rounded-lg border bg-card text-card-foreground shadow-sm',
  cardContent: 'p-6',
  cardHeader: 'flex flex-col space-y-1.5 p-6',
  
  // Forms
  formField: 'space-y-2',
  formRow: 'grid grid-cols-1 gap-4 md:grid-cols-2',
  
  // States
  loading: 'animate-pulse',
  disabled: 'opacity-50 cursor-not-allowed',
} as const;

// Grid layouts
export const gridLayouts = {
  posts: 'grid gap-6 md:grid-cols-2',
  postsThree: 'grid gap-6 md:grid-cols-2 lg:grid-cols-3',
  dashboard: 'grid gap-6 md:grid-cols-2 lg:grid-cols-3',
  form: 'grid gap-4',
  formWide: 'grid gap-4 md:grid-cols-2',
} as const;

export type SpacingToken = keyof typeof spacing;
export type ClassNameToken = keyof typeof classNames;
export type GridLayoutToken = keyof typeof gridLayouts;