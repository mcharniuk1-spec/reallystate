"use client";

import Link from "next/link";
import { MOCK_LISTINGS } from "@/lib/mock/listings";
import { MapCanvas } from "./MapCanvas";

export function FullScreenMap() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="shrink-0 border-b border-line bg-panel/90 backdrop-blur-md sticky top-0 z-30">
        <div className="flex items-center justify-between gap-4 px-4 py-2.5 sm:px-6">
          <div className="flex items-center gap-5">
            <Link href="/" className="font-display text-lg tracking-tight text-ink">
              BG<span className="text-sea">Estate</span>
            </Link>
            <span className="text-xs font-semibold text-mist">Full map view</span>
          </div>
          <Link
            href="/"
            className="rounded-full border border-line px-3 py-1 text-xs font-semibold text-ink hover:border-sea/30"
          >
            Back to listings
          </Link>
        </div>
      </header>
      <div className="flex-1">
        <MapCanvas listings={MOCK_LISTINGS} />
      </div>
    </div>
  );
}
