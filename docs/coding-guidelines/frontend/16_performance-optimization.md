# 16. Performance Optimization

This section outlines the rules and best practices for optimizing performance in Next.js applications, focusing on Core Web Vitals, bundle optimization, and runtime performance.

## Goals

- **Improve Core Web Vitals**: Optimize LCP, FID, and CLS metrics
- **Bundle optimization**: Minimize JavaScript bundle size and loading time
- **Runtime performance**: Ensure smooth user interactions and fast rendering
- **Network efficiency**: Optimize API calls and resource loading
- **Memory management**: Prevent memory leaks and optimize resource usage

## 1. Core Web Vitals Optimization

### Largest Contentful Paint (LCP)

**Target: < 2.5 seconds**

```typescript
//  Good: Optimize images with Next.js Image component
import Image from 'next/image'

export function HeroSection() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero image"
      width={1200}
      height={600}
      priority // Load above-the-fold images with priority
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,..."
    />
  )
}

//  Good: Preload critical resources
export function Layout() {
  return (
    <>
      <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossOrigin="" />
      <link rel="preload" href="/api/critical-data" as="fetch" crossOrigin="" />
    </>
  )
}
```

### First Input Delay (FID)

**Target: < 100 milliseconds**

```typescript
//  Good: Use React.lazy for code splitting
import { lazy, Suspense } from 'react'

const HeavyComponent = lazy(() => import('@/components/HeavyComponent'))

export function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  )
}

//  Good: Debounce user inputs
import { useDebouncedCallback } from 'use-debounce'

export function SearchInput() {
  const debouncedSearch = useDebouncedCallback(
    (value: string) => {
      // Expensive search operation
    },
    300
  )

  return (
    <input
      onChange={(e) => debouncedSearch(e.target.value)}
      placeholder="Search..."
    />
  )
}
```

### Cumulative Layout Shift (CLS)

**Target: < 0.1**

```typescript
//  Good: Specify dimensions for media
<Image
  src="/image.jpg"
  alt="Description"
  width={400}
  height={300}
  style={{ width: '100%', height: 'auto' }}
/>

//  Good: Reserve space for dynamic content
export function UserProfile() {
  const { data: user, isLoading } = useUser()

  return (
    <div className="min-h-[100px]"> {/* Reserve minimum height */}
      {isLoading ? (
        <div className="h-16 w-16 bg-gray-200 rounded-full animate-pulse" />
      ) : (
        <div className="h-16 w-16">
          <Image src={user.avatar} alt={user.name} width={64} height={64} />
        </div>
      )}
    </div>
  )
}
```

## 2. Bundle Optimization

### Code Splitting

```typescript
//  Good: Route-based code splitting (automatic in App Router)
// app/dashboard/page.tsx - automatically split by Next.js

//  Good: Component-based code splitting
const Chart = lazy(() => import('@/components/Chart'))

//  Good: Third-party library splitting
const Editor = lazy(() => 
  import('@monaco-editor/react').then(module => ({
    default: module.Editor
  }))
)

//  Good: Conditional loading
export function AdminPanel() {
  const { user } = useAuth()
  
  if (!user?.isAdmin) return null
  
  // Only load admin components for admin users
  const AdminDashboard = lazy(() => import('@/components/AdminDashboard'))
  
  return (
    <Suspense fallback={<div>Loading admin panel...</div>}>
      <AdminDashboard />
    </Suspense>
  )
}
```

### Tree Shaking

```typescript
//  Good: Use named imports
import { format } from 'date-fns'
import { Button } from '@/components/ui/button'

// L Bad: Default imports that prevent tree shaking
import * as dateFns from 'date-fns'
import * as utils from '@/lib/utils'

//  Good: Configure barrel exports properly
// lib/utils/index.ts
export { formatDate } from './date'
export { validateEmail } from './validation'
// Don't re-export everything

// L Bad: Re-exporting everything
export * from './date'
export * from './validation'
```

### Bundle Analysis

```json
// package.json
{
  "scripts": {
    "analyze": "ANALYZE=true next build",
    "build:analyze": "next build && npx @next/bundle-analyzer"
  }
}
```

## 3. React Performance

### Memoization

```typescript
//  Good: Memoize expensive calculations
import { useMemo } from 'react'

export function DataTable({ data, filters }: DataTableProps) {
  const filteredData = useMemo(() => {
    return data.filter(item => 
      filters.every(filter => filter.apply(item))
    )
  }, [data, filters])

  return <Table data={filteredData} />
}

//  Good: Memoize components with stable props
import { memo } from 'react'

const ExpensiveComponent = memo(function ExpensiveComponent({ 
  data, 
  onSelect 
}: ExpensiveComponentProps) {
  // Complex rendering logic
})

//  Good: Use useCallback for event handlers
import { useCallback } from 'react'

export function ItemList({ items, onItemClick }: ItemListProps) {
  const handleClick = useCallback((id: string) => {
    onItemClick(id)
  }, [onItemClick])

  return (
    <div>
      {items.map(item => (
        <Item
          key={item.id}
          data={item}
          onClick={handleClick}
        />
      ))}
    </div>
  )
}
```

