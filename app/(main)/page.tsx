import type { Metadata } from "next";

import { ListingFeed } from "@/components/listings/ListingFeed";
import { SiteHeader } from "@/components/shell/SiteHeader";

export const metadata: Metadata = {
  title: "Browse properties · BGEstate",
  description: "Every property in Bulgaria. One search. Interactive map.",
};

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <SiteHeader />
      <ListingFeed />
    </div>
  );
}
