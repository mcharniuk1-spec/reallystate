"use client";

import { useState, useCallback, useRef, useEffect, useMemo } from "react";
import type { Listing, ListingIntent, PropertyCategory, SortOption } from "@/lib/types/listing";
import { useListings, type ListingFilters } from "@/lib/hooks/useListings";
import { IntentToggle, CategoryPicker } from "./CategoryPicker";
import { ListingCard } from "./ListingCard";
import { FilterPanel, type AdvancedFilters, DEFAULT_FILTERS } from "./FilterPanel";
import { MapCanvas } from "@/components/map/MapCanvas";

function applyAdvancedFilters(listings: Listing[], af: AdvancedFilters): Listing[] {
  return listings.filter((l) => {
    if (af.priceMin != null && (l.price == null || l.price < af.priceMin)) return false;
    if (af.priceMax != null && (l.price == null || l.price > af.priceMax)) return false;
    if (af.areaMin != null && (l.area_sqm == null || l.area_sqm < af.areaMin)) return false;
    if (af.areaMax != null && (l.area_sqm == null || l.area_sqm > af.areaMax)) return false;
    if (af.roomsMin != null && (l.rooms == null || l.rooms < af.roomsMin)) return false;
    if (af.roomsMax != null && (l.rooms == null || l.rooms > af.roomsMax)) return false;
    if (af.floorMin != null && (l.floor == null || l.floor < af.floorMin)) return false;
    if (af.floorMax != null && (l.floor == null || l.floor > af.floorMax)) return false;
    if (af.yearMin != null && (l.year_built == null || l.year_built < af.yearMin)) return false;
    if (af.yearMax != null && (l.year_built == null || l.year_built > af.yearMax)) return false;
    if (af.constructionTypes.length > 0 && (l.construction_type == null || !af.constructionTypes.includes(l.construction_type))) return false;
    if (af.amenities.length > 0 && !af.amenities.every((a) => l.amenities?.includes(a))) return false;
    return true;
  });
}

function applySorting(listings: Listing[], sort: SortOption): Listing[] {
  const sorted = [...listings];
  switch (sort) {
    case "price_asc":
      return sorted.sort((a, b) => (a.price ?? Infinity) - (b.price ?? Infinity));
    case "price_desc":
      return sorted.sort((a, b) => (b.price ?? 0) - (a.price ?? 0));
    case "area_asc":
      return sorted.sort((a, b) => (a.area_sqm ?? Infinity) - (b.area_sqm ?? Infinity));
    case "area_desc":
      return sorted.sort((a, b) => (b.area_sqm ?? 0) - (a.area_sqm ?? 0));
    case "newest":
    default:
      return sorted.sort((a, b) => {
        const ta = a.last_seen ? new Date(a.last_seen).getTime() : 0;
        const tb = b.last_seen ? new Date(b.last_seen).getTime() : 0;
        return tb - ta;
      });
  }
}

export function ListingFeed() {
  const [intent, setIntent] = useState<ListingIntent | null>(null);
  const [category, setCategory] = useState<PropertyCategory | null>(null);
  const [hoverId, setHoverId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [advFilters, setAdvFilters] = useState<AdvancedFilters>(DEFAULT_FILTERS);
  const [filterOpen, setFilterOpen] = useState(false);
  const [mobileView, setMobileView] = useState<"list" | "map">("list");
  const scrollRef = useRef<HTMLDivElement>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);

  const filters: ListingFilters = {
    intent,
    category,
    search,
    source_name: null,
  };

  const {
    listings: rawListings,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    isApiDown,
  } = useListings(filters);

  const listings = useMemo(() => {
    const filtered = applyAdvancedFilters(rawListings, advFilters);
    return applySorting(filtered, advFilters.sort);
  }, [rawListings, advFilters]);

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
    setMobileView("list");
    setTimeout(() => {
      const el = document.getElementById(`listing-${id}`);
      el?.scrollIntoView({ behavior: "smooth", block: "center" });
      setHoverId(id);
      setTimeout(() => setHoverId(null), 2000);
    }, 100);
  }, []);

  return (
    <div className="flex flex-col h-[calc(100vh-64px-52px)]">
      {/* Filter bar */}
      <div className="shrink-0 border-b border-line bg-panel/95 backdrop-blur-sm px-4 py-3 sm:px-6 z-20 relative">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <IntentToggle value={intent} onChange={setIntent} />

          <div className="relative flex-1 max-w-xs">
            <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 text-mist/40" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search city, district, resort..."
              className="w-full rounded-xl border border-line bg-paper pl-8 pr-3 py-1.5 text-sm text-ink placeholder:text-mist/50 focus:outline-none focus:border-sea/40 focus:ring-1 focus:ring-sea/20"
            />
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <FilterPanel
              filters={advFilters}
              onChange={setAdvFilters}
              open={filterOpen}
              onToggle={() => setFilterOpen(!filterOpen)}
            />

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
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden relative">
        {/* Map (hidden on mobile when list view active) */}
        <div
          className={`lg:flex-1 shrink-0 border-b lg:border-b-0 lg:border-r border-line ${
            mobileView === "map" ? "flex-1" : "h-[280px] lg:h-auto"
          } ${mobileView === "list" ? "hidden lg:block" : ""}`}
        >
          <MapCanvas listings={listings} highlightId={hoverId} onSelect={handleMapSelect} />
        </div>

        {/* Listing scroll (hidden on mobile when map view active) */}
        <div
          ref={scrollRef}
          className={`flex-1 lg:w-[420px] lg:min-w-[380px] lg:max-w-[480px] overflow-y-auto ${
            mobileView === "map" ? "hidden lg:block" : ""
          }`}
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
              <div className="text-center max-w-xs">
                <svg className="mx-auto text-mist/30" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M3 7v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-6l-2-2H5a2 2 0 0 0-2 2z" />
                </svg>
                <p className="mt-3 font-display text-xl text-ink">No matches</p>
                <p className="mt-2 text-sm text-mist">
                  Try broadening your filters or searching a different area.
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

        {/* Mobile FAB: Map/List toggle (above chat bar) */}
        <div className="lg:hidden fixed bottom-[68px] left-1/2 -translate-x-1/2 z-30">
          <button
            type="button"
            onClick={() => setMobileView(mobileView === "list" ? "map" : "list")}
            className="inline-flex items-center gap-2 rounded-full bg-sea px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-sea/30 hover:bg-sea-bright transition-colors"
          >
            {mobileView === "list" ? (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6" />
                  <line x1="8" y1="2" x2="8" y2="18" />
                  <line x1="16" y1="6" x2="16" y2="22" />
                </svg>
                Map
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="8" y1="6" x2="21" y2="6" />
                  <line x1="8" y1="12" x2="21" y2="12" />
                  <line x1="8" y1="18" x2="21" y2="18" />
                  <line x1="3" y1="6" x2="3.01" y2="6" />
                  <line x1="3" y1="12" x2="3.01" y2="12" />
                  <line x1="3" y1="18" x2="3.01" y2="18" />
                </svg>
                List
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
