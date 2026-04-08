"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import type { ListingIntent, PropertyCategory } from "@/lib/types/listing";
import { useListings, type ListingFilters } from "@/lib/hooks/useListings";
import { IntentToggle, CategoryPicker } from "./CategoryPicker";
import { ListingCard } from "./ListingCard";
import { MapCanvas } from "@/components/map/MapCanvas";

export function ListingFeed() {
  const [intent, setIntent] = useState<ListingIntent | null>(null);
  const [category, setCategory] = useState<PropertyCategory | null>(null);
  const [hoverId, setHoverId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);

  const filters: ListingFilters = {
    intent,
    category,
    search,
    source_name: null,
  };

  const {
    listings,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    isApiDown,
  } = useListings(filters);

  useEffect(() => {
    if (!sentinelRef.current || !hasNextPage) return;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { rootMargin: "200px" },
    );
    observer.observe(sentinelRef.current);
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  const handleMapSelect = useCallback((id: string) => {
    const el = document.getElementById(`listing-${id}`);
    el?.scrollIntoView({ behavior: "smooth", block: "center" });
    setHoverId(id);
    setTimeout(() => setHoverId(null), 2000);
  }, []);

  return (
    <div className="flex flex-col h-[calc(100vh-64px)]">
      {/* Filter bar */}
      <div className="shrink-0 border-b border-line bg-panel/95 backdrop-blur-sm px-4 py-3 sm:px-6 z-20">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <IntentToggle value={intent} onChange={setIntent} />

          <div className="relative flex-1 max-w-xs">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search city, district, resort..."
              className="w-full rounded-xl border border-line bg-paper px-3 py-1.5 text-sm text-ink placeholder:text-mist/50 focus:outline-none focus:border-sea/40 focus:ring-1 focus:ring-sea/20"
            />
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {isApiDown && (
              <span className="inline-flex items-center gap-1.5 rounded-full border border-warn/40 bg-warn/10 px-2.5 py-0.5 text-[10px] font-semibold text-warn">
                <span className="h-1.5 w-1.5 rounded-full bg-warn" aria-hidden />
                Demo data
              </span>
            )}
            <span className="text-xs text-mist font-medium">
              {listings.length} {listings.length === 1 ? "result" : "results"}
            </span>
          </div>
        </div>

        <div className="mt-2.5">
          <CategoryPicker selected={category} onChange={setCategory} />
        </div>
      </div>

      {/* Split: map + list */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Map */}
        <div className="h-[280px] lg:h-auto lg:flex-1 shrink-0 border-b lg:border-b-0 lg:border-r border-line">
          <MapCanvas listings={listings} highlightId={hoverId} onSelect={handleMapSelect} />
        </div>

        {/* Listing scroll */}
        <div
          ref={scrollRef}
          className="flex-1 lg:w-[420px] lg:min-w-[380px] lg:max-w-[480px] overflow-y-auto"
        >
          {isLoading ? (
            <div className="flex items-center justify-center h-full p-8">
              <div className="text-center">
                <div className="mx-auto h-8 w-8 rounded-full border-2 border-sea border-t-transparent animate-spin" />
                <p className="mt-3 text-sm text-mist">Loading listings...</p>
              </div>
            </div>
          ) : listings.length === 0 ? (
            <div className="flex items-center justify-center h-full p-8">
              <div className="text-center">
                <p className="font-display text-xl text-ink">No matches</p>
                <p className="mt-2 text-sm text-mist">
                  Try adjusting the category or intent filter.
                </p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-3 p-4">
              {listings.map((l) => (
                <div
                  key={l.reference_id}
                  id={`listing-${l.reference_id}`}
                  className={`transition-all duration-300 rounded-2xl ${
                    hoverId === l.reference_id ? "ring-2 ring-sea/40 ring-offset-1" : ""
                  }`}
                >
                  <ListingCard listing={l} compact onHover={setHoverId} />
                </div>
              ))}

              {/* Infinite scroll sentinel */}
              {hasNextPage && (
                <div ref={sentinelRef} className="flex justify-center py-4">
                  {isFetchingNextPage && (
                    <div className="h-6 w-6 rounded-full border-2 border-sea border-t-transparent animate-spin" />
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
