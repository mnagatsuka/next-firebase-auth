# 9. Metadata, SEO & Accessibility

This section defines the rules and best practices for setting metadata, optimizing SEO, and improving accessibility (a11y) in Next.js projects using the **App Router**.

Our goals are:
- Use the Next.js Metadata API for consistent and type-safe metadata
- Ensure all pages have appropriate titles and descriptions
- Support Open Graph (OG) and Twitter cards for social sharing
- Improve accessibility for users relying on assistive technologies
- Manage robots.txt and sitemap.xml for search engine visibility


## 1. Metadata API Usage

Next.js provides a built-in [Metadata API](https://nextjs.org/docs/app/building-your-application/optimizing/metadata) for setting SEO and accessibility-friendly metadata in the App Router.

**Rules:**
- Use the `metadata` export for **static** metadata.
- Use the `generateMetadata` function for **dynamic** metadata.
- Always provide `title` and `description`.
- Set the `lang` attribute in metadata (for correct screen reader pronunciation).
- Ensure that descriptions are concise, meaningful, and human-readable.

**Example (Static Metadata):**

```ts
// src/app/page.tsx
export const metadata = {
  title: 'Home | MyApp',
  description: 'Welcome to MyApp, the best app for managing your projects.',
  metadataBase: new URL('https://example.com'),
  alternates: { canonical: '/' },
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#ffffff',
  manifest: '/manifest.json'
}
````

**Example (Dynamic Metadata):**

```ts
// src/app/posts/[id]/page.tsx
import { getPost } from '@/lib/posts'

export async function generateMetadata({ params }) {
  const post = await getPost(params.id)
  return {
    title: `${post.title} | MyApp`,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [
        {
          url: post.ogImage,
          alt: `${post.title} - Featured Image`
        }
      ]
    }
  }
}
```


## 2. Open Graph & Twitter Card Support

* Always set `openGraph` and `twitter` metadata for pages intended for sharing on social platforms.
* Use descriptive `alt` text for OG/Twitter images for accessibility.
* Ensure images have correct aspect ratios (1200x630 for OG).

**Example:**

```ts
export const metadata = {
  title: 'Product Page',
  description: 'Details about our amazing product.',
  openGraph: {
    title: 'Product Page',
    description: 'Details about our amazing product.',
    url: 'https://example.com/product',
    siteName: 'MyApp',
    images: [
      {
        url: 'https://example.com/images/product-og.png',
        width: 1200,
        height: 630,
        alt: 'Front view of our amazing product'
      }
    ],
    type: 'website',
    locale: 'en_US'
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Product Page',
    description: 'Details about our amazing product.',
    images: ['https://example.com/images/product-og.png']
  }
}
```


## 3. Dynamic OG/Twitter Image Generation

* Use Next.js’ [Image Response API](https://nextjs.org/docs/app/api-reference/functions/image-response) for dynamic OG/Twitter images.
* Ensure generated images contain high-contrast text and clear visuals for accessibility.
* Place image generation logic in `/src/app/api/og/route.ts` or similar.

**Example:**

```ts
// src/app/api/og/route.ts
import { ImageResponse } from 'next/server'

export const runtime = 'edge'

export async function GET() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 60,
          color: 'white',
          background: 'black',
          padding: '50px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
        role="img"
        aria-label="My Dynamic OG Image for MyApp"
      >
        My Dynamic OG Image
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
```


## 4. robots.txt and sitemap.xml

* Place `robots.txt` and `sitemap.xml` in the `/public` directory so they are served at the root.
* Ensure that `robots.txt` allows crawling for public pages and blocks sensitive routes.
* Update `sitemap.xml` automatically in CI/CD if pages are added frequently.

**Example robots.txt:**

```
User-agent: *
Allow: /
Disallow: /admin
Sitemap: https://example.com/sitemap.xml
```


## 5. SEO & Accessibility Best Practices

### SEO

* Each page should have a **unique** `title` and `description`.
* Use **semantic HTML** (`<h1>` for page title, `<h2>` for sections).
* Avoid duplicate content across pages.
* Use `next/image` for optimized images with meaningful `alt` attributes.
* Test SEO performance with **Lighthouse** and fix issues before deployment.

### Accessibility (a11y)

* Ensure `lang` is set in metadata (`lang="en"` or project language).
* Provide descriptive `alt` text for all images, including OG/Twitter.
* Ensure color contrast meets WCAG AA standards.
* Use clear and descriptive page titles — avoid generic titles like "Home" without context.
* Test with accessibility tools (e.g., axe-core, Lighthouse a11y audit).


By following these rules, we ensure our Next.js applications are **discoverable, shareable, and accessible**, meeting both SEO and accessibility standards for a better user experience.
