import Link from "next/link";
import { HeaderAuth } from "./HeaderAuth";

export function Header() {
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

					<Link href="/my/posts" className="text-sm font-medium hover:underline">
						My Posts
					</Link>

					<HeaderAuth />
				</nav>
			</div>
		</header>
	);
}
