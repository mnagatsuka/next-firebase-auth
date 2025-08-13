import Link from "next/link"

export interface FooterProps {
  /** Copyright year */
  year?: number
  /** Site name or company name */
  siteName?: string
}

export function Footer({ 
  year = new Date().getFullYear(),
  siteName = "Blog App"
}: FooterProps) {
  return (
    <footer className="border-t bg-background mt-auto">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="font-bold text-lg mb-4">{siteName}</h3>
            <p className="text-sm text-muted-foreground">
              A simple blog application built with Next.js and modern web technologies.
            </p>
          </div>
          
          <div>
            <h4 className="font-medium mb-4">Quick Links</h4>
            <nav className="space-y-2">
              <Link 
                href="/" 
                className="block text-sm text-muted-foreground hover:text-foreground"
              >
                Home
              </Link>
              <Link 
                href="/create-post" 
                className="block text-sm text-muted-foreground hover:text-foreground"
              >
                Create Post
              </Link>
            </nav>
          </div>
          
          <div>
            <h4 className="font-medium mb-4">About</h4>
            <p className="text-sm text-muted-foreground">
              This is a demo blog application showcasing Server-Side Rendering and 
              Client-Side Rendering with Next.js.
            </p>
          </div>
        </div>
        
        <div className="border-t mt-8 pt-8 text-center">
          <p className="text-sm text-muted-foreground">
            © {year} {siteName}. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}