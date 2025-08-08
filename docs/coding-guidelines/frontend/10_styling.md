# 10. Styling & Assets

This section defines the rules and best practices for styling and managing assets in Next.js projects using **Tailwind CSS**, **shadcn/ui**, `next/font`, and `next/image`.

Our goals are:
- Maintain a consistent and scalable design system
- Use utility-first styling with Tailwind CSS
- Leverage shadcn/ui for accessible, reusable UI components
- Optimize fonts and images for performance


## 1. Styling with Tailwind CSS

We use [Tailwind CSS](https://tailwindcss.com/) for utility-first styling to ensure speed and consistency.

**Rules:**
- Use Tailwind utility classes for most styling.
- Avoid excessive custom CSS unless required for unique layouts.
- Use responsive classes (`sm:`, `md:`, `lg:`, `xl:`) for breakpoints.
- Use `@apply` in `.css` files sparingly, mainly for global styles.

**Example:**

```tsx
export default function Button() {
  return (
    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
      Click me
    </button>
  )
}
````


## 2. Using shadcn/ui

We use [shadcn/ui](https://ui.shadcn.com/) for accessible, unstyled components built with Tailwind.

**Rules:**

* Customize components via Tailwind classes, not by modifying the core library files.
* Keep component overrides in `/components/ui/` to maintain a consistent design system.
* Use composition to extend components instead of duplicating code.

**Example:**

```tsx
import { Button } from '@/components/ui/button'

export default function App() {
  return <Button variant="default">Submit</Button>
}
```


## 3. Fonts with `next/font`

We use [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) for self-hosted fonts to avoid layout shift and improve performance.

**Rules:**

* Prefer `next/font/local` for self-hosted fonts.
* Store font files in `/public/fonts`.
* Define fonts in a shared file and reuse across the app.

**Example:**

```ts
// src/lib/fonts.ts
import localFont from 'next/font/local'

export const myFont = localFont({
  src: '../public/fonts/MyFont.woff2',
  display: 'swap',
  weight: '400 700'
})
```

```tsx
// layout.tsx
import { myFont } from '@/lib/fonts'

export default function RootLayout({ children }) {
  return <body className={myFont.className}>{children}</body>
}
```


## 4. Image Optimization with `next/image`

We use [`next/image`](https://nextjs.org/docs/app/building-your-application/optimizing/images) for optimized, responsive images.

**Rules:**

* Always provide `alt` text for accessibility.
* Use `fill` for responsive layouts and `width/height` for fixed-size images.
* Store static images in `/public/images`.
* Use `priority` for above-the-fold images.

**Example:**

```tsx
import Image from 'next/image'

export default function Hero() {
  return (
    <Image
      src="/images/hero.jpg"
      alt="Hero banner"
      width={1200}
      height={600}
      priority
    />
  )
}
```


## 5. Global Styles

* Define global CSS in `src/styles/globals.css`.
* Keep global styles minimal — rely on Tailwind utilities for most styling.
* Use CSS variables for theme tokens (colors, spacing) when needed.


By following these rules, we ensure our applications are **visually consistent, accessible, and performant** while maintaining a scalable and maintainable styling system.
