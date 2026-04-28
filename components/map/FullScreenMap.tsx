"use client";

import { MOCK_LISTINGS } from "@/lib/mock/listings";
import { SCRAPED_LISTINGS } from "@/lib/mock/scraped-listings";
import { MapCanvas } from "./MapCanvas";
import { SiteHeader } from "@/components/shell/SiteHeader";

export function FullScreenMap() {
  const listings = SCRAPED_LISTINGS.length > 0 ? SCRAPED_LISTINGS : MOCK_LISTINGS;

  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      <div className="flex-1">
        <MapCanvas listings={listings} />
      </div>
    </div>
  );
}
