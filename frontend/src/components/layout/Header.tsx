import Link from "next/link"
import { Button } from "@/components/ui/button"

export interface HeaderProps {
  /** Whether user is authenticated */
  isAuthenticated?: boolean
  /** User's display name if authenticated */
  userName?: string
  /** Callback for sign out action */
  onSignOut?: () => void
}

export function Header({ 
  isAuthenticated = false, 
  userName,
  onSignOut 
}: HeaderProps) {
  return (
    <header className="border-b bg-background">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center space-x-4">
          <Link href="/" className="text-xl font-bold">
            Blog App
          </Link>
        </div>
        
        <nav className="flex items-center space-x-4">
          <Link href="/" className="text-sm font-medium hover:underline">
            Home
          </Link>
          
          {isAuthenticated ? (
            <>
              <Link href="/create-post" className="text-sm font-medium hover:underline">
                Create Post
              </Link>
              <div className="flex items-center space-x-2">
                <span className="text-sm">Welcome, {userName}</span>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={onSignOut}
                >
                  Sign Out
                </Button>
              </div>
            </>
          ) : (
            <Button variant="default" size="sm">
              Sign In
            </Button>
          )}
        </nav>
      </div>
    </header>
  )
}