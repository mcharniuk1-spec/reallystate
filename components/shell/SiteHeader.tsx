"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Browse", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
  { href: "/chat", label: "Chat", icon: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" },
  { href: "/admin", label: "Admin", icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z" },
] as const;

export function SiteHeader() {
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <header className="shrink-0 border-b border-line bg-panel/90 backdrop-blur-md sticky top-0 z-40">
      <div className="flex items-center justify-between gap-4 px-4 py-2.5 sm:px-6 max-w-[1920px] mx-auto">
        {/* Left: logo + desktop nav */}
        <div className="flex items-center gap-5">
          <Link href="/" className="font-display text-lg tracking-tight text-ink shrink-0">
            BG<span className="text-sea">Estate</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden sm:flex gap-1" aria-label="Primary">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-full px-3 py-1 text-xs font-semibold transition-colors ${
                  isActive(item.href)
                    ? "bg-sea/10 border border-sea/20 text-sea"
                    : "text-mist hover:bg-paper hover:text-ink"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Right: beta badge + avatar + hamburger */}
        <div className="flex items-center gap-3">
          <span className="hidden sm:inline text-[10px] text-mist uppercase tracking-wider font-semibold">
            Beta
          </span>

          {/* Avatar / user button */}
          <button
            type="button"
            className="hidden sm:flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-sea to-sea-bright ring-2 ring-white shadow-sm text-white text-xs font-bold"
            title="Account (coming soon)"
          >
            U
          </button>

          {/* Mobile hamburger */}
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="sm:hidden flex items-center justify-center h-8 w-8 rounded-lg text-mist hover:text-ink hover:bg-paper transition-colors"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
          >
            {menuOpen ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Mobile slide-down menu */}
      {menuOpen && (
        <div className="sm:hidden border-t border-line bg-panel/95 backdrop-blur-md">
          <nav className="px-4 py-3 space-y-1" aria-label="Mobile">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMenuOpen(false)}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive(item.href)
                    ? "bg-sea/10 text-sea"
                    : "text-mist hover:bg-paper hover:text-ink"
                }`}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d={item.icon} />
                </svg>
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="px-4 pb-3 pt-1 border-t border-line/50">
            <div className="flex items-center gap-3 rounded-xl px-3 py-2.5">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-sea to-sea-bright flex items-center justify-center text-white text-xs font-bold">
                U
              </div>
              <div>
                <p className="text-sm font-medium text-ink">Sign in</p>
                <p className="text-[11px] text-mist">Save searches, get alerts</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
