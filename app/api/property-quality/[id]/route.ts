import { NextRequest, NextResponse } from "next/server";

import { getListingSourceLinks } from "@/lib/listing-source-links";
import { readScrapedListings } from "@/lib/server/scraped-listings";
import type { Listing } from "@/lib/types/listing";

type Params = { id: string };
type CheckStatus = "pass" | "warn" | "fail";

export async function GET(_request: NextRequest, context: { params: Promise<Params> }) {
  const params = await context.params;
  const id = decodeURIComponent(params.id);
  const listings = await readScrapedListings();
  const listing = listings.find((item) => item.reference_id === id);

  if (!listing) {
    return NextResponse.json({ error: "property_not_found", reference_id: id }, { status: 404 });
  }

  const sourceLinks = getListingSourceLinks(listing, listings);
  const checks = buildChecks(listing, sourceLinks);

  return NextResponse.json({
    reference_id: listing.reference_id,
    source_name: listing.source_name,
    listing_url: listing.listing_url,
    title: listing.title,
    location: {
      city: listing.city,
      district: listing.district,
      region: listing.region,
      address_text: listing.address_text,
      latitude: listing.latitude,
      longitude: listing.longitude,
    },
    facts: {
      listing_intent: listing.listing_intent,
      property_category: listing.property_category,
      price: listing.price,
      currency: listing.currency,
      area_sqm: listing.area_sqm,
      rooms: listing.rooms,
      floor: listing.floor,
      total_floors: listing.total_floors,
    },
    media: {
      remote_photos: listing.photo_count_remote ?? listing.image_urls.length,
      local_photos: listing.photo_count_local ?? listing.local_image_files?.length ?? 0,
      full_gallery_downloaded: Boolean(listing.full_gallery_downloaded),
      image_report_status: listing.image_report_status ?? "missing",
      image_report_md: listing.image_report_md,
      image_report_json: listing.image_report_json,
    },
    description: {
      scraped_chars: listing.description_chars ?? listing.description?.length ?? 0,
      combined_chars: combinedDescription(listing).length,
      has_image_report_text: Boolean(listing.image_report_md || listing.image_report_json),
    },
    source_links: sourceLinks,
    checks,
    qa_protocol: {
      required_agent_action:
        "Every scraping or enrichment agent must run photo completeness, image-report coverage, description context, and price/size plausibility checks before marking this property complete.",
      llm_photo_review_required: (listing.photo_count_local ?? listing.local_image_files?.length ?? 0) > 0 && listing.image_report_status !== "complete",
      building_match_required: Boolean(listing.address_text || listing.latitude != null || listing.longitude != null),
    },
  });
}

function buildChecks(listing: Listing, sourceLinks: ReturnType<typeof getListingSourceLinks>) {
  const remotePhotos = listing.photo_count_remote ?? listing.image_urls.length;
  const localPhotos = listing.photo_count_local ?? listing.local_image_files?.length ?? 0;
  const descriptionChars = combinedDescription(listing).length;
  const ppsqm = listing.price != null && listing.area_sqm != null && listing.area_sqm > 0 ? listing.price / listing.area_sqm : null;

  return [
    check("price_present", listing.price != null && listing.price > 0 ? "pass" : "fail", "Listing has a positive parsed price."),
    check(
      "area_present",
      listing.property_category === "land" || (listing.area_sqm != null && listing.area_sqm > 0) ? "pass" : "fail",
      "Listing has a positive parsed size unless it is land with source-specific size handling.",
    ),
    check(
      "price_range",
      priceStatus(listing),
      "Price is inside broad Bulgaria marketplace sanity bounds for the listing intent.",
    ),
    check(
      "area_range",
      areaStatus(listing),
      "Area is inside broad residential/commercial sanity bounds.",
    ),
    check(
      "price_per_sqm_range",
      ppsqm == null ? "warn" : ppsqmStatus(listing, ppsqm),
      ppsqm == null ? "Price per square meter cannot be computed." : `Computed price per square meter: ${Math.round(ppsqm)}.`,
    ),
    check(
      "photo_presence",
      remotePhotos > 0 || localPhotos > 0 ? "pass" : "warn",
      `Remote photos: ${remotePhotos}; local photos: ${localPhotos}.`,
    ),
    check(
      "photo_completeness",
      remotePhotos === 0 || localPhotos >= remotePhotos || listing.full_gallery_downloaded ? "pass" : "warn",
      "Local gallery should contain every reachable remote image or carry an explicit partial-gallery status.",
    ),
    check(
      "image_report",
      listing.image_report_status === "complete" ? "pass" : localPhotos > 0 ? "warn" : "fail",
      "Gemma/OpenClaw image description report should cover every local image in order.",
    ),
    check(
      "description_context",
      descriptionChars >= 350 ? "pass" : descriptionChars >= 120 ? "warn" : "fail",
      `Combined scraped + image-report description length: ${descriptionChars} characters.`,
    ),
    check(
      "source_provenance",
      sourceLinks.length > 0 ? "pass" : "fail",
      `${sourceLinks.length} source link(s) available for this property.`,
    ),
    check(
      "building_match_ready",
      listing.address_text || (listing.latitude != null && listing.longitude != null) ? "warn" : "fail",
      "Address-based building-object matching still requires OSM/PostGIS footprint confirmation.",
    ),
  ];
}

function check(name: string, status: CheckStatus, detail: string) {
  return { name, status, detail };
}

function combinedDescription(listing: Listing) {
  return [listing.description, listing.image_report_md, listing.image_report_json].filter(Boolean).join("\n\n");
}

function priceStatus(listing: Listing): CheckStatus {
  if (listing.price == null || listing.price <= 0) return "fail";
  if (listing.listing_intent === "rent" || listing.listing_intent === "short_term_rental") {
    return listing.price >= 50 && listing.price <= 50_000 ? "pass" : "warn";
  }
  return listing.price >= 5_000 && listing.price <= 10_000_000 ? "pass" : "warn";
}

function areaStatus(listing: Listing): CheckStatus {
  if (listing.area_sqm == null || listing.area_sqm <= 0) return listing.property_category === "land" ? "warn" : "fail";
  if (listing.property_category === "land") return listing.area_sqm <= 1_000_000 ? "pass" : "warn";
  if (listing.property_category === "office" || listing.property_category === "shop") {
    return listing.area_sqm >= 5 && listing.area_sqm <= 20_000 ? "pass" : "warn";
  }
  return listing.area_sqm >= 10 && listing.area_sqm <= 2_500 ? "pass" : "warn";
}

function ppsqmStatus(listing: Listing, ppsqm: number): CheckStatus {
  if (listing.listing_intent === "rent" || listing.listing_intent === "short_term_rental") {
    return ppsqm >= 0.5 && ppsqm <= 500 ? "pass" : "warn";
  }
  return ppsqm >= 50 && ppsqm <= 30_000 ? "pass" : "warn";
}
