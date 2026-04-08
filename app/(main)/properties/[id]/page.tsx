import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";

import { getApiBaseUrl } from "@/lib/config";
import type { Listing } from "@/lib/types/listing";
import { MOCK_LISTINGS } from "@/lib/mock/listings";

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
              ID <code className="bg-paper px-1 rounded text-ink">{id}</code> does not exist or the API
              is unreachable.
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

  const l = listing;
  const location = [l.district, l.city].filter(Boolean).join(", ") || l.region || "Bulgaria";

  return (
    <div className="min-h-screen flex flex-col bg-paper">
      {/* Header */}
      <header className="shrink-0 border-b border-line bg-panel/90 backdrop-blur-md sticky top-0 z-30">
        <div className="flex items-center justify-between gap-4 px-4 py-2.5 sm:px-6">
          <div className="flex items-center gap-4">
            <Link href="/" className="font-display text-lg tracking-tight text-ink">
              BG<span className="text-sea">Estate</span>
            </Link>
            <span className="hidden sm:inline text-xs text-mist">/</span>
            <span className="hidden sm:inline text-xs text-mist truncate max-w-[200px]">{location}</span>
          </div>
          <Link
            href="/"
            className="rounded-full border border-line px-3 py-1 text-xs font-semibold text-ink hover:border-sea/30"
          >
            Back to listings
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 mx-auto w-full max-w-5xl px-4 py-8 sm:px-6">
        <div className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr]">
          {/* Left: gallery + description */}
          <div className="space-y-6">
            {/* Photo gallery placeholder */}
            <div className="aspect-[16/10] rounded-3xl border border-line bg-gradient-to-br from-panel to-line/30 shadow-inner flex items-center justify-center overflow-hidden">
              {l.image_urls.length > 0 ? (
                <img src={l.image_urls[0]} alt="" className="w-full h-full object-cover" />
              ) : (
                <div className="text-center px-8">
                  <p className="text-xs font-medium text-mist/60 uppercase tracking-wider">
                    {l.source_name}
                  </p>
                  <p className="mt-1 text-[10px] text-mist/40">Photo pipeline not yet connected</p>
                </div>
              )}
            </div>

            {/* Description */}
            {l.description && (
              <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
                <h2 className="text-xs font-semibold uppercase tracking-wide text-mist">Description</h2>
                <p className="mt-3 text-sm text-ink leading-relaxed whitespace-pre-line">{l.description}</p>
              </div>
            )}

            {/* Source provenance */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-mist">Source</h2>
              <dl className="mt-3 grid grid-cols-2 gap-3 text-sm">
                <div>
                  <dt className="text-xs text-mist">Portal</dt>
                  <dd className="font-medium text-ink">{l.source_name}</dd>
                </div>
                <div>
                  <dt className="text-xs text-mist">External ID</dt>
                  <dd className="font-mono text-ink text-xs">{l.external_id}</dd>
                </div>
                <div className="col-span-2">
                  <dt className="text-xs text-mist">Source URL</dt>
                  <dd className="truncate">
                    <a
                      href={l.listing_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sea hover:text-sea-bright text-xs"
                    >
                      {l.listing_url}
                    </a>
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          {/* Right: price + facts + actions */}
          <div className="space-y-5">
            {/* Price box */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
              <p className="font-display text-3xl text-ink tracking-tight">
                {fmt(l.price, l.currency, l.listing_intent)}
              </p>
              <p className="mt-1 text-sm text-mist capitalize">{l.listing_intent.replace(/_/g, " ")}</p>
              {l.area_sqm != null && l.price != null && (
                <p className="mt-2 text-xs text-mist">
                  {"\u20AC"}
                  {new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(
                    Math.round(l.price / l.area_sqm),
                  )}
                  /m\u00B2
                </p>
              )}
            </div>

            {/* Facts grid */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-mist">Details</h2>
              <dl className="mt-3 grid grid-cols-2 gap-y-3 gap-x-4 text-sm">
                {l.property_category && (
                  <div>
                    <dt className="text-xs text-mist">Type</dt>
                    <dd className="font-medium text-ink capitalize">{l.property_category}</dd>
                  </div>
                )}
                {l.area_sqm != null && (
                  <div>
                    <dt className="text-xs text-mist">Area</dt>
                    <dd className="font-medium text-ink">{l.area_sqm} m{"\u00B2"}</dd>
                  </div>
                )}
                {l.rooms != null && (
                  <div>
                    <dt className="text-xs text-mist">Rooms</dt>
                    <dd className="font-medium text-ink">{l.rooms}</dd>
                  </div>
                )}
                <div>
                  <dt className="text-xs text-mist">Location</dt>
                  <dd className="font-medium text-ink">{location}</dd>
                </div>
                {l.resort && (
                  <div>
                    <dt className="text-xs text-mist">Resort</dt>
                    <dd className="font-medium text-ink">{l.resort}</dd>
                  </div>
                )}
                {l.region && (
                  <div>
                    <dt className="text-xs text-mist">Region</dt>
                    <dd className="font-medium text-ink">{l.region}</dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Timestamps */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-mist">Timeline</h2>
              <dl className="mt-3 space-y-2 text-xs">
                {l.first_seen && (
                  <div className="flex justify-between">
                    <dt className="text-mist">First seen</dt>
                    <dd className="text-ink">{new Date(l.first_seen).toLocaleDateString()}</dd>
                  </div>
                )}
                {l.last_seen && (
                  <div className="flex justify-between">
                    <dt className="text-mist">Last seen</dt>
                    <dd className="text-ink">{new Date(l.last_seen).toLocaleDateString()}</dd>
                  </div>
                )}
                {l.last_changed_at && (
                  <div className="flex justify-between">
                    <dt className="text-mist">Last changed</dt>
                    <dd className="text-ink">{new Date(l.last_changed_at).toLocaleDateString()}</dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <Link
                href="/"
                className="inline-flex flex-1 justify-center rounded-full border border-line px-4 py-2.5 text-sm font-semibold text-ink hover:border-sea/40"
              >
                Back
              </Link>
              <button
                type="button"
                className="inline-flex flex-1 justify-center rounded-full bg-sea px-4 py-2.5 text-sm font-semibold text-white hover:bg-sea-bright cursor-not-allowed opacity-70"
                disabled
                title="CRM lead action — needs `/crm` APIs"
              >
                Create lead
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
