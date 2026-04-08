export type ListingIntent = "sale" | "rent" | "short_term_rental" | "auction";

export type PropertyCategory =
  | "apartment"
  | "house"
  | "studio"
  | "villa"
  | "office"
  | "shop"
  | "land"
  | "garage"
  | "penthouse"
  | "other";

export type Listing = {
  reference_id: string;
  source_name: string;
  owner_group: string | null;
  listing_url: string;
  external_id: string;
  listing_intent: ListingIntent;
  property_category: PropertyCategory;
  city: string | null;
  district: string | null;
  resort: string | null;
  region: string | null;
  address_text: string | null;
  latitude: number | null;
  longitude: number | null;
  area_sqm: number | null;
  rooms: number | null;
  price: number | null;
  currency: string | null;
  description: string | null;
  image_urls: string[];
  first_seen: string | null;
  last_seen: string | null;
  last_changed_at: string | null;
  removed_at: string | null;
  parser_version: string | null;
  crawl_provenance: Record<string, unknown>;
};

export type ListingsPayload = {
  count: number;
  items: Listing[];
};

export const CATEGORIES: { value: PropertyCategory; label: string }[] = [
  { value: "apartment", label: "Apartment" },
  { value: "house", label: "House" },
  { value: "studio", label: "Studio" },
  { value: "villa", label: "Villa" },
  { value: "penthouse", label: "Penthouse" },
  { value: "office", label: "Office" },
  { value: "shop", label: "Shop" },
  { value: "land", label: "Land" },
  { value: "garage", label: "Garage" },
];

export const INTENTS: { value: ListingIntent; label: string }[] = [
  { value: "sale", label: "Buy" },
  { value: "rent", label: "Rent" },
  { value: "short_term_rental", label: "Short-term" },
  { value: "auction", label: "Auction" },
];
