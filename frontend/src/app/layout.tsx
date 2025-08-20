import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { PageTransition } from "@/components/ui/PageTransition";
import { MswProvider } from "@/lib/providers/MswProvider";
import { QueryProvider } from "@/lib/providers/QueryProvider";

export const runtime = "nodejs"; // SSRモックを有効にする場合

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
	title: {
		template: "%s | Blog App",
		default: "Blog App",
	},
	description: "A modern blog application built with Next.js and Firebase Auth",
	keywords: ["blog", "nextjs", "firebase", "typescript"],
	authors: [{ name: "Blog App Team" }],
	viewport: "width=device-width, initial-scale=1",
	robots: "index, follow",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
	return (
		<html lang="en">
			<body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
				<ErrorBoundary>
					<MswProvider>
						<QueryProvider>
							<AuthProvider>
								<div className="flex flex-col min-h-screen">
									<Header />
									<main className="flex-grow container mx-auto px-4 py-8">
										<PageTransition>{children}</PageTransition>
									</main>
									<Footer />
								</div>
								<Toaster />
							</AuthProvider>
						</QueryProvider>
					</MswProvider>
				</ErrorBoundary>
			</body>
		</html>
	);
}
