"use client";

import { MOCK_LISTINGS } from "@/lib/mock/listings";
import { MapCanvas } from "./MapCanvas";
import { SiteHeader } from "@/components/shell/SiteHeader";

export function FullScreenMap() {
  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      <div className="flex-1">
        <MapCanvas listings={MOCK_LISTINGS} />
      </div>
    </div>
  );
}
