import type { Metadata } from "next";
import Link from "next/link";

import { ListingFeed } from "@/components/listings/ListingFeed";

export const metadata: Metadata = {
  title: "Browse properties · Bulgaria Real Estate",
};

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Compact nav header */}
      <header className="shrink-0 border-b border-line bg-panel/90 backdrop-blur-md sticky top-0 z-30">
        <div className="flex items-center justify-between gap-4 px-4 py-2.5 sm:px-6">
          <div className="flex items-center gap-5">
            <Link href="/" className="font-display text-lg tracking-tight text-ink">
              BG<span className="text-sea">Estate</span>
            </Link>
            <nav className="hidden sm:flex gap-1" aria-label="Primary">
              <Link
                href="/"
                className="rounded-full bg-sea/10 border border-sea/20 px-3 py-1 text-xs font-semibold text-sea"
              >
                Browse
              </Link>
              <Link
                href="/map"
                className="rounded-full px-3 py-1 text-xs font-medium text-mist hover:bg-paper hover:text-ink transition-colors"
              >
                Full map
              </Link>
              <Link
                href="/chat"
                className="rounded-full px-3 py-1 text-xs font-medium text-mist hover:bg-paper hover:text-ink transition-colors"
              >
                Chat
              </Link>
              <Link
                href="/admin"
                className="rounded-full px-3 py-1 text-xs font-medium text-mist hover:bg-paper hover:text-ink transition-colors"
              >
                Admin
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline text-[10px] text-mist uppercase tracking-wider">Beta</span>
            <div className="h-7 w-7 rounded-full bg-gradient-to-br from-sea to-sea-bright ring-2 ring-white shadow-sm" />
          </div>
        </div>
      </header>

      {/* Full-bleed listing + map split */}
      <ListingFeed />
    </div>
  );
}
