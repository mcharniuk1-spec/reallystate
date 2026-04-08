import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";

import { getApiBaseUrl } from "@/lib/config";
import type { Listing } from "@/lib/types/listing";
import { MOCK_LISTINGS } from "@/lib/mock/listings";
import { PropertyDetailClient } from "./detail-client";

type Props = { params: Promise<{ id: string }> };

async function fetchListing(id: string): Promise<Listing | null> {
  const base = getApiBaseUrl();
  try {
    const res = await fetch(`${base}/listings/${id}`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });
    if (!res.ok) return null;
    const data = (await res.json()) as { item: Listing };
    return data.item;
  } catch {
    return MOCK_LISTINGS.find((l) => l.reference_id === id) ?? null;
  }
}

async function fetchSimilar(listing: Listing): Promise<Listing[]> {
  return MOCK_LISTINGS.filter(
    (l) =>
      l.reference_id !== listing.reference_id &&
      (l.city === listing.city || l.region === listing.region) &&
      l.listing_intent === listing.listing_intent,
  ).slice(0, 4);
}

function fmt(price: number | null, currency: string | null, intent: string): string {
  if (price == null) return "Price on request";
  const sym = currency === "EUR" ? "\u20AC" : currency === "BGN" ? "BGN " : `${currency ?? ""} `;
  const suffix = intent === "rent" || intent === "short_term_rental" ? "/mo" : "";
  return `${sym}${new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(price)}${suffix}`;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const listing = await fetchListing(id);
  if (!listing) return { title: "Property not found" };
  const location = [listing.district, listing.city].filter(Boolean).join(", ");
  return {
    title: `${fmt(listing.price, listing.currency, listing.listing_intent)} — ${location || "Bulgaria"}`,
    description: listing.description?.slice(0, 160) ?? undefined,
  };
}

export default async function PropertyDetailPage({ params }: Props) {
  const { id } = await params;
  if (!id) notFound();

  const listing = await fetchListing(id);

  if (!listing) {
    return (
      <div className="min-h-screen flex flex-col">
        <header className="shrink-0 border-b border-line bg-panel/90 backdrop-blur-md sticky top-0 z-30">
          <div className="flex items-center gap-4 px-4 py-2.5 sm:px-6">
            <Link href="/" className="font-display text-lg tracking-tight text-ink">
              BG<span className="text-sea">Estate</span>
            </Link>
          </div>
        </header>
        <main className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <p className="font-display text-3xl text-ink">Property not found</p>
            <p className="mt-3 text-mist">
              ID <code className="bg-paper px-1 rounded text-ink">{id}</code> does not exist or the API is unreachable.
            </p>
            <Link
              href="/"
              className="mt-6 inline-flex rounded-full bg-sea px-5 py-2.5 text-sm font-semibold text-white hover:bg-sea-bright"
            >
              Back to listings
            </Link>
          </div>
        </main>
      </div>
    );
  }

  const similar = await fetchSimilar(listing);

  return <PropertyDetailClient listing={listing} similar={similar} />;
}
