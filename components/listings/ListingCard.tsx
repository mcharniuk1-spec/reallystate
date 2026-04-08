"use client";

import Link from "next/link";
import type { Listing } from "@/lib/types/listing";

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

function relativeTime(iso: string | null): string {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
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

  return (
    <Link
      href={`/properties/${l.reference_id}`}
      className={`group block rounded-2xl border border-line bg-panel transition-all hover:border-sea/30 hover:shadow-lift ${
        compact ? "p-3" : "p-4"
      }`}
      onMouseEnter={() => onHover?.(l.reference_id)}
      onMouseLeave={() => onHover?.(null)}
    >
      <div className="aspect-[16/10] rounded-xl bg-gradient-to-br from-paper to-line/40 border border-line/50 flex items-center justify-center overflow-hidden">
        <span className="text-[11px] font-medium text-mist/60 uppercase tracking-wider">
          {l.source_name}
        </span>
      </div>

      <div className="mt-3 flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className={`font-display text-ink leading-tight ${compact ? "text-base" : "text-lg"}`}>
            {formatPrice(l.price, l.currency, l.listing_intent)}
          </p>
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

      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-mist">
        {l.property_category && (
          <span className="capitalize">{l.property_category}</span>
        )}
        {l.area_sqm != null && <span>{l.area_sqm} m\u00B2</span>}
        {l.rooms != null && (
          <span>
            {l.rooms} {l.rooms === 1 ? "room" : "rooms"}
          </span>
        )}
      </div>

      {!compact && l.description && (
        <p className="mt-2 text-xs text-mist line-clamp-2 leading-relaxed">{l.description}</p>
      )}

      <div className="mt-2.5 flex items-center justify-between text-[10px] text-mist/70">
        <span className="font-medium">{l.source_name}</span>
        {l.last_seen && <span>{relativeTime(l.last_seen)}</span>}
      </div>
    </Link>
  );
}
