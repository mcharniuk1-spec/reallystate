"use client";

import { useInfiniteQuery } from "@tanstack/react-query";
import type { Listing, ListingsPayload, ListingIntent, PropertyCategory } from "@/lib/types/listing";
import { MOCK_LISTINGS } from "@/lib/mock/listings";
import { SCRAPED_LISTINGS } from "@/lib/mock/scraped-listings";

const PAGE_SIZE = 50;

export type ListingFilters = {
  intent: ListingIntent | null;
  category: PropertyCategory | null;
  search: string;
  source_name: string | null;
};

async function fetchPage(
  filters: ListingFilters,
  offset: number,
): Promise<{ items: Listing[]; nextOffset: number | null }> {
  const params = new URLSearchParams();
  params.set("limit", String(PAGE_SIZE));
  params.set("offset", String(offset));
  if (filters.source_name) params.set("source_name", filters.source_name);

  const res = await fetch(`/api/backend/listings?${params.toString()}`, {
    cache: "no-store",
  });

  if (!res.ok) throw new Error(`API ${res.status}`);

  const data = (await res.json()) as ListingsPayload;

  let items = data.items;

  if (filters.intent) {
    items = items.filter((l) => l.listing_intent === filters.intent);
  }
  if (filters.category) {
    items = items.filter((l) => l.property_category === filters.category);
  }
  if (filters.search.trim()) {
    const q = filters.search.toLowerCase();
    items = items.filter(
      (l) =>
        l.city?.toLowerCase().includes(q) ||
        l.district?.toLowerCase().includes(q) ||
        l.resort?.toLowerCase().includes(q) ||
        l.description?.toLowerCase().includes(q) ||
        l.source_name.toLowerCase().includes(q),
    );
  }

  const hasMore = data.items.length === PAGE_SIZE;
  return { items, nextOffset: hasMore ? offset + PAGE_SIZE : null };
}

function applyClientFilters(all: Listing[], filters: ListingFilters): Listing[] {
  let out = all;
  if (filters.intent) out = out.filter((l) => l.listing_intent === filters.intent);
  if (filters.category) out = out.filter((l) => l.property_category === filters.category);
  if (filters.search.trim()) {
    const q = filters.search.toLowerCase();
    out = out.filter(
      (l) =>
        l.city?.toLowerCase().includes(q) ||
        l.district?.toLowerCase().includes(q) ||
        l.resort?.toLowerCase().includes(q) ||
        l.description?.toLowerCase().includes(q) ||
        l.source_name.toLowerCase().includes(q),
    );
  }
  if (filters.source_name) out = out.filter((l) => l.source_name === filters.source_name);
  return out;
}

export function useListings(filters: ListingFilters) {
  const query = useInfiniteQuery({
    queryKey: ["listings", filters.source_name],
    queryFn: ({ pageParam = 0 }) => fetchPage(filters, pageParam as number),
    getNextPageParam: (last) => last.nextOffset,
    initialPageParam: 0,
    staleTime: 30_000,
    retry: 1,
  });

  const isApiDown = query.isError;

  if (isApiDown) {
    const fallbackListings = SCRAPED_LISTINGS.length > 0 ? SCRAPED_LISTINGS : MOCK_LISTINGS;
    const mockFiltered = applyClientFilters(fallbackListings, filters);
    return {
      listings: mockFiltered,
      isLoading: false,
      isFetchingNextPage: false,
      hasNextPage: false,
      fetchNextPage: () => {},
      isApiDown: true,
      error: query.error,
    };
  }

  const allItems = (query.data?.pages ?? []).flatMap((p) => p.items);
  const filtered = applyClientFilters(allItems, filters);

  return {
    listings: filtered,
    isLoading: query.isLoading,
    isFetchingNextPage: query.isFetchingNextPage,
    hasNextPage: query.hasNextPage ?? false,
    fetchNextPage: query.fetchNextPage,
    isApiDown: false,
    error: null,
  };
}
