"use client";

import Link from "next/link";
import type { Listing } from "@/lib/types/listing";
import { PhotoGallery } from "@/components/listings/PhotoCarousel";
import { ListingCard } from "@/components/listings/ListingCard";

function fmt(price: number | null, currency: string | null, intent: string): string {
  if (price == null) return "Price on request";
  const sym = currency === "EUR" ? "\u20AC" : currency === "BGN" ? "BGN " : `${currency ?? ""} `;
  const suffix = intent === "rent" || intent === "short_term_rental" ? "/mo" : "";
  return `${sym}${new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(price)}${suffix}`;
}

function amenityLabel(a: string): string {
  return a.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function FactRow({ label, value }: { label: string; value: string | number | null | undefined }) {
  if (value == null || value === "") return null;
  return (
    <div className="flex items-center justify-between py-2 border-b border-line/50 last:border-0">
      <dt className="text-xs text-mist">{label}</dt>
      <dd className="text-sm font-medium text-ink">{value}</dd>
    </div>
  );
}

export function PropertyDetailClient({
  listing,
  similar,
}: {
  listing: Listing;
  similar: Listing[];
}) {
  const l = listing;
  const location = [l.district, l.city].filter(Boolean).join(", ") || l.region || "Bulgaria";
  const ppsqm =
    l.price != null && l.area_sqm != null && l.area_sqm > 0
      ? Math.round(l.price / l.area_sqm)
      : null;

  return (
    <div className="min-h-screen flex flex-col bg-paper">
      {/* Header */}
      <header className="shrink-0 border-b border-line bg-panel/90 backdrop-blur-md sticky top-0 z-30">
        <div className="flex items-center justify-between gap-4 px-4 py-2.5 sm:px-6 max-w-7xl mx-auto w-full">
          <div className="flex items-center gap-3 min-w-0">
            <Link href="/" className="font-display text-lg tracking-tight text-ink shrink-0">
              BG<span className="text-sea">Estate</span>
            </Link>
            {/* Breadcrumb */}
            <nav className="hidden sm:flex items-center gap-1.5 text-xs text-mist min-w-0" aria-label="Breadcrumb">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6" /></svg>
              {l.region && (
                <>
                  <span className="truncate max-w-[80px]">{l.region}</span>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6" /></svg>
                </>
              )}
              {l.city && (
                <>
                  <span className="truncate max-w-[80px]">{l.city}</span>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6" /></svg>
                </>
              )}
              <span className="truncate max-w-[120px] text-ink font-medium capitalize">
                {l.rooms ? `${l.rooms}-room ` : ""}{l.property_category}
              </span>
            </nav>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={() => navigator.clipboard?.writeText(window.location.href)}
              className="rounded-full border border-line px-3 py-1 text-xs font-medium text-mist hover:border-sea/30 hover:text-ink transition-colors"
              title="Copy link"
            >
              <svg className="inline -mt-0.5 mr-1" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
              </svg>
              Share
            </button>
            <Link
              href="/"
              className="rounded-full border border-line px-3 py-1 text-xs font-semibold text-ink hover:border-sea/30"
            >
              Back
            </Link>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 mx-auto w-full max-w-6xl px-4 py-8 sm:px-6">
        <div className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr]">
          {/* Left column */}
          <div className="space-y-6">
            {/* Photo gallery */}
            <PhotoGallery
              images={l.image_urls}
              alt={`${l.property_category} in ${location}`}
            />

            {/* Description */}
            {l.description && (
              <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
                <h2 className="text-xs font-semibold uppercase tracking-wide text-mist">Description</h2>
                <p className="mt-3 text-sm text-ink leading-relaxed whitespace-pre-line">
                  {l.description}
                </p>
              </div>
            )}

            {/* Source provenance */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-mist">Listed on</h2>
              <div className="mt-3 flex items-center gap-3">
                <span className="inline-flex items-center gap-2 rounded-xl border border-line bg-paper px-3 py-2">
                  <span className="h-2 w-2 rounded-full bg-sea" />
                  <span className="text-sm font-medium text-ink">{l.source_name}</span>
                </span>
                <a
                  href={l.listing_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-sea hover:text-sea-bright font-medium"
                >
                  View original listing ↗
                </a>
              </div>
              <dl className="mt-3 grid grid-cols-2 gap-3 text-xs">
                <div>
                  <dt className="text-mist">External ID</dt>
                  <dd className="font-mono text-ink mt-0.5">{l.external_id}</dd>
                </div>
                {l.owner_group && (
                  <div>
                    <dt className="text-mist">Owner group</dt>
                    <dd className="text-ink mt-0.5">{l.owner_group}</dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Timeline */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-mist">Timeline</h2>
              <div className="mt-3 space-y-3">
                {l.first_seen && (
                  <div className="flex items-center gap-3">
                    <div className="shrink-0 flex flex-col items-center">
                      <span className="h-2.5 w-2.5 rounded-full bg-sea" />
                      {(l.last_changed_at || l.last_seen) && <span className="w-px h-6 bg-line" />}
                    </div>
                    <div>
                      <p className="text-xs font-medium text-ink">First discovered</p>
                      <p className="text-[11px] text-mist">{new Date(l.first_seen).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}</p>
                    </div>
                  </div>
                )}
                {l.last_changed_at && (
                  <div className="flex items-center gap-3">
                    <div className="shrink-0 flex flex-col items-center">
                      <span className="h-2.5 w-2.5 rounded-full bg-sand" />
                      {l.last_seen && <span className="w-px h-6 bg-line" />}
                    </div>
                    <div>
                      <p className="text-xs font-medium text-ink">Last changed</p>
                      <p className="text-[11px] text-mist">{new Date(l.last_changed_at).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}</p>
                    </div>
                  </div>
                )}
                {l.last_seen && (
                  <div className="flex items-center gap-3">
                    <span className="shrink-0 h-2.5 w-2.5 rounded-full bg-mist/30" />
                    <div>
                      <p className="text-xs font-medium text-ink">Last seen active</p>
                      <p className="text-[11px] text-mist">{new Date(l.last_seen).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right column */}
          <div className="space-y-5">
            {/* Price box */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-display text-3xl text-ink tracking-tight">
                    {fmt(l.price, l.currency, l.listing_intent)}
                  </p>
                  {ppsqm != null && (
                    <p className="mt-1 text-sm text-mist">
                      €{new Intl.NumberFormat("en-US").format(ppsqm)}/m²
                    </p>
                  )}
                </div>
                <span
                  className={`shrink-0 rounded-full border px-3 py-1 text-xs font-semibold capitalize ${
                    l.listing_intent === "sale"
                      ? "bg-sea/10 text-sea border-sea/20"
                      : l.listing_intent === "rent"
                        ? "bg-purple-100 text-purple-700 border-purple-200"
                        : "bg-amber-50 text-amber-700 border-amber-200"
                  }`}
                >
                  {l.listing_intent.replace(/_/g, " ")}
                </span>
              </div>

              {/* Price history placeholder */}
              <div className="mt-4 rounded-xl bg-paper border border-line/50 p-3">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-mist mb-2">Price history</p>
                <div className="h-12 flex items-end gap-0.5">
                  {[40, 55, 50, 60, 65, 70, 72, 75, 80, 85, 82, 88].map((h, i) => (
                    <div
                      key={i}
                      className={`flex-1 rounded-t transition-colors ${i === 11 ? "bg-sea" : "bg-sea/20"}`}
                      style={{ height: `${h}%` }}
                    />
                  ))}
                </div>
                <div className="flex justify-between mt-1 text-[9px] text-mist/50">
                  <span>12 months ago</span>
                  <span>Now</span>
                </div>
              </div>
            </div>

            {/* Facts grid */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-mist mb-1">Property details</h2>
              <dl>
                <FactRow label="Type" value={l.property_category ? l.property_category.charAt(0).toUpperCase() + l.property_category.slice(1) : null} />
                <FactRow label="Area" value={l.area_sqm != null ? `${l.area_sqm} m²` : null} />
                <FactRow label="Rooms" value={l.rooms} />
                <FactRow label="Floor" value={l.floor != null && l.total_floors != null ? `${l.floor} of ${l.total_floors}` : l.floor} />
                <FactRow label="Year built" value={l.year_built} />
                <FactRow label="Construction" value={l.construction_type ? l.construction_type.charAt(0).toUpperCase() + l.construction_type.slice(1) : null} />
                <FactRow label="Location" value={location} />
                <FactRow label="Resort" value={l.resort} />
                <FactRow label="Region" value={l.region} />
              </dl>
            </div>

            {/* Amenities */}
            {l.amenities && l.amenities.length > 0 && (
              <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
                <h2 className="text-xs font-semibold uppercase tracking-wide text-mist mb-3">Amenities</h2>
                <div className="flex flex-wrap gap-2">
                  {l.amenities.map((a) => (
                    <span
                      key={a}
                      className="inline-flex items-center rounded-lg border border-sea/20 bg-sea/5 px-2.5 py-1 text-xs font-medium text-sea"
                    >
                      {amenityLabel(a)}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Contact panel */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-lift">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-mist mb-3">Contact</h2>
              <div className="flex items-center gap-3 mb-4">
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-sea to-sea-bright flex items-center justify-center text-white text-sm font-bold">
                  {l.source_name.charAt(0)}
                </div>
                <div>
                  <p className="text-sm font-medium text-ink">Owner representative</p>
                  <p className="text-xs text-mist">via {l.source_name}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-full bg-sea px-4 py-2.5 text-sm font-semibold text-white hover:bg-sea-bright transition-colors cursor-not-allowed opacity-70"
                  disabled
                  title="Requires CRM APIs"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z" />
                  </svg>
                  Call
                </button>
                <button
                  type="button"
                  className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-full border border-line px-4 py-2.5 text-sm font-semibold text-ink hover:border-sea/30 transition-colors cursor-not-allowed opacity-70"
                  disabled
                  title="Requires CRM APIs"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                  Message
                </button>
              </div>
              <p className="mt-2 text-[10px] text-mist/60 text-center">
                Contact functionality will be available when CRM APIs are ready
              </p>
            </div>

            {/* Save + back */}
            <div className="flex gap-3">
              <Link
                href="/"
                className="inline-flex flex-1 justify-center items-center gap-1.5 rounded-full border border-line px-4 py-2.5 text-sm font-semibold text-ink hover:border-sea/40 transition-colors"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="15 18 9 12 15 6" />
                </svg>
                Back
              </Link>
              <button
                type="button"
                className="inline-flex flex-1 justify-center items-center gap-1.5 rounded-full border border-rose-200 bg-rose-50 px-4 py-2.5 text-sm font-semibold text-rose-600 hover:bg-rose-100 transition-colors cursor-not-allowed opacity-70"
                disabled
                title="Requires auth"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                </svg>
                Save
              </button>
            </div>
          </div>
        </div>

        {/* Similar properties */}
        {similar.length > 0 && (
          <section className="mt-12">
            <h2 className="text-lg font-display text-ink mb-4">
              Similar properties in {l.city || l.region || "Bulgaria"}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {similar.map((s) => (
                <ListingCard key={s.reference_id} listing={s} compact />
              ))}
            </div>
          </section>
        )}

        {/* AI chat prompt */}
        <div className="mt-8 rounded-2xl border border-sea/20 bg-sea/5 p-6 text-center">
          <p className="text-sm font-medium text-sea">Ask about this property</p>
          <p className="mt-1 text-xs text-mist">
            AI chat will be available to answer questions about this listing, the neighborhood, and market trends.
          </p>
          <button
            type="button"
            className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-sea px-5 py-2 text-sm font-semibold text-white cursor-not-allowed opacity-70"
            disabled
            title="Requires AI chat backend"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            Chat about this property
          </button>
        </div>
      </main>
    </div>
  );
}
