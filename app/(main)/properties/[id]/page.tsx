import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";

import { getApiBaseUrl } from "@/lib/config";
import type { Listing, ListingSourceLink } from "@/lib/types/listing";
import { MOCK_LISTINGS } from "@/lib/mock/listings";
import { SCRAPED_LISTINGS } from "@/lib/mock/scraped-listings";
import { readScrapedListings } from "@/lib/server/scraped-listings";
import { PropertyDetailClient } from "./detail-client";

type Props = { params: Promise<{ id: string }> };
const FALLBACK_LISTINGS = SCRAPED_LISTINGS.length > 0 ? SCRAPED_LISTINGS : MOCK_LISTINGS;

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
    const decoded = decodeURIComponent(id);
    const scraped = await readScrapedListings();
    return scraped.find((l) => l.reference_id === decoded) ?? FALLBACK_LISTINGS.find((l) => l.reference_id === decoded) ?? null;
  }
}

async function fetchSimilar(listing: Listing): Promise<Listing[]> {
  const scraped = await readScrapedListings();
  const pool = scraped.length > 0 ? scraped : FALLBACK_LISTINGS;
  return pool.filter(
    (l) =>
      l.reference_id !== listing.reference_id &&
      (l.city === listing.city || l.region === listing.region) &&
      l.listing_intent === listing.listing_intent,
  ).slice(0, 4);
}

async function fetchSourceLinks(listing: Listing): Promise<ListingSourceLink[]> {
  const scraped = await readScrapedListings();
  const pool = scraped.length > 0 ? scraped : FALLBACK_LISTINGS;
  const candidates = pool.filter((candidate) => isSameMarketedProperty(listing, candidate));
  const withCurrent = candidates.some((candidate) => candidate.reference_id === listing.reference_id)
    ? candidates
    : [listing, ...candidates];

  const seen = new Set<string>();
  return withCurrent
    .map((candidate) => toSourceLink(listing, candidate))
    .filter((link) => {
      const key = `${link.source_key ?? link.source_name}:${link.listing_url}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return Boolean(link.listing_url);
    })
    .sort((a, b) => Number(b.is_current) - Number(a.is_current) || a.source_name.localeCompare(b.source_name));
}

function toSourceLink(base: Listing, candidate: Listing): ListingSourceLink {
  return {
    reference_id: candidate.reference_id,
    source_name: candidate.source_name,
    source_key: candidate.source_key,
    listing_url: candidate.listing_url,
    external_id: candidate.external_id,
    listing_intent: candidate.listing_intent,
    price: candidate.price,
    currency: candidate.currency,
    photo_count_remote: candidate.photo_count_remote ?? candidate.image_urls.length,
    photo_count_local: candidate.photo_count_local ?? candidate.local_image_files?.length ?? 0,
    full_gallery_downloaded: candidate.full_gallery_downloaded,
    evidence: sourceMatchEvidence(base, candidate),
    is_current: candidate.reference_id === base.reference_id,
  };
}

function isSameMarketedProperty(base: Listing, candidate: Listing): boolean {
  if (candidate.reference_id === base.reference_id) return true;
  if ((candidate.source_key ?? candidate.source_name) === (base.source_key ?? base.source_name)) return false;
  if (candidate.property_category !== base.property_category || candidate.listing_intent !== base.listing_intent) return false;

  const sameCity = sameText(base.city, candidate.city);
  const sameRegion = sameText(base.region, candidate.region);
  if (!sameCity && !sameRegion) return false;

  const areaMatch = closeNumber(base.area_sqm, candidate.area_sqm, 0.025, 2);
  const priceMatch = closeNumber(base.price, candidate.price, 0.035, 4000);
  const roomsMatch = base.rooms != null && candidate.rooms != null && Math.abs(base.rooms - candidate.rooms) <= 0.25;
  const strongTitleMatch = titleOverlap(base.title, candidate.title) >= 0.7;
  const exactAddressMatch = sameText(base.address_text, candidate.address_text) && Boolean(base.address_text && candidate.address_text);

  if (areaMatch && priceMatch && (roomsMatch || strongTitleMatch || exactAddressMatch)) return true;
  if (areaMatch && roomsMatch && strongTitleMatch) return true;
  if (priceMatch && roomsMatch && strongTitleMatch && exactAddressMatch) return true;

  return false;
}

function sourceMatchEvidence(base: Listing, candidate: Listing): string[] {
  if (candidate.reference_id === base.reference_id) return ["current source"];
  const evidence: string[] = [];
  if (sameText(base.city, candidate.city)) evidence.push("same city");
  if (sameText(base.district, candidate.district)) evidence.push("same district");
  if (closeNumber(base.area_sqm, candidate.area_sqm, 0.04, 4)) evidence.push("similar area");
  if (closeNumber(base.price, candidate.price, 0.06, 7000)) evidence.push("similar price");
  if (base.rooms != null && candidate.rooms != null && Math.abs(base.rooms - candidate.rooms) <= 0.25) evidence.push("same rooms");
  if (titleOverlap(base.title, candidate.title) >= 0.45) evidence.push("similar title");
  return evidence.slice(0, 4);
}

function closeNumber(a: number | null, b: number | null, percent: number, absolute: number): boolean {
  if (a == null || b == null || a <= 0 || b <= 0) return false;
  return Math.abs(a - b) <= Math.max(Math.max(a, b) * percent, absolute);
}

function sameText(a: string | null | undefined, b: string | null | undefined): boolean {
  const left = normalizeText(a);
  const right = normalizeText(b);
  return left.length > 0 && left === right;
}

function normalizeText(value: string | null | undefined): string {
  return String(value ?? "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim();
}

function titleOverlap(a: string | null | undefined, b: string | null | undefined): number {
  const left = new Set(normalizeText(a).split(" ").filter((token) => token.length > 3));
  const right = new Set(normalizeText(b).split(" ").filter((token) => token.length > 3));
  if (!left.size || !right.size) return 0;
  let shared = 0;
  for (const token of left) {
    if (right.has(token)) shared += 1;
  }
  return shared / Math.min(left.size, right.size);
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
  const sourceLinks = await fetchSourceLinks(listing);

  return <PropertyDetailClient listing={listing} similar={similar} sourceLinks={sourceLinks} />;
}
