import Link from "next/link";
import type { ReactNode } from "react";

const nav = [
  { href: "/listings", label: "Listings" },
  { href: "/map", label: "Map" },
  { href: "/chat", label: "Chat" },
  { href: "/settings", label: "Settings" },
  { href: "/admin", label: "Admin" },
] as const;

export function AppShell({
  children,
  title,
  subtitle,
}: {
  children: ReactNode;
  title?: string;
  subtitle?: string;
}) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-line bg-panel/90 backdrop-blur-md sticky top-0 z-30">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <div className="flex items-center gap-6">
            <Link href="/" className="font-display text-xl tracking-tight text-ink">
              BG<span className="text-sea">Estate</span>
            </Link>
            <nav className="hidden md:flex flex-wrap gap-1" aria-label="Primary">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-full px-3 py-1.5 text-sm font-medium text-mist hover:bg-paper hover:text-ink transition-colors"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline text-xs text-mist uppercase tracking-wider">Operator</span>
            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-sea to-sea-bright ring-2 ring-white shadow-lift" />
          </div>
        </div>
        <div className="border-t border-line/60 md:hidden overflow-x-auto">
          <nav className="flex gap-1 px-4 py-2" aria-label="Primary mobile">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="shrink-0 rounded-full px-3 py-1.5 text-sm font-medium text-mist hover:bg-paper hover:text-ink"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      {(title || subtitle) && (
        <div className="border-b border-line bg-panel">
          <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
            {title && (
              <h1 className="font-display text-4xl sm:text-5xl tracking-tight text-balance text-ink">{title}</h1>
            )}
            {subtitle && <p className="mt-3 max-w-2xl text-lg text-mist leading-relaxed">{subtitle}</p>}
          </div>
        </div>
      )}

      <main className="flex-1 mx-auto w-full max-w-6xl px-4 py-10 sm:px-6">{children}</main>

      <footer className="border-t border-line bg-panel mt-auto">
        <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 text-sm text-mist flex flex-wrap gap-4 justify-between">
          <span>Source registry and compliance gates drive what appears here.</span>
          <Link href="/" className="text-sea hover:text-sea-bright font-medium">
            Home
          </Link>
        </div>
      </footer>
    </div>
  );
}