### Virtualization

```typescript
//  Good: Virtualize large lists
import { FixedSizeList as List } from 'react-window'

export function VirtualizedList({ items }: { items: Item[] }) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <ItemComponent data={items[index]} />
    </div>
  )

  return (
    <List
      height={600}
      itemCount={items.length}
      itemSize={60}
      width={400}
    >
      {Row}
    </List>
  )
}
```

## 4. Network Optimization

### API Optimization

```typescript
//  Good: Use React Query with proper caching
import { useQuery } from '@tanstack/react-query'

export function useUserData(userId: string) {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  })
}

//  Good: Prefetch data
export function UserList() {
  const queryClient = useQueryClient()
  
  const handleUserHover = (userId: string) => {
    queryClient.prefetchQuery({
      queryKey: ['user', userId],
      queryFn: () => fetchUser(userId),
    })
  }

  return (
    <div>
      {users.map(user => (
        <div
          key={user.id}
          onMouseEnter={() => handleUserHover(user.id)}
        >
          {user.name}
        </div>
      ))}
    </div>
  )
}
```

### Image Optimization

```typescript
//  Good: Responsive images with Next.js
import Image from 'next/image'

export function ResponsiveImage({ src, alt }: ImageProps) {
  return (
    <Image
      src={src}
      alt={alt}
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      style={{
        width: '100%',
        height: 'auto',
      }}
      width={800}
      height={600}
    />
  )
}

//  Good: Use appropriate image formats
// next.config.js
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
}
```

## 5. Loading States

### Progressive Loading

```typescript
//  Good: Show immediate feedback
export function DataComponent() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['data'],
    queryFn: fetchData,
  })

  if (error) return <ErrorState error={error} />
  
  return (
    <div>
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 rounded animate-pulse" />
          ))}
        </div>
      ) : (
        <div>
          {data?.map(item => (
            <DataItem key={item.id} data={item} />
          ))}
        </div>
      )}
    </div>
  )
}

//  Good: Skeleton UI components
export function PostSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
      <div className="h-32 bg-gray-200 rounded"></div>
    </div>
  )
}
```

## 6. Performance Monitoring

### Web Vitals Tracking

```typescript
// lib/analytics.ts
export function reportWebVitals({ id, name, value }: Metric) {
  // Send to analytics service
  gtag('event', name, {
    event_category: 'Web Vitals',
    value: Math.round(name === 'CLS' ? value * 1000 : value),
    event_label: id,
    non_interaction: true,
  })
}

// app/layout.tsx
import { reportWebVitals } from '@/lib/analytics'

export { reportWebVitals }
```

### Performance Budgets

```javascript
// next.config.js
module.exports = {
  experimental: {
    bundlePagesRouterDependencies: true,
  },
  // Set performance budgets
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      config.optimization.splitChunks.cacheGroups.vendor = {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendors',
        chunks: 'all',
        maxSize: 244000, // 244KB limit
      }
    }
    return config
  },
}
```

## 7. Best Practices Summary

### Must Rules

- **MUST** use Next.js Image component for all images
- **MUST** implement proper loading states for async operations
- **MUST** use React.memo for expensive components
- **MUST** specify dimensions for images and media
- **MUST** use code splitting for large components

### Should Rules

- **SHOULD** prefetch critical data and resources
- **SHOULD** use virtualization for large lists (>100 items)
- **SHOULD** implement skeleton UI for better perceived performance
- **SHOULD** monitor Core Web Vitals in production
- **SHOULD** use proper caching strategies

### Could Rules

- **COULD** implement service worker for offline functionality
- **COULD** use web workers for CPU-intensive tasks
- **COULD** implement advanced prefetching strategies
- **COULD** use performance profiler to identify bottlenecks

## 8. Troubleshooting

### Common Performance Issues

**Large Bundle Size**
```bash
# Analyze bundle
npm run analyze

# Check for duplicate dependencies
npx duplicate-package-checker-webpack-plugin
```

**Slow Rendering**
```typescript
// Use React DevTools Profiler
// Check for unnecessary re-renders
// Implement proper memoization
```

**Poor Core Web Vitals**
```bash
# Use Lighthouse CI
npx @lhci/cli@0.12.x autorun

# Check with PageSpeed Insights
# Monitor with Web Vitals extension
```

This performance optimization strategy ensures fast, responsive applications that provide excellent user experience while maintaining good Core Web Vitals scores.