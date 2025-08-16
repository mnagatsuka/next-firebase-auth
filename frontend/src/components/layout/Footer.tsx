export interface FooterProps {
  /** Optional site name to display in the footer */
  siteName?: string
  /** Optional copyright year */
  year?: number
}

export function Footer({ siteName = "Blog App", year = new Date().getFullYear() }: FooterProps) {
  return (
    <footer className="border-t bg-background py-4">
      <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
        &copy; {year} {siteName}. All rights reserved.
      </div>
    </footer>
  )
}
