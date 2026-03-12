import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "OpenClaw Skill Store",
  description: "The best marketplace for OpenClaw AI agent skills",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-gray-50`}>
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <div className="flex-shrink-0 flex items-center gap-2">
                  <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-xl">⚡</span>
                  </div>
                  <span className="text-xl font-bold text-gray-900">OpenClaw Skill Store</span>
                </div>
                <nav className="hidden md:ml-10 md:flex md:space-x-8">
                  <a href="/" className="text-gray-900 font-medium hover:text-primary-600">
                    Explore
                  </a>
                  <a href="/categories" className="text-gray-500 font-medium hover:text-primary-600">
                    Categories
                  </a>
                  <a href="/trending" className="text-gray-500 font-medium hover:text-primary-600">
                    Trending
                  </a>
                  <a href="/workflows" className="text-gray-500 font-medium hover:text-primary-600">
                    Workflows
                  </a>
                </nav>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-72">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Search skills..."
                      className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
                    />
                    <div className="absolute left-3 top-2.5 text-gray-400">
                      🔍
                    </div>
                  </div>
                </div>
                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-primary-700 transition-colors">
                  Submit Skill
                </button>
              </div>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="bg-white border-t border-gray-200 mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center">
              <div className="text-gray-500 text-sm">
                © 2026 OpenClaw Skill Store. All rights reserved.
              </div>
              <div className="flex gap-6">
                <a href="#" className="text-gray-500 hover:text-gray-900 text-sm">
                  Documentation
                </a>
                <a href="#" className="text-gray-500 hover:text-gray-900 text-sm">
                  GitHub
                </a>
                <a href="#" className="text-gray-500 hover:text-gray-900 text-sm">
                  Security
                </a>
                <a href="#" className="text-gray-500 hover:text-gray-900 text-sm">
                  Terms
                </a>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
