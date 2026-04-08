import Link from "next/link";
import type { ReactNode } from "react";
import { SiteHeader } from "./SiteHeader";

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
      <SiteHeader />

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
          <span>&copy; 2026 BGEstate &middot; Every property. One search.</span>
          <Link href="/" className="text-sea hover:text-sea-bright font-medium">
            Home
          </Link>
        </div>
      </footer>
    </div>
  );
}
