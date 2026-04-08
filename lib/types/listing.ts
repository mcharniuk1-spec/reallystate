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

export type ConstructionType = "brick" | "panel" | "epk" | "monolith" | "wood" | "other";

export type Amenity =
  | "parking"
  | "balcony"
  | "elevator"
  | "furnished"
  | "sea_view"
  | "mountain_view"
  | "pool"
  | "garden"
  | "garage"
  | "ac"
  | "central_heating";

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
  floor: number | null;
  total_floors: number | null;
  year_built: number | null;
  construction_type: ConstructionType | null;
  amenities: Amenity[];
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

export const AMENITIES: { value: Amenity; label: string }[] = [
  { value: "parking", label: "Parking" },
  { value: "balcony", label: "Balcony" },
  { value: "elevator", label: "Elevator" },
  { value: "furnished", label: "Furnished" },
  { value: "sea_view", label: "Sea view" },
  { value: "mountain_view", label: "Mountain view" },
  { value: "pool", label: "Pool" },
  { value: "garden", label: "Garden" },
  { value: "garage", label: "Garage" },
  { value: "ac", label: "A/C" },
  { value: "central_heating", label: "Central heating" },
];

export const CONSTRUCTION_TYPES: { value: ConstructionType; label: string }[] = [
  { value: "brick", label: "Brick" },
  { value: "panel", label: "Panel" },
  { value: "epk", label: "EPK" },
  { value: "monolith", label: "Monolith" },
  { value: "wood", label: "Wood" },
];

export const SORT_OPTIONS = [
  { value: "newest", label: "Newest first" },
  { value: "price_asc", label: "Price: low to high" },
  { value: "price_desc", label: "Price: high to low" },
  { value: "area_asc", label: "Area: small to large" },
  { value: "area_desc", label: "Area: large to small" },
] as const;

export type SortOption = (typeof SORT_OPTIONS)[number]["value"];
