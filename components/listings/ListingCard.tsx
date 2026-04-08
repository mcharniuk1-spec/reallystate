"use client";

import Link from "next/link";
import type { Listing } from "@/lib/types/listing";
import { PhotoCarousel } from "./PhotoCarousel";

function intentLabel(intent: string): string {
  const map: Record<string, string> = {
    sale: "For sale",
    rent: "For rent",
    short_term_rental: "Short-term",
    auction: "Auction",
  };
  return map[intent] ?? intent;
}

function intentStyle(intent: string): string {
  const map: Record<string, string> = {
    sale: "bg-sea/10 text-sea border-sea/20",
    rent: "bg-purple-100 text-purple-700 border-purple-200",
    short_term_rental: "bg-amber-50 text-amber-700 border-amber-200",
    auction: "bg-red-50 text-red-700 border-red-200",
  };
  return map[intent] ?? "bg-mist/10 text-mist border-line";
}

function formatPrice(price: number | null, currency: string | null, intent: string): string {
  if (price == null) return "Price on request";
  const fmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
  const sym = currency === "EUR" ? "\u20AC" : currency === "BGN" ? "BGN " : `${currency ?? ""} `;
  const suffix = intent === "rent" || intent === "short_term_rental" ? "/mo" : "";
  return `${sym}${fmt.format(price)}${suffix}`;
}

function pricePerSqm(price: number | null, area: number | null, currency: string | null): string | null {
  if (price == null || area == null || area <= 0) return null;
  const perSqm = Math.round(price / area);
  const sym = currency === "EUR" ? "\u20AC" : currency === "BGN" ? "BGN " : "";
  return `${sym}${new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(perSqm)}/m\u00B2`;
}

function relativeTime(iso: string | null): string {
  if (!iso) return "";
  const diff = Math.max(0, Date.now() - new Date(iso).getTime());
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function amenityIcon(amenity: string): string {
  const icons: Record<string, string> = {
    parking: "\u{1F17F}\uFE0F",
    balcony: "\u{1F3D7}",
    elevator: "\u{1F6D7}",
    furnished: "\u{1FA91}",
    sea_view: "\u{1F30A}",
    mountain_view: "\u{26F0}\uFE0F",
    pool: "\u{1F3CA}",
    garden: "\u{1F333}",
    garage: "\u{1F697}",
    ac: "\u{2744}\uFE0F",
    central_heating: "\u{1F525}",
  };
  return icons[amenity] ?? "";
}

export function ListingCard({
  listing,
  compact = false,
  onHover,
}: {
  listing: Listing;
  compact?: boolean;
  onHover?: (id: string | null) => void;
}) {
  const l = listing;
  const ppsqm = pricePerSqm(l.price, l.area_sqm, l.currency);

  return (
    <Link
      href={`/properties/${l.reference_id}`}
      className={`group block rounded-2xl border border-line bg-panel transition-all hover:border-sea/30 hover:shadow-lift ${
        compact ? "p-3" : "p-4"
      }`}
      onMouseEnter={() => onHover?.(l.reference_id)}
      onMouseLeave={() => onHover?.(null)}
    >
      <PhotoCarousel
        images={l.image_urls}
        alt={`${l.property_category} in ${l.city || "Bulgaria"}`}
        sourceName={l.source_name}
      />

      <div className="mt-3 flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className={`font-display text-ink leading-tight ${compact ? "text-base" : "text-lg"}`}>
            {formatPrice(l.price, l.currency, l.listing_intent)}
          </p>
          {ppsqm && (
            <p className="text-[11px] text-mist">{ppsqm}</p>
          )}
          <p className="mt-0.5 text-xs text-mist truncate">
            {[l.district, l.city].filter(Boolean).join(", ") || l.region || "Bulgaria"}
          </p>
        </div>
        <span
          className={`shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${intentStyle(
            l.listing_intent,
          )}`}
        >
          {intentLabel(l.listing_intent)}
        </span>
      </div>

      {/* Facts row */}
      <div className="mt-2 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-xs text-mist">
        {l.property_category && (
          <span className="capitalize font-medium">{l.property_category}</span>
        )}
        {l.property_category && (l.area_sqm != null || l.rooms != null) && (
          <span className="text-line">·</span>
        )}
        {l.area_sqm != null && <span>{l.area_sqm} m²</span>}
        {l.rooms != null && (
          <span>
            {l.rooms} {l.rooms === 1 ? "room" : "rooms"}
          </span>
        )}
        {l.floor != null && l.total_floors != null && (
          <>
            <span className="text-line">·</span>
            <span>Floor {l.floor}/{l.total_floors}</span>
          </>
        )}
        {l.year_built != null && (
          <>
            <span className="text-line">·</span>
            <span>{l.year_built}</span>
          </>
        )}
      </div>

      {/* Amenity chips (show up to 4) */}
      {!compact && l.amenities && l.amenities.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {l.amenities.slice(0, 4).map((a) => (
            <span
              key={a}
              className="inline-flex items-center gap-0.5 rounded-md bg-paper border border-line/60 px-1.5 py-0.5 text-[10px] text-mist"
            >
              <span className="text-[9px]">{amenityIcon(a)}</span>
              <span className="capitalize">{a.replace(/_/g, " ")}</span>
            </span>
          ))}
          {l.amenities.length > 4 && (
            <span className="inline-flex items-center rounded-md bg-paper border border-line/60 px-1.5 py-0.5 text-[10px] text-mist">
              +{l.amenities.length - 4}
            </span>
          )}
        </div>
      )}

      {!compact && l.description && (
        <p className="mt-2 text-xs text-mist line-clamp-2 leading-relaxed">{l.description}</p>
      )}

      {/* Footer: source + freshness */}
      <div className="mt-2.5 flex items-center justify-between text-[10px] text-mist/70">
        <span className="inline-flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-sea/40" />
          <span className="font-medium">{l.source_name}</span>
        </span>
        {l.last_seen && <span>{relativeTime(l.last_seen)}</span>}
      </div>
    </Link>
  );
}
