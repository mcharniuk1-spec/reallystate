import type { Listing, ListingSourceLink } from "@/lib/types/listing";

export function getListingSourceLinks(listing: Listing, pool: Listing[]): ListingSourceLink[] {
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

export function toSourceLink(base: Listing, candidate: Listing): ListingSourceLink {
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

export function isSameMarketedProperty(base: Listing, candidate: Listing): boolean {
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

export function sourceMatchEvidence(base: Listing, candidate: Listing): string[] {
  if (candidate.reference_id === base.reference_id) return ["current source"];
  const evidence: string[] = [];
  if (sameText(base.city, candidate.city)) evidence.push("same city");
  if (sameText(base.district, candidate.district)) evidence.push("same district");
  if (sameText(base.address_text, candidate.address_text)) evidence.push("same address text");
  if (closeNumber(base.area_sqm, candidate.area_sqm, 0.04, 4)) evidence.push("similar area");
  if (closeNumber(base.price, candidate.price, 0.06, 7000)) evidence.push("similar price");
  if (base.rooms != null && candidate.rooms != null && Math.abs(base.rooms - candidate.rooms) <= 0.25) evidence.push("same rooms");
  if (titleOverlap(base.title, candidate.title) >= 0.45) evidence.push("similar title");
  return evidence.slice(0, 5);
}

export function closeNumber(a: number | null, b: number | null, percent: number, absolute: number): boolean {
  if (a == null || b == null || a <= 0 || b <= 0) return false;
  return Math.abs(a - b) <= Math.max(Math.max(a, b) * percent, absolute);
}

export function sameText(a: string | null | undefined, b: string | null | undefined): boolean {
  const left = normalizeText(a);
  const right = normalizeText(b);
  return left.length > 0 && left === right;
}

export function normalizeText(value: string | null | undefined): string {
  return String(value ?? "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim();
}

export function titleOverlap(a: string | null | undefined, b: string | null | undefined): number {
  const left = new Set(normalizeText(a).split(" ").filter((token) => token.length > 3));
  const right = new Set(normalizeText(b).split(" ").filter((token) => token.length > 3));
  if (!left.size || !right.size) return 0;
  let shared = 0;
  for (const token of left) {
    if (right.has(token)) shared += 1;
  }
  return shared / Math.min(left.size, right.size);
}
